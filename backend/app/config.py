"""
Application configuration.

Centralizes settings so nothing is hardcoded across the codebase.
For the hackathon MVP we use SQLite and a simple secret key;
these are read from environment variables so they can be swapped
for production values without touching code.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Arogent API"
    app_description: str = (
        "Decision-support API for community diabetes screening. "
        "Arogent Verify estimates a Screening Confidence Score before "
        "Arogent Risk generates any diabetes risk prediction. "
        "This system supports — never replaces — clinical judgement."
    )
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./arogent.db"

    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12  # 12 hours, suits a field worker's shift

    # Screening Confidence Score thresholds (see Arogent Verify)
    confidence_high_threshold: float = 80.0
    confidence_medium_threshold: float = 50.0

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
