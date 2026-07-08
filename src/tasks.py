from crewai import Task


def create_intent_task(agent) -> Task:
    return Task(
        description=(
            "Conversation history:\n\n"
            "{conversation_history}\n\n"
            "Analyze this current user message:\n\n"
            "{user_message}\n\n"
            "The user may write in English, Arabic, or Egyptian Arabic dialect. "
            "Determine whether the user wants to create a site, farm, or farm/site record. "
            "Treat Arabic/Egyptian Arabic phrases like عايز أضيف مزرعة, ضيف مزرعة, اعمل موقع, "
            "سجل مزرعة, or عايز أعمل فارم as Create Site requests. "
            "If this is not a Create Site request, respond politely that only Create Site is supported right now. "
            "Respond in the same language or dialect used by the user. "
            "Use the conversation history to resolve follow-up messages. "
            "If it is a Create Site request, delegate the work to the Site Agent."
        ),
        expected_output=(
            "Either a polite unsupported-intent message, a follow-up question for missing site details, "
            "or a successful site creation response."
        ),
        agent=agent,
    )


def create_site_task(agent) -> Task:
    return Task(
        description=(
            "Handle the Create Site request from this user message:\n\n"
            "{user_message}\n\n"
            "Extract the farm/site name and location to use as create_site arguments. "
            "The farm/site name and location may be written in Arabic or Egyptian Arabic; preserve them exactly. "
            "If either the farm/site name or location is missing, ask one concise follow-up question. "
            "Ask follow-up questions in the same language or dialect used by the user. "
            "Do not ask for type because it is optional and omitted from the API payload. "
            "Do not ask for timezone because it is always Africa/Cairo. "
            "If both farm/site name and location are available, call the create_site tool."
        ),
        expected_output=(
            "A concise response explaining whether the site was created, "
            "or a follow-up question asking for missing information."
        ),
        agent=agent,
    )
