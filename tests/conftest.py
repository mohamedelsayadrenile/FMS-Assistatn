"""Settings are read at import time, so the environment is pinned before `src` loads."""

import os


os.environ.update(
    {
        "LLM_MODEL": "openai/test-model",
        "LLM_BASE_URL": "http://localhost:8000/v1",
        "LLM_API_KEY": "test-api-key",
        "CREATE_SITE_URL": "https://fms.test/api/sites",
        "DEFAULT_TIMEZONE": "Africa/Cairo",
        "GET_SITES_URL": "https://fms.test/api/sites",
        "CREATE_FARM_URL_TEMPLATE": "https://fms.test/api/sites/{siteId}/farms",
        "CREATE_TASK_URL": "https://fms.test/api/task-types",
        "API_TIMEOUT_SECONDS": "30",
        "REDIS_URL": "redis://localhost:6379/0",
        "CONVERSATION_MEMORY_LIMIT": "12",
        "CONVERSATION_TTL_SECONDS": "3600",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
    }
)

import pytest  # noqa: E402

from src.schemas import ChatContext  # noqa: E402


@pytest.fixture(scope="session")
def context() -> ChatContext:
    return ChatContext(
        conversation_id="conversation-1",
        jwt="test-jwt",
        company_id="company-1",
        manager_ids=["manager-1"],
        request_id="request-1",
    )
