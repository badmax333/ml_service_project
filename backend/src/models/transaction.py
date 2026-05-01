from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # положительное = пополнение, отрицательное = списание
    type = Column(String, nullable=False)  # "deposit", "transcription"
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())