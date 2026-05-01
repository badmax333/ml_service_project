from src.api.v1.transcription import router as transcription_router

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.v1 import auth_router, models_router
from src.api.v1.transcription import router as transcription_router
from src.api.v1.users import router as users_router
from src.api.v1.billing import router as billing_router

from src.core.metrics import REQUESTS, REQUESTS_LATENCY, ACTIVE_REQUESTS, USERS_TOTAL, TRANSCRIPTIONS_TOTAL, CREDITS_SPENT

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        REQUESTS.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUESTS_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        ACTIVE_REQUESTS.dec()
        return response

app = FastAPI(
    title="ML Prediction Service",
    description="Сервис для транскрибации аудио с помощью Whisper",
    version="1.0.0"
)

app.add_middleware(MetricsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(models_router)
app.include_router(transcription_router)
app.include_router(users_router)
app.include_router(billing_router)

@app.get("/")
async def root():
    return {"message": "ML Service is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)