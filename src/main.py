from contextlib import asynccontextmanager
import logging
from uuid import uuid4

from fastapi import FastAPI
from src.core.config import settings
from src.core.logging import configure_logging
from src.crew import run_fms_assistant
from src.schemas import ChatContext, ChatRequest, ChatResponse
from src.services.memory.RedisMemory import RedisMemory


configure_logging(settings.log_level, settings.log_format)
logger = logging.getLogger(__name__)

memory = RedisMemory(
    redis_url=settings.redis_url,
    message_limit=settings.conversation_memory_limit,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Application startup complete",
        extra={"redis_url": settings.redis_url, "memory_limit": settings.conversation_memory_limit},
    )
    yield
    logger.info("Application shutdown started")
    await memory.close()


app = FastAPI(title="FMS AI Assistant", lifespan=lifespan)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    request_id = str(uuid4())
    logger.info(
        "Chat request started",
        extra={
            "request_id": request_id,
            "conversation_id": request.conversation_id,
            "company_id": request.company_id,
            "manager_count": len(request.manager_ids),
        },
    )
    context = ChatContext(
        conversation_id=request.conversation_id,
        jwt=request.jwt,
        company_id=request.company_id,
        manager_ids=request.manager_ids,
        request_id=request_id,
    )
    conversation_history = await memory.format_history(request.conversation_id)
    logger.info(
        "Conversation history loaded",
        extra={
            "request_id": request_id,
            "conversation_id": request.conversation_id,
            "history_char_count": len(conversation_history),
        },
    )
    response = await run_fms_assistant(request.message, context, conversation_history)
    await memory.add_exchange(request.conversation_id, request.message, response)
    logger.info(
        "Chat request completed",
        extra={
            "request_id": request_id,
            "conversation_id": request.conversation_id,
            "response_char_count": len(response),
        },
    )
    return ChatResponse(response=response)
