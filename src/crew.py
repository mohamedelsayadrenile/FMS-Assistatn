import logging
from time import perf_counter

from crewai import Crew, Process

from src.agents import (
    create_farm_agent,
    create_intent_agent,
    create_site_agent,
    create_task_agent,
)
from src.schemas import ChatContext
from src.tasks import create_intent_task


logger = logging.getLogger(__name__)


def build_crew(context: ChatContext) -> Crew:
    intent_agent = create_intent_agent()
    site_agent = create_site_agent(context)
    farm_agent = create_farm_agent(context)
    task_agent = create_task_agent(context)

    return Crew(
        agents=[intent_agent, site_agent, farm_agent, task_agent],
        tasks=[create_intent_task(intent_agent)],
        process=Process.sequential,
        verbose=True,
    )


async def run_fms_assistant(user_message: str, context: ChatContext, conversation_history: str) -> str:
    start_time = perf_counter()
    logger.info(
        "CrewAI run started",
        extra={
            "request_id": context.request_id,
            "conversation_id": context.conversation_id,
            "history_char_count": len(conversation_history),
        },
    )
    crew = build_crew(context)
    try:
        result = await crew.akickoff(
            inputs={
                "user_message": user_message,
                "conversation_id": context.conversation_id,
                "conversation_history": conversation_history,
            }
        )
    except Exception:
        logger.exception(
            "CrewAI run failed",
            extra={"request_id": context.request_id, "conversation_id": context.conversation_id},
        )
        raise

    response = str(result)
    latency_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(
        "CrewAI run completed",
        extra={
            "request_id": context.request_id,
            "conversation_id": context.conversation_id,
            "latency_ms": latency_ms,
            "response_char_count": len(response),
        },
    )
    return response
