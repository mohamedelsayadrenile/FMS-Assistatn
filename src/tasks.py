from crewai import Task


def create_intent_task(agent) -> Task:
    return Task(
        description=(
           """
        Conversation history:

        {conversation_history}

        Analyze this current user message:

        {user_message}

        The user may write in English, Arabic, or Egyptian Arabic dialect.

        Classify the user's intent into exactly one of these two supported flows:

        1) Create Site: the user wants to create a brand-new top-level site/farm.
        Treat Egyptian Arabic phrases like عايز أضيف مكان, اعمل موقع, عايز أعمل موقع as Create Site requests.
        If so, delegate the work to the Site Agent.

        2) Add Crop/Farm: the user wants to add a crop (also called a farm) UNDER an already existing site.
        Treat Egyptian Arabic phrases like ضيف كروب, ضيف محصول, اعمل كروب, اعمل مزرعة, أضيف محصول, عايز أضيف محصول, or عايز أضيف كروب as Add Crop/Farm requests.
        If so, delegate the work to the Farm Agent.

        3) Add Task: the user wants to add a task (a task-type used in the FMS).
        Treat Egyptian Arabic phrases like عايز أضيف مهمة, ضيف مهمة, اعمل مهمة, أضيف مهمة, عايز أعمل مهمة, or ضيف تاسك as Add Task requests.
        If so, delegate the work to the Task Agent.

        If the user is greeting, chatting casually, or their intent is unclear, respond with:
        أهلاً بك 👋

        أنا مساعدك الشخصي في إدارة المزرعة، وممكن أساعدك في:

        1. إضافة موقع جديد 🏡
        2. إضافة محصول 🌱
        3. إضافة مهمة ✅

        تفضل اكتب طلبك، وأنا هساعدك خطوة بخطوة.

        Use the conversation history to resolve follow-up messages (for example, a user continuing a multi-turn add-crop flow).

        Important: Always respond in Egyptian Arabic dialect (اللهجة المصرية العامية), written in Arabic script, regardless of which language the user writes in.
        Tone: Use a formal-yet-friendly tone (احترامي وودود) — polite and professional, but warm and approachable. Greet the user with 'أهلاً'/'تفضل' style pleasantries, yet keep answers concise and well-structured. Avoid overly colloquial slang; keep it dignified and helpful.
           """
        ),
        expected_output=(
            "Either a polite unsupported-intent message, a follow-up question, "
            "or a delegation to the Site Agent or the Farm Agent. Written in Egyptian Arabic dialect."
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
            "Ask follow-up questions in Egyptian Arabic dialect (اللهجة المصرية العامية), written in Arabic script. "
            "Tone: formal-yet-friendly (احترامي وودود) — polite and professional but warm; "
            "greet with 'تفضل'/'أهلاً' pleasantries, keep answers concise and well-structured, avoid overly colloquial slang. "
            "Do not ask for type because it is optional and omitted from the API payload. "
            "Do not ask for timezone because it is always Africa/Cairo. "
            "If both farm/site name and location are available, call the create_site tool."
        ),
        expected_output=(
            "A concise response explaining whether the site was created, "
            "or a follow-up question asking for missing information. Written in Egyptian Arabic dialect."
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
            "Respond in Egyptian Arabic dialect (اللهجة المصرية العامية), written in Arabic script, regardless of the user's language. "
            "Tone: formal-yet-friendly (احترامي وودود) — polite and professional but warm; "
            "greet with 'تفضل'/'أهلاً' pleasantries, keep answers concise and well-structured, avoid overly colloquial slang."
        ),
        expected_output=(
            "Either a list of the user's sites to choose from, a follow-up question for missing details, "
            "or a success/failure message after calling create_crop. Written in Egyptian Arabic dialect."
        ),
        agent=agent,
    )


def create_task_task(agent) -> Task:
    return Task(
        description=(
            "Conversation history:\n\n"
            "{conversation_history}\n\n"
            "Handle this current user message for adding a task (a task-type):\n\n"
            "{user_message}\n\n"
            "The user may write in English, Arabic, or Egyptian Arabic dialect. "
            "Follow this exact multi-turn flow, relying on the conversation history to carry state across turns:\n"
            "Step 1: Ask for the task title and description. Preserve Arabic titles/descriptions exactly as written.\n"
            "Step 2: Ask for input_type. It must be exactly one of: 'string', 'number', 'image', 'checkbox', or 'select'. "
            "If the user gives any other value, list the five allowed options and ask again.\n"
            "Step 3: Ask for farm_type. It must be exactly one of: 'greenhouse', 'traditional_land', or 'trees'. "
            "If the user gives any other value, list the three allowed options and ask again.\n"
            "Step 4: ONLY if input_type is 'select', ask for the list of options (allowed choices). "
            "For every other input_type, do not ask for options.\n"
            "Step 5: When title, description, input_type, and farm_type are present "
            "(plus options when input_type is 'select'), call the create_task tool "
            "with title, description, input_type, farm_type, and options.\n"
            "Step 6: On success, tell the user the task was added successfully, reusing the task title.\n"
            "Respond in Egyptian Arabic dialect (اللهجة المصرية العامية), written in Arabic script, regardless of the user's language. "
            "Keep tool/API parameter values (such as input_type='number') in English as required by the API. "
            "Tone: formal-yet-friendly (احترامي وودود) — polite and professional but warm; "
            "greet with 'تفضل'/'أهلاً' pleasantries, keep answers concise and well-structured, avoid overly colloquial slang."
        ),
        expected_output=(
            "Either a follow-up question for missing details, "
            "or a success/failure message after calling create_task. Written in Egyptian Arabic dialect."
        ),
        agent=agent,
    )
