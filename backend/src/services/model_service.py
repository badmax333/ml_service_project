import os
import pickle
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from src.models.model_registry import ModelRegistry
from src.config import settings

# Создаем папку для моделей, если её нет
Path(settings.MODEL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

def save_model_file(file: UploadFile, user_id: int) -> str:
    """Сохраняет загруженный .pkl файл и возвращает путь"""
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension != '.pkl':
        raise HTTPException(400, "Only .pkl files are allowed")
    
    unique_filename = f"user_{user_id}_{uuid.uuid4().hex}{file_extension}"
    file_path = Path(settings.MODEL_STORAGE_PATH) / unique_filename
    
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    
    return str(file_path)

def create_model(db: Session, user_id: int, name: str, file_path: str, price: int):
    """Создает запись о модели в БД"""
    model = ModelRegistry(
        user_id=user_id,
        name=name,
        file_path=file_path,
        price_per_prediction=price
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

def get_user_models(db: Session, user_id: int):
    """Возвращает все модели пользователя"""
    return db.query(ModelRegistry).filter(
        ModelRegistry.user_id == user_id,
        ModelRegistry.is_active == True
    ).all()

def get_model(db: Session, model_id: int, user_id: int):
    """Возвращает модель по ID, проверяя принадлежность пользователю"""
    model = db.query(ModelRegistry).filter(
        ModelRegistry.id == model_id,
        ModelRegistry.user_id == user_id
    ).first()
    
    if not model:
        raise HTTPException(404, "Model not found")
    return model