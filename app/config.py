from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://alma:alma@localhost:5432/alma"
    SECRET_KEY: str = "change-me-in-production"
    UPLOAD_DIR: str = "./uploads"
    EMAIL_FROM: str = "noreply@alma.local"
    ATTORNEY_EMAIL: str = "attorney@alma.local"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
