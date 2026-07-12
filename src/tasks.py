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

        When you delegate, pass the user's COMPLETE original request verbatim (do not summarize or drop details), so the specialized agent can extract every parameter the user already provided and avoid re-asking for it.

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
    # NOTE: Not currently wired into the crew (see src/crew.py). The Site Agent's
    # backstory drives behavior; this description is kept aligned for consistency.
    return Task(
        description=(
            "Handle the Create Site request from this user message:\n\n"
            "{user_message}\n\n"
            "Extract the farm/site name and location from the message to use as create_site arguments. "
            "The farm/site name and location may be written in Arabic or Egyptian Arabic; preserve them exactly. "
            "Never ask for information the user already provided. "
            "If either the farm/site name or location is genuinely missing, ask for the missing pieces "
            "together in one concise follow-up question. "
            "Do not ask for type because it is optional and omitted from the API payload. "
            "Do not ask for timezone because it is always Africa/Cairo. "
            "When both name and location are known, first show a one-line summary and ask the user to confirm; "
            "only after the user confirms, call the create_site tool. "
            "Ask questions and confirmations in Egyptian Arabic dialect (اللهجة المصرية العامية), written in Arabic script. "
            "Tone: formal-yet-friendly (احترامي وودود) — polite and professional but warm; "
            "greet with 'تفضل'/'أهلاً' pleasantries, keep answers concise and well-structured, avoid overly colloquial slang."
        ),
        expected_output=(
            "A concise response: a follow-up question for missing info, a confirmation prompt, "
            "or a success/failure message after calling create_site. Written in Egyptian Arabic dialect."
        ),
        agent=agent,
    )


def create_farm_task(agent) -> Task:
    # NOTE: Not currently wired into the crew (see src/crew.py). The Farm Agent's
    # backstory drives behavior; this description is kept aligned for consistency.
    return Task(
        description=(
            "Conversation history:\n\n"
            "{conversation_history}\n\n"
            "Handle this current user message for adding a crop/farm UNDER an existing site:\n\n"
            "{user_message}\n\n"
            "The user may write in English, Arabic, or Egyptian Arabic dialect. "
            "A crop and a farm mean the same thing here. "
            "Extract everything the user already gave, ask once for what's missing, confirm, then act. "
            "Rely on the conversation history to carry state across turns:\n"
            "Step 1 (EXTRACT FIRST): Pull out every parameter already provided — any site the user named, "
            "farm_name, farm_type, and the crop/tree details. Map natural-language farm types to the API value "
            "(صوبة → 'greenhouse'; أرض/حقل → 'traditional_land'; أشجار/شجر → 'trees'). "
            "Never ask for something the user already provided.\n"
            "Step 2 (RESOLVE THE SITE): Call the get_all_farms tool (or reuse the list already in the history). "
            "If the user named a site matching exactly one entry, use its site_id silently. Otherwise present the "
            "sites as a numbered list and ask which one; accept the reply by number or name.\n"
            "Step 3 (ASK ONCE FOR WHAT'S MISSING): Required is farm_name plus, for 'traditional_land'/'greenhouse': "
            "crop_type, sowing_date (ISO like '2026-06-01'), area value, area unit; for 'trees': tree_species, "
            "planting_date (ISO like '2026-07-09'), number_of_trees, area value, area unit. If farm_type is missing "
            "or invalid, include it and list the three allowed options. Ask for all missing params together in one message.\n"
            "Step 4 (CONFIRM BEFORE ACTING): When site and all required params are known, show a short summary and "
            "ask the user to confirm; do not call the tool yet.\n"
            "Step 5 (ACT ON CONFIRMATION): After the user confirms, build the initial_data object for that farm_type "
            "(crop_type+sowing_date+area for traditional_land/greenhouse; "
            "tree_species+planting_date+number_of_trees+area for trees) "
            "and call the create_crop tool with site_id, farm_name, farm_type, and initial_data.\n"
            "Step 6 (REPORT): On success, tell the user the crop/farm was added successfully.\n"
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
    # NOTE: Not currently wired into the crew (see src/crew.py). The Task Agent's
    # backstory drives behavior; this description is kept aligned for consistency.
    return Task(
        description=(
            "Conversation history:\n\n"
            "{conversation_history}\n\n"
            "Handle this current user message for adding a task (a task-type):\n\n"
            "{user_message}\n\n"
            "The user may write in English, Arabic, or Egyptian Arabic dialect. "
            "Extract everything the user already gave, ask once for what's missing, confirm, then act. "
            "Rely on the conversation history to carry state across turns:\n"
            "Step 1 (EXTRACT FIRST): Pull out every parameter already provided — title, description, input_type, "
            "farm_type, and options. Preserve Arabic titles/descriptions exactly. Map natural language to the API value "
            "(input_type: نص → 'string'; رقم → 'number'; صورة → 'image'; اختيار/صح وخطأ → 'checkbox'; قائمة → 'select'. "
            "farm_type: صوبة → 'greenhouse'; أرض/حقل → 'traditional_land'; أشجار → 'trees'). "
            "Never ask for something the user already provided.\n"
            "Step 2 (ASK ONCE FOR WHAT'S MISSING): Required is title, description, input_type, and farm_type "
            "(plus options ONLY when input_type is 'select'). If input_type or farm_type is invalid, include it and "
            "list its allowed values. Ask for all missing params together in one message; never one field per turn.\n"
            "Step 3 (CONFIRM BEFORE ACTING): When all required params are known, show a short summary and ask the user "
            "to confirm; do not call the tool yet.\n"
            "Step 4 (ACT ON CONFIRMATION): After the user confirms, call the create_task tool "
            "with title, description, input_type, farm_type, and options.\n"
            "Step 5 (REPORT): On success, tell the user the task was added successfully, reusing the task title.\n"
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
