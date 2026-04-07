from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from src.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    telegram_username = Column(String, nullable=True)
    
    balance = Column(Integer, default=100)  # Стартовый бонус 100 кредитов
    role = Column(String, default="user")  # "user" или "admin"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())