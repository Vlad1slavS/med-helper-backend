from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"

    class Config:
        extra = "allow"

settings = Settings()
