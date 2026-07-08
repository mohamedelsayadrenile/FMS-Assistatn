from crewai import Crew, Process

from src.agents import create_crop_agent, create_intent_agent
from src.schemas import ChatContext
from src.tasks import create_intent_task


def build_crew(context: ChatContext) -> Crew:
    intent_agent = create_intent_agent()
    crop_agent = create_crop_agent(context)

    return Crew(
        agents=[intent_agent, crop_agent],
        tasks=[create_intent_task(intent_agent)],
        process=Process.sequential,
        verbose=True,
    )


def run_fms_assistant(user_message: str, context: ChatContext) -> str:
    crew = build_crew(context)
    result = crew.kickoff(
        inputs={
            "user_message": user_message,
            "conversation_id": context.conversation_id,
        }
    )
    return str(result)
