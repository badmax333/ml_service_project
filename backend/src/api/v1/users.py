from fastapi import APIRouter, Depends
from src.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.schemas.user import UserResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user