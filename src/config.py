from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


class Settings(BaseModel):
    llm_model: str = os.environ.get("LLM_MODEL", "openai/local-model")
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "local-api-key")
    create_site_url: str = os.environ.get("CREATE_SITE_URL", "")
    default_timezone: str = os.environ.get("DEFAULT_TIMEZONE", "")
    create_site_timeout_seconds: float = float(os.environ.get("CREATE_SITE_TIMEOUT_SECONDS", "30"))
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    conversation_memory_limit: int = int(os.environ.get("CONVERSATION_MEMORY_LIMIT", "10"))
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_format: str = os.environ.get("LOG_FORMAT", "json")


settings = Settings()
