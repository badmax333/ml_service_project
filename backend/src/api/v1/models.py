from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.model import ModelCreate, ModelResponse, ModelUploadResponse
from src.services.model_service import save_model_file, create_model, get_user_models, get_model
from src.core.security import get_current_user
from src.models.user import User

router = APIRouter(prefix="/models", tags=["Models"])

@router.post("/upload", response_model=ModelUploadResponse)
async def upload_model(
    name: str = Form(...),
    price_per_prediction: int = Form(10),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Загружает новую ML модель"""
    file_path = save_model_file(file, current_user.id)
    
    model = create_model(
        db=db,
        user_id=current_user.id,
        name=name,
        file_path=file_path,
        price=price_per_prediction
    )
    
    return ModelUploadResponse(
        model_id=model.id,
        name=model.name,
        message=f"Model '{name}' uploaded successfully"
    )

@router.get("/", response_model=list[ModelResponse])
def list_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает список всех моделей пользователя"""
    return get_user_models(db, current_user.id)

@router.get("/{model_id}", response_model=ModelResponse)
def get_model_info(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает информацию о конкретной модели"""
    return get_model(db, model_id, current_user.id)
