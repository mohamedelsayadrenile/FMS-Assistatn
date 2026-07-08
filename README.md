FMS Assistant
=============

Simple CrewAI prototype for a Farm Management System assistant.

Run after syncing dependencies:

```bash
uv sync
docker compose -f docker/compose.yml up -d
uv run uvicorn src.main:app --reload
```

Required Redis memory settings:

```env
REDIS_URL=redis://localhost:6379/0
CONVERSATION_MEMORY_LIMIT=10
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a site named Al-Ahliyya Farm Complex located in Sadat City, Egypt.",
    "ConversationID": "conversation-1",
    "JWT": "your-jwt-token",
    "companyId": "0e5c556f-b352-4970-a4e3-f32a465eb12f",
    "managerIds": ["9e91204a-d03d-46cd-83b5-a5b40ff36e5e"]
  }'
```

Arabic example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "عايز أعمل موقع باسم مزرعة الأهلية في مدينة السادات، مصر.",
    "ConversationID": "conversation-1",
    "JWT": "your-jwt-token",
    "companyId": "0e5c556f-b352-4970-a4e3-f32a465eb12f",
    "managerIds": ["9e91204a-d03d-46cd-83b5-a5b40ff36e5e"]
  }'
```
