Сервис для транскрибации аудио с использованием Whisper.

## Быстрый старт

# 1. Клонировать репозиторий
git clone https://github.com/badmax333/ml_service_project.git
cd ml_service_project

# 2. Создать .env файл
cp .env.example .env

# 3. Запустить контейнеры (Whisper установится автоматически из Dockerfile)
docker-compose up -d

# 4. Дождаться завершения сборки (5-10 минут, т.к. качается torch)
docker-compose logs -f backend  # Понаблюдать за установкой

# 5. Применить миграции
docker-compose exec backend alembic upgrade head

# 6. Проверить работу
curl http://localhost:8000/health

# 7. Посмотреть список моделей
curl http://localhost:8000/transcribe/models

## API Docs
http://localhost:8000/docs