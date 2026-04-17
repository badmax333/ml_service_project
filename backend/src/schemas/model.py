from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelCreate(BaseModel):
    name: str
    price_per_prediction: Optional[int] = 10

class ModelResponse(BaseModel):
    id: int
    name: str
    price_per_prediction: int
    is_active: bool
    predictions_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModelUploadResponse(BaseModel):
    model_id: int
    name: str
    message: str