from crewai import Task


def create_intent_task(agent) -> Task:
    return Task(
        description=(
            "Conversation history:\n\n"
            "{conversation_history}\n\n"
            "Analyze this current user message:\n\n"
            "{user_message}\n\n"
            "The user may write in English, Arabic, or Egyptian Arabic dialect. "
            "Classify the user's intent into exactly one of these two supported flows:\n"
            "1) Create Site: the user wants to create a brand-new top-level site/farm. "
            "Treat Egyptian Arabic phrases like عايز أضيف مزرعة, ضيف مزرعة, اعمل موقع, "
            "سجل مزرعة, or عايز أعمل موقع as Create Site requests. "
            "If so, delegate the work to the Site Agent.\n"
            "2) Add Crop/Farm: the user wants to add a crop (also called a farm) UNDER an already existing site. "
            "Treat Egyptian Arabic phrases like ضيف كوب, ضيف محصول, ضيف كورم, اعمل كوب, اعمل فارم, "
            "أضيف محصول عايز أضيف محصول, or عايز أضيف كوب as Add Crop/Farm requests. "
            "If so, delegate the work to the Farm Agent.\n"
            "If the request is neither of these, respond politely that only Create Site and Add Crop/Farm are supported right now. "
            "Use the conversation history to resolve follow-up messages (for example, a user continuing a multi-turn add-crop flow). "
            "Respond in the same language or dialect used by the user."
        ),
        expected_output=(
            "Either a polite unsupported-intent message, a follow-up question, "
            "or a delegation to the Site Agent or the Farm Agent."
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


def create_farm_task(agent) -> Task:
    return Task(
        description=(
            "Conversation history:\n\n"
            "{conversation_history}\n\n"
            "Handle this current user message for adding a crop/farm UNDER an existing site:\n\n"
            "{user_message}\n\n"
            "The user may write in English, Arabic, or Egyptian Arabic dialect. "
            "A crop and a farm mean the same thing here. "
            "Follow this exact multi-turn flow, relying on the conversation history to carry state across turns:\n"
            "Step 1: If no site has been chosen yet in the conversation, call the get_all_farms tool to fetch the user's sites.\n"
            "Step 2: Present the sites as a numbered list and ask which site to add the crop/farm to.\n"
            "Step 3: When the user answers by number or name, match it to the previously listed site "
            "(use the list recorded in the conversation history) and keep its site_id.\n"
            "Step 4: FIRST ask for farm_type. It must be exactly one of: 'traditional_land', 'greenhouse', or 'trees'. "
            "If the user gives any other value, list the three allowed options and ask again.\n"
            "Step 5: After farm_type is confirmed, ask for the remaining required parameters that match that farm_type. "
            "Always also ask for farm_name. "
            "For 'traditional_land' or 'greenhouse' ask: crop_type, sowing_date (ISO date like '2026-06-01'), area value, area unit. "
            "For 'trees' ask: tree_species, planting_date (ISO date like '2026-07-09'), number_of_trees, area value, area unit.\n"
            "Step 6: When all required parameters are present, build the initial_data object for that farm_type "
            "(crop_type+sowing_date+area for traditional_land/greenhouse; "
            "tree_species+planting_date+number_of_trees+area for trees) "
            "and call the create_crop tool with site_id, farm_name, farm_type, and initial_data.\n"
            "Step 7: On success, tell the user the crop/farm was added successfully.\n"
            "Do NOT ask for location (sent empty), and do NOT ask for initialNumber or farmAge (sent as null). "
            "Respond in the same language or dialect used by the user."
        ),
        expected_output=(
            "Either a list of the user's sites to choose from, a follow-up question for missing details, "
            "or a success/failure message after calling create_crop."
        ),
        agent=agent,
    )
