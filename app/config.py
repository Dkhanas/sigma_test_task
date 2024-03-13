from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    SCHEMA: str = "http"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./test.db"
    REDIRECT_STATUS_CODE: int = 302

    class Config:
        env_file = ".env"


settings = Settings()
