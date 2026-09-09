from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://enforcement:enforcement@localhost:5432/enforcement"
    redis_url: str = "redis://localhost:6379/0"
    backend_url: str = "http://localhost:8001"
    frontend_url: str = "http://localhost:5174"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    review_email: str = "reviewer@example.test"
    news_poll_interval_minutes: int = 15
    auto_approval_threshold: float = 0.90
    review_threshold: float = 0.70
    review_token_ttl_hours: int = 48
    cors_origins: str = "http://localhost:5174"
    internal_api_key: str = "development-only-change-me"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()
