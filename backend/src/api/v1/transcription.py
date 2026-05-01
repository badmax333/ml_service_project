from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path
from src.database import get_db
from src.schemas.transcription import (
    TranscriptionResponse, TranscriptionResult, AvailableModel
)
from src.services.whisper_service import get_price_for_model, get_available_models
from src.core.security import get_current_user
from src.models.user import User
from src.models.transcription_model import TranscriptionJob
from src.config import settings
from src.tasks.transcription_tasks import process_transcription
from src.core.metrics import TRANSCRIPTIONS_TOTAL, CREDITS_SPENT

router = APIRouter(prefix="/transcribe", tags=["Transcription"])

# Создаем папку для аудиофайлов
AUDIO_STORAGE = Path(settings.MODEL_STORAGE_PATH) / "audio"
AUDIO_STORAGE.mkdir(parents=True, exist_ok=True)

# Допустимые расширения файлов
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".webm", ".flac"}

@router.get("/models", response_model=List[AvailableModel])
def list_models():
    return get_available_models()

@router.post("/{model_size}", response_model=TranscriptionResponse)
async def transcribe_audio(
    model_size: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    available_sizes = ["tiny", "base", "small"]
    if model_size not in available_sizes:
        raise HTTPException(400, f"Model size must be one of {available_sizes}")
    
    # Проверяем расширение файла
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file extension. Allowed: {ALLOWED_EXTENSIONS}")
    
    # Сохраняем аудиофайл
    unique_filename = f"user_{current_user.id}_{uuid.uuid4().hex}{file_extension}"
    file_path = AUDIO_STORAGE / unique_filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    price = get_price_for_model(model_size)
    
    if current_user.balance < price:
        raise HTTPException(402, f"Insufficient balance. Need {price} credits, have {current_user.balance}")
    
    # Создаем задачу в БД
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
    
    # Запускаем Celery задачу
    process_transcription.delay(
        job_id=job.id,
        audio_path=str(file_path),
        model_size=model_size,
        user_id=current_user.id,
        price=price
    )
    
    return TranscriptionResponse(
        job_id=job.id,
        status="pending",
        message=f"Transcription queued. Cost: {price} credits"
    )

@router.get("/jobs", response_model=List[TranscriptionResult])
def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    job = db.query(TranscriptionJob).filter(
        TranscriptionJob.id == job_id,
        TranscriptionJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(404, "Job not found")
    return job