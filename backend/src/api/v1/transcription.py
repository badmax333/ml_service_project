from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import datetime
from pathlib import Path
from src.database import get_db
from src.schemas.transcription import (
    TranscriptionRequest, TranscriptionResponse, 
    TranscriptionResult, AvailableModel
)
from src.services.whisper_service import transcribe_audio_file, get_price_for_model, get_available_models
from src.core.security import get_current_user
from src.models.user import User
from src.models.transcription_model import TranscriptionJob
from src.config import settings

router = APIRouter(prefix="/transcribe", tags=["Transcription"])


AUDIO_STORAGE = Path(settings.MODEL_STORAGE_PATH) / "audio"
AUDIO_STORAGE.mkdir(parents=True, exist_ok=True)

@router.get("/models", response_model=List[AvailableModel])
def list_models():
    """Возвращает список доступных моделей с ценами"""
    return get_available_models()

@router.post("/{model_size}", response_model=TranscriptionResponse)
async def transcribe_audio(
    model_size: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправляет аудио на транскрибацию"""
    
    available_sizes = ["tiny", "base", "small"]
    if model_size not in available_sizes:
        raise HTTPException(400, f"Model size must be one of {available_sizes}")
    
    allowed_formats = ["audio/mpeg", "audio/mp3", "audio/ogg", "audio/m4a", "audio/wav"]
    if file.content_type not in allowed_formats:
        raise HTTPException(400, f"Unsupported audio format. Use: {allowed_formats}")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"user_{current_user.id}_{uuid.uuid4().hex}{file_extension}"
    file_path = AUDIO_STORAGE / unique_filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    price = get_price_for_model(model_size)
    
    if current_user.balance < price:
        raise HTTPException(402, f"Insufficient balance. Need {price} credits, have {current_user.balance}")
    
    job = TranscriptionJob(
        user_id=current_user.id,
        model_size=model_size,
        audio_file_path=str(file_path),
        credits_cost=price,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # TODO: Здесь запустим Celery задачу (Спринт 5)
    # Пока делаем синхронно для теста
    
    try:
        job.status = "processing"
        db.commit()
        
        result = transcribe_audio_file(str(file_path), model_size)
        
        job.transcribed_text = result["text"]
        job.status = "completed"
        job.duration_seconds = result["duration"]
        job.completed_at = datetime.utcnow()
        
        # Списываем кредиты
        current_user.balance -= price
        db.commit()
        
        return TranscriptionResponse(
            job_id=job.id,
            status="completed",
            message=f"Transcription completed. Cost: {price} credits"
        )
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        raise HTTPException(500, f"Transcription failed: {str(e)}")

@router.get("/jobs", response_model=List[TranscriptionResult])
def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает историю транскрибаций пользователя"""
    jobs = db.query(TranscriptionJob).filter(
        TranscriptionJob.user_id == current_user.id
    ).order_by(TranscriptionJob.created_at.desc()).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=TranscriptionResult)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает результат конкретной транскрибации"""
    job = db.query(TranscriptionJob).filter(
        TranscriptionJob.id == job_id,
        TranscriptionJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(404, "Job not found")
    return job