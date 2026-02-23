from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parents[1]   # backend/app -> backend
    DB_FILE: Path = BASE_DIR / "car_deals.db"
    DB_URL: str = f"sqlite:///{DB_FILE}"

    MODEL_PATH: str = str(BASE_DIR / "artifacts" / "model.pkl")
    META_PATH: str = str(BASE_DIR / "artifacts" / "meta.json")

    CORS_ORIGINS: str = "http://localhost:3000"

settings = Settings()