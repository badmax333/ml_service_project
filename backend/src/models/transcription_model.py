from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from src.database import Base

class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_size = Column(String, nullable=False)  # "tiny", "base", "small"
    audio_file_path = Column(String, nullable=False)
    transcribed_text = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(String, nullable=True)
    credits_cost = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=True)  # длительность аудио
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class PricingConfig(Base):
    __tablename__ = "pricing_config"
    
    id = Column(Integer, primary_key=True)
    model_size = Column(String, unique=True, nullable=False)  # tiny, base, small
    price_per_job = Column(Integer, nullable=False)
    is_active = Column(Integer, default=1)