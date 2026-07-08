from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from src.crew import run_fms_assistant
from src.schemas import ChatContext, ChatRequest, ChatResponse


app = FastAPI(title="FMS AI Assistant")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    context = ChatContext(
        conversation_id=request.conversation_id,
        jwt=request.jwt,
        company_id=request.company_id,
        manager_ids=request.manager_ids,
    )
    response = await run_in_threadpool(run_fms_assistant, request.message, context)
    return ChatResponse(response=response)
