# Using Pydantic's BaseSettings for better environment variable management

from pydantic import BaseSettings, ConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Boilerplate"
    DEBUG_MODE: bool = True
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "FastAPI Boilerplate"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://fastapi_user:your_password@localhost:5432/fastapi_boilerplate"
    SECRET_KEY: str = "your-super-secret-key-minimum-32-chars-long-change-this"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 60 minutes * 24 hours * 7 days = 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@1234"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()