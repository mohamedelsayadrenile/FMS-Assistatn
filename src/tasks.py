from crewai import Task


def create_intent_task(agent) -> Task:
    return Task(
        description=(
            """
        Conversation history:

        {conversation_history}

        Current user message:

        {user_message}

        Classify the intent into exactly one of these flows and delegate, passing the user's
        COMPLETE original message verbatim (never summarize or drop details):

        1) Create Site — a new top-level site/farm (عايز أضيف مكان، اعمل موقع) → Site Agent.
        2) Add Crop/Farm — a crop under an existing site (ضيف محصول، اعمل كروب، عايز أضيف كروب) → Farm Agent.
        3) Add Task — a task-type (ضيف مهمة، اعمل مهمة، ضيف تاسك) → Task Agent.

        Use the conversation history to resolve follow-up messages in an ongoing flow.

        If the user is greeting, chatting casually, or the intent is unclear, respond with exactly:
        أهلاً بك 👋

        أنا مساعدك الشخصي في إدارة المزرعة، وممكن أساعدك في:

        1. إضافة موقع جديد 🏡
        2. إضافة محصول 🌱
        3. إضافة مهمة ✅

        تفضل اكتب طلبك، وأنا هساعدك خطوة بخطوة.
           """
        ),
        expected_output=(
            "Either a polite unsupported-intent message, a follow-up question, "
            "or a delegation to the Site, Farm, or Task Agent. Written in Egyptian Arabic dialect."
        ),
        agent=agent,
    )
