# 🎙️ ML Service — Сервис транскрибации аудио на базе Whisper

![Demo](demo.gif)

Полноценный production-ready микросервис для автоматической транскрибации аудиофайлов с использованием модели OpenAI Whisper. Проект реализован как набор Docker-контейнеров с REST API, фоновой обработкой задач, веб-дашбордом и встроенным мониторингом.

---

## 📋 Содержание

- [Финансовая модель](#-финансовая-модель)
- [Обзор архитектуры](#-обзор-архитектуры)
- [Стек технологий](#-стек-технологий)
- [Структура проекта](#-структура-проекта)
- [Как устроена система](#-как-устроена-система)
- [Переменные окружения](#-переменные-окружения)
- [Быстрый старт](#-быстрый-старт)
- [API Reference](#-api-reference)
- [Мониторинг](#-мониторинг)
- [Дашборд](#-дашборд)

---
### УТП

**«Транскрибация аудио в текст за секунды — без подписки, только за фактические операции»**

- 🔐 **Без подписок** — платите только за реально использованные транскрибации
- 🎯 **Три уровня точности** — выбирайте между скоростью и качеством (tiny / base / small)

## Финансовая модель

#### 💰 Монетизация

| Модель | Цена | Описание |
|--------|------|----------|
| **Whisper Tiny** | 5 кредитов | Быстрая, для черновиков и коротких аудио |
| **Whisper Base** | 15 кредитов | Оптимальный баланс скорости и точности |
| **Whisper Small** | 30 кредитов | Максимальная точность для важных записей |

**100 бонусных кредитов** — начисляются при регистрации (для знакомства с сервисом).

---

#### 📈 Экономика юнита

| Показатель | Значение |
|------------|----------|
| Средняя стоимость транскрибации | ~15 кредитов |
| Время обработки (base) | 10–30 сек на 1 мин аудио |
| Инфраструктурные затраты | минимальные (Docker + PostgreSQL) |
| **Маржинальность** | высокая (Whisper работает локально, без API-ключей


## 🏗️ Обзор архитектуры

Проект построен по принципу **разделения ответственности**: HTTP-запросы принимаются FastAPI-сервером и сразу же делегируются в очередь задач Celery, которая выполняет тяжёлую ML-работу (инференс Whisper) асинхронно. Результаты хранятся в PostgreSQL, состояние задач — в Redis.

```
Клиент
  │
  ▼
FastAPI (backend :8000)
  │── JWT-аутентификация
  │── Валидация запросов
  │── REST API + Swagger UI
  │
  ├──► Redis (брокер задач :6379)
  │         │
  │         ▼
  │    Celery Worker
  │         │── Whisper инференс
  │         │── Обновление статуса задачи
  │         └──► PostgreSQL (результаты)
  │
  ├──► PostgreSQL (хранение данных :5432)
  │
  └──► Prometheus (метрики :9090)
            │
            ▼
         Grafana (дашборд :3000)

Streamlit Dashboard (:8501) ──► backend API
```

---

## 🛠️ Стек технологий

| Компонент | Технология | Назначение |
|-----------|-----------|------------|
| **ML-модель** | OpenAI Whisper | Транскрибация аудио |
| **Backend API** | FastAPI + Uvicorn | REST API, валидация, Swagger |
| **Очередь задач** | Celery | Асинхронная обработка аудио |
| **Брокер / кэш** | Redis 7 | Брокер для Celery, хранение статусов |
| **База данных** | PostgreSQL 15 | Хранение транскрипций и пользователей |
| **Миграции** | Alembic | Управление схемой БД |
| **Дашборд** | Streamlit | Веб-интерфейс для пользователей |
| **Метрики** | Prometheus | Сбор метрик с backend |
| **Визуализация** | Grafana | Графики и алерты |
| **Контейнеризация** | Docker + Docker Compose | Оркестрация всех сервисов |
| **Аутентификация** | JWT (HS256) | Авторизация пользователей |

---

## 📁 Структура проекта

```
ml_service_project/
├── backend/                    # FastAPI-приложение + Celery-воркер
│   ├── src/
│   │   ├── main.py             # Точка входа FastAPI
│   │   ├── core/
│   │   │   ├── celery_app.py   # Конфигурация Celery
│   │   │   └── config.py       # Настройки приложения
│   │   ├── api/                # Роутеры (endpoints)
│   │   └── models/             # SQLAlchemy-модели
│   └── tests/                  # Тесты (на одном уровне с src)
│
├── dashboard/                  # Streamlit-приложение
│
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml      # Конфиг сбора метрик
│   └── grafana/
│       ├── provisioning/       # Автопровизионирование источников данных
│       └── dashboards/         # Готовые дашборды Grafana
│
├── docker-compose.yml          # Описание всех сервисов
├── .env.example                # Пример переменных окружения
├── Makefile                    # Утилиты для разработки
└── demo.gif                    # Демонстрация работы сервиса
```

---

## ⚙️ Как устроена система

### 1. Приём запроса и аутентификация

Каждый запрос к API проходит через JWT-middleware. Токен генерируется при логине и передаётся в заголовке `Authorization: Bearer <token>`. Алгоритм подписи — HS256, время жизни токена настраивается через `JWT_EXPIRES_HOURS`.

### 2. Асинхронная обработка аудио

Транскрибация — дорогостоящая операция (несколько секунд или минут в зависимости от длины аудио). Чтобы не блокировать HTTP-соединение, FastAPI помещает задачу в Redis-очередь и сразу возвращает клиенту `task_id`. Celery-воркер забирает задачу и запускает Whisper-инференс в фоне.

Клиент может опрашивать эндпоинт статуса (`GET /transcribe/{task_id}`) пока задача не перейдёт в состояние `SUCCESS` или `FAILURE`.

### 3. ML-модель (Whisper)

Whisper устанавливается автоматически при сборке Docker-образа backend. Поддерживаются несколько размеров моделей (tiny, base, small, medium, large) — доступные варианты можно получить через `GET /transcribe/models`. Модели кэшируются внутри контейнера, повторная загрузка при рестарте не происходит.

### 4. Хранение данных

PostgreSQL используется для хранения пользователей и результатов транскрибаций. Схема управляется через **Alembic** — миграции применяются вручную командой `alembic upgrade head` (или через `docker-compose exec backend alembic upgrade head`).

### 5. Мониторинг

Backend экспортирует метрики в формате Prometheus (количество задач, время обработки, ошибки). Prometheus собирает их по расписанию, Grafana визуализирует в виде графиков. Все настройки Grafana (источники данных, дашборды) провизионируются автоматически при старте контейнера из директории `monitoring/grafana/provisioning/`.

---

## 🔐 Переменные окружения

Все переменные задаются в файле `.env` (скопируйте из `.env.example`):

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql://mluser:mlpass@postgres:5432/mlservice` |
| `REDIS_URL` | Строка подключения к Redis | `redis://redis:6379/0` |
| `JWT_SECRET` | Секрет для подписи JWT-токенов | `your_super_secret_key` |
| `JWT_ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `JWT_EXPIRES_HOURS` | Время жизни токена (часы) | `24` |
| `WEBHOOK_SECRET` | Секрет для вебхуков (опционально) | — |
| `ADMIN_SECRET_KEY` | Ключ администратора для Streamlit | `admin_key_for_streamlit` |

> ⚠️ **Важно**: перед деплоем в production обязательно смените `JWT_SECRET` и `ADMIN_SECRET_KEY` на случайно сгенерированные строки.

---

## 🚀 Быстрый старт

### Предварительные требования

- Docker >= 24
- Docker Compose >= 2.x
- ~5–10 ГБ свободного места (для образов и весов модели)

### Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/badmax333/ml_service_project.git
cd ml_service_project

# 2. Создать файл с переменными окружения
cp .env.example .env

# 3. Запустить все контейнеры
docker-compose up -d

# 4. Следить за сборкой backend (скачивается torch — займёт 5–10 минут)
docker-compose logs -f backend

# 5. Применить миграции базы данных
docker-compose exec backend alembic upgrade head

# 6. Проверить, что сервис работает
curl http://localhost:8000/health

# 7. Посмотреть список доступных моделей Whisper
curl http://localhost:8000/transcribe/models
```

### Адреса сервисов после запуска

| Сервис | URL |
|--------|-----|
| REST API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Streamlit Dashboard | http://localhost:8501 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin / admin) |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### Остановка

```bash
docker-compose down          # остановить контейнеры
docker-compose down -v       # остановить и удалить volumes (данные)
```

---

## 📡 API Reference

Полная интерактивная документация доступна на **http://localhost:8000/docs** (Swagger UI).

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Проверка состояния сервиса |
| `POST` | `/auth/register` | Регистрация пользователя |
| `POST` | `/auth/login` | Получение JWT-токена |
| `POST` | `/transcribe/` | Отправить аудиофайл на транскрибацию |
| `GET` | `/transcribe/{task_id}` | Получить статус и результат задачи |
| `GET` | `/transcribe/models` | Список доступных моделей Whisper |

### Пример: отправка аудио на транскрибацию

```bash
# Получить токен
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}' | jq -r '.access_token')

# Загрузить файл
TASK_ID=$(curl -s -X POST http://localhost:8000/transcribe/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@audio.mp3" | jq -r '.task_id')

# Опросить статус
curl http://localhost:8000/transcribe/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Мониторинг

### Prometheus

Метрики backend доступны на http://localhost:9090. Prometheus автоматически скрейпит эндпоинт `/metrics` FastAPI-приложения согласно конфигурации в `monitoring/prometheus/prometheus.yml`.

### Grafana

Дашборды Grafana доступны на http://localhost:3000 (логин: `admin`, пароль: `admin`).

Готовые дашборды из директории `monitoring/grafana/dashboards/` провизионируются автоматически при первом запуске и включают:
- количество обработанных задач в единицу времени
- среднее время транскрибации
- количество ошибок
- загрузка воркеров Celery

---

## 🖥️ Дашборд

Streamlit-приложение на http://localhost:8501 предоставляет удобный веб-интерфейс для загрузки аудиофайлов и просмотра результатов транскрибации без необходимости работать напрямую с API.

Для доступа к административным функциям дашборда используется `ADMIN_SECRET_KEY` из `.env`.

---

## 🐳 Docker Compose — сервисы

| Сервис | Образ | Порт | Зависит от |
|--------|-------|------|-----------|
| `postgres` | postgres:15-alpine | 5432 | — |
| `redis` | redis:7-alpine | 6379 | — |
| `backend` | ./backend (custom) | 8000 | postgres, redis |
| `celery_worker` | ./backend (custom) | — | postgres, redis |
| `dashboard` | ./dashboard (custom) | 8501 | backend |
| `prometheus` | prom/prometheus:latest | 9090 | backend |
| `grafana` | grafana/grafana:latest | 3000 | prometheus |

Сервисы `backend` и `celery_worker` собираются из одного Dockerfile, но запускаются с разными командами:
- backend: `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`
- celery_worker: `celery -A src.core.celery_app worker --loglevel=info`

Healthcheck настроен для `postgres` и `redis`, поэтому backend и воркер гарантированно стартуют только после полной готовности зависимостей.

## 📊 Покрытие кода

[![coverage](https://img.shields.io/badge/coverage-73.6%25-brightgreen)](reports/coverage_html/index.html)