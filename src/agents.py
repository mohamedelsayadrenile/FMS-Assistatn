from crewai import Agent, LLM

from src.config import settings
from src.schemas import ChatContext
from src.tools import create_create_crop_tool


def get_llm() -> LLM:
    return LLM(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )


def create_intent_agent() -> Agent:
    return Agent(
        role="Intent Agent",
        goal="Understand the farm owner's request and decide whether it is an Add Crop request.",
        backstory=(
            "You are the first agent in a Farm Management System assistant. "
            "Only Add Crop requests are supported in this MVP. "
            "If the user asks for anything else, politely explain that only Add Crop is supported right now."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=True,
    )


def create_crop_agent(context: ChatContext) -> Agent:
    create_crop = create_create_crop_tool(context)

    return Agent(
        role="Crop Agent",
        goal="Collect crop creation details and call the create_crop tool when ready.",
        backstory=(
            "You handle only crop creation in a Farm Management System. "
            "The current first step of crop creation is creating the farm/site. "
            "Required information is the farm/site name. "
            "If the farm/site name is missing, ask a short follow-up question. "
            "If it is present, call create_crop with the farm/site name as the name argument."
        ),
        llm=get_llm(),
        tools=[create_crop],
        verbose=True,
        allow_delegation=False,
    )
