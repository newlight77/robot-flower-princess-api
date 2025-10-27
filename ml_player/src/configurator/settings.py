"""Configuration settings for ML Player service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "ML Player Service"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8001

    # Game Service Connection
    game_service_url: str = "http://localhost:8000"
    game_service_timeout: int = 30

    # ML Player Configuration
    default_strategy: str = "default"  # "default", "aggressive", "conservative"
    enable_ml_models: bool = False  # Set to True when ML models are available
    model_path: str = "./models"

    # Data Collection
    data_dir: str = "data/training"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
