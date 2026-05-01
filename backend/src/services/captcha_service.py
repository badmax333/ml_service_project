import random
import hashlib
import time
from typing import Dict, Tuple

# Хранилище капч (в реальном проекте используйте Redis)
_captcha_store: Dict[str, Tuple[int, float]] = {}

def generate_captcha() -> Tuple[str, str, int]:
    """
    Генерирует математическую капчу
    Returns: (captcha_id, question, expiration_seconds)
    """
    # Генерируем пример
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(['+', '-'])
    
    if operator == '+':
        answer = num1 + num2
        question = f"{num1} + {num2} = ?"
    else:
        # Убеждаемся что результат неотрицательный
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
        question = f"{num1} - {num2} = ?"
    
    # Генерируем уникальный ID
    captcha_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()
    
    # Сохраняем с временем жизни 5 минут
    _captcha_store[captcha_id] = (answer, time.time() + 300)
    
    return captcha_id, question, 300

def verify_captcha(captcha_id: str, user_answer: int) -> bool:
    """
    Проверяет ответ капчи
    """
    if captcha_id not in _captcha_store:
        return False
    
    answer, expires_at = _captcha_store[captcha_id]
    
    # Проверяем срок действия
    if time.time() > expires_at:
        del _captcha_store[captcha_id]
        return False
    
    # Удаляем использованную капчу
    del _captcha_store[captcha_id]
    
    return answer == user_answer

def cleanup_expired_captchas():
    """Очищает просроченные капчи (можно запускать по крону)"""
    current_time = time.time()
    expired = [cid for cid, (_, exp) in _captcha_store.items() if current_time > exp]
    for cid in expired:
        del _captcha_store[cid]