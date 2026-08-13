from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    llm_model: str
    llm_base_url: str
    llm_api_key: str

    create_site_url: str
    default_timezone: str
    create_site_timeout_seconds: float

    get_sites_url: str
    create_farm_url_template: str
    create_task_url: str

    api_timeout_seconds: float

    redis_url: str

    conversation_memory_limit: int
    conversation_ttl_seconds: int

    log_level: str
    log_format: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()