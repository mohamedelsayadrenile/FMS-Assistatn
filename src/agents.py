from crewai import Agent, LLM

from src.config import settings
from src.schemas import ChatContext
from src.tools import create_create_site_tool


def get_llm() -> LLM:
    return LLM(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )


def create_intent_agent() -> Agent:
    return Agent(
        role="Intent Agent",
        goal="Understand the farm owner's request and decide whether it is a Create Site request.",
        backstory=(
            "You are the first agent in a Farm Management System assistant. "
            "Users may write in English, Arabic, or Egyptian Arabic dialect. "
            "Understand Egyptian Arabic phrases for creating or adding a farm/site, such as عايز أضيف مزرعة, "
            "اعمل موقع, ضيف مزرعة, or سجل مزرعة. "
            "Only Create Site requests are supported in this MVP. "
            "If the user asks for anything else, politely explain that only Create Site is supported right now. "
            "Always respond in the same language or dialect used by the user."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=True,
    )


def create_site_agent(context: ChatContext) -> Agent:
    create_site = create_create_site_tool(context)

    return Agent(
        role="Site Agent",
        goal="Collect site creation details and call the create_site tool when ready.",
        backstory=(
            "You handle only site creation in a Farm Management System. "
            "Users may provide details in English, Arabic, or Egyptian Arabic dialect. "
            "Required user-provided information is the farm/site name and location. "
            "Accept Arabic names and Arabic locations exactly as the user writes them. "
            "Timezone is always Africa/Cairo, so do not ask the user for it. "
            "Type is optional and must be omitted, so do not ask the user for it. "
            "If the farm/site name or location is missing, ask a short follow-up question. "
            "Ask follow-up questions in the same language or dialect used by the user. "
            "If both are present, call create_site with name and location."
        ),
        llm=get_llm(),
        tools=[create_site],
        verbose=True,
        allow_delegation=False,
    )
