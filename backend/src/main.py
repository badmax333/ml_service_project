from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import auth_router, models_router
from src.api.v1.transcription import router as transcription_router

app = FastAPI(
    title="ML Prediction Service",
    description="Сервис для асинхронных ML предсказаний с биллингом",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(models_router)
app.include_router(transcription_router)

@app.get("/")
async def root():
    return {"message": "ML Service is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
