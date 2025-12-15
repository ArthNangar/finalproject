from pydantic import BaseModel
import os

class Settings(BaseModel):
    # App
    app_name: str = "IS601 Final: Secure Calculator"
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PROD")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

settings = Settings()
