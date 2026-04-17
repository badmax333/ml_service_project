Сервис для транскрибации аудио с использованием Whisper.

## Быстрый старт

\`\`\`bash
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend pip install openai-whisper numba tiktoken ffmpeg-python
docker-compose restart backend
\`\`\`

## API Docs
http://localhost:8000/docs