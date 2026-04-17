from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class TranscriptionRequest(BaseModel):
    model_size: str  # tiny, base, small

class TranscriptionResponse(BaseModel):
    job_id: int
    status: str
    message: str

class TranscriptionResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    id: int
    model_size: str
    transcribed_text: Optional[str] = None
    status: str
    credits_cost: int
    duration_seconds: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class AvailableModel(BaseModel):
    size: str
    name: str
    price: int
    description: str