from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from src.database import Base

class ModelRegistry(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    price_per_prediction = Column(Integer, default=10)
    input_schema = Column(String, nullable=True)  # JSON схема (опционально)
    is_active = Column(Boolean, default=True)
    predictions_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())