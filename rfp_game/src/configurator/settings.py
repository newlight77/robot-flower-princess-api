from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "info"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    # ML Player Service
    ml_player_service_url: str = "http://localhost:8001"
    ml_player_service_timeout: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
