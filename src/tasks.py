from crewai import Task


def create_intent_task(agent) -> Task:
    return Task(
        description=(
            "Analyze this user message:\n\n"
            "{user_message}\n\n"
            "Determine whether the user wants to add a crop. "
            "If this is not an Add Crop request, respond politely that only Add Crop is supported right now. "
            "If it is an Add Crop request, delegate the work to the Crop Agent."
        ),
        expected_output=(
            "Either a polite unsupported-intent message, a follow-up question for missing crop details, "
            "or a successful crop creation response."
        ),
        agent=agent,
    )


def create_crop_task(agent) -> Task:
    return Task(
        description=(
            "Handle the Add Crop request from this user message:\n\n"
            "{user_message}\n\n"
            "Extract the farm/site name to use as the create_crop name argument. "
            "If the farm/site name is missing, ask one concise follow-up question. "
            "If the farm/site name is available, call the create_crop tool."
        ),
        expected_output=(
            "A concise response explaining whether the crop was created, "
            "or a follow-up question asking for missing information."
        ),
        agent=agent,
    )
