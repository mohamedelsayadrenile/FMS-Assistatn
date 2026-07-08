from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel


ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(ENV_FILE)


class Settings(BaseModel):
    llm_model: str = os.environ.get("LLM_MODEL", "openai/local-model")
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "local-api-key")
    create_site_url: str = os.environ.get("CREATE_SITE_URL", "")
    default_site_type: str = os.environ.get("DEFAULT_SITE_TYPE", "")
    default_site_location: str = os.environ.get("DEFAULT_SITE_LOCATION", "")
    default_timezone: str = os.environ.get("DEFAULT_TIMEZONE", "")
    create_site_timeout_seconds: float = float(os.environ.get("CREATE_SITE_TIMEOUT_SECONDS", "30"))


settings = Settings()
