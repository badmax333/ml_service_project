from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.models.transaction import Transaction
from src.schemas.captcha import CaptchaResponse, TopUpRequest
from src.services.captcha_service import generate_captcha, verify_captcha
from src.core.metrics import CREDITS_SPENT

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/captcha", response_model=CaptchaResponse)
def get_captcha():
    """Генерирует математическую капчу"""
    captcha_id, question, expires = generate_captcha()
    return CaptchaResponse(
        captcha_id=captcha_id,
        question=question,
        expires_in=expires
    )

@router.post("/topup")
def top_up_balance(
    request: TopUpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Пополнение баланса с проверкой капчи"""
    
    # Проверяем сумму
    if request.amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if request.amount > 10000:
        raise HTTPException(400, "Amount too high (max 10000)")
    
    # Проверяем капчу
    if not verify_captcha(request.captcha_id, request.answer):
        raise HTTPException(400, "Invalid captcha answer or captcha expired")
    
    # Пополняем баланс
    current_user.balance += request.amount
    
    # Записываем транзакцию
    transaction = Transaction(
        user_id=current_user.id,
        amount=request.amount,
        type="deposit",
        description=f"Manual top-up via captcha"
    )
    db.add(transaction)
    db.commit()
    db.refresh(current_user)
    
    # Обновляем метрику (отрицательное списание = пополнение)
    # CREDITS_SPENT.inc(-request.amount)  # опционально
    
    return {
        "status": "success",
        "amount": request.amount,
        "new_balance": current_user.balance,
        "message": f"Balance topped up by {request.amount} credits"
    }