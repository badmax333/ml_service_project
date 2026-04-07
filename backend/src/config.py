from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://mluser:mlpass@localhost:5432/mlservice"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "dev_secret_key_change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_HOURS: int = 24
    ADMIN_SECRET_KEY: str = "admin_key_for_streamlit"
    MODEL_STORAGE_PATH: str = "/app/models_storage"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
