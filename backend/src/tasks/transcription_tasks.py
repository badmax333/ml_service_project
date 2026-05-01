from celery import Task
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.user import User
from src.models.transcription_model import TranscriptionJob
from src.services.whisper_service import transcribe_audio_file
from datetime import datetime

class TranscriptionTask(Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

from src.core.celery_app import celery_app

@celery_app.task(base=TranscriptionTask, bind=True)
def process_transcription(self, job_id: int, audio_path: str, model_size: str, user_id: int, price: int):
    """
    Асинхронная транскрибация аудио
    """
    db = self.db
    
    try:
        # Обновляем статус
        db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).update({
            "status": "processing"
        })
        db.commit()
        
        # Выполняем транскрибацию
        result = transcribe_audio_file(audio_path, model_size)
        
        # Обновляем запись
        db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).update({
            "status": "completed",
            "transcribed_text": result["text"],
            "duration_seconds": result["duration"],
            "completed_at": datetime.utcnow()
        })
        
        # Списываем кредиты
        db.query(User).filter(User.id == user_id).update({
            "balance": User.balance - price
        })
        
        db.commit()
        
        # 📊 МЕТРИКИ — добавляем после успешного коммита
        from src.core.metrics import TRANSCRIPTIONS_TOTAL, CREDITS_SPENT
        TRANSCRIPTIONS_TOTAL.labels(model_size=model_size, status="completed").inc()
        CREDITS_SPENT.inc(price)
        
        return {
            "job_id": job_id,
            "text": result["text"],
            "duration": result["duration"]
        }
        
    except Exception as e:
        # 📊 МЕТРИКА ОШИБКИ
        from src.core.metrics import TRANSCRIPTIONS_TOTAL
        TRANSCRIPTIONS_TOTAL.labels(model_size=model_size, status="failed").inc()
        
        db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).update({
            "status": "failed",
            "error_message": str(e)
        })
        db.commit()
        raise self.retry(exc=e, countdown=60, max_retries=3)