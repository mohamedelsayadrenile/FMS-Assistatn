FMS Assistant
=============

Simple CrewAI prototype for a Farm Management System assistant.

Run after syncing dependencies:

```bash
uv sync
uv run uvicorn src.main:app --reload
```

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a tomato crop to Al-Ahliyya Farm Complex.",
    "ConversationID": "conversation-1",
    "JWT": "your-jwt-token",
    "companyId": "0e5c556f-b352-4970-a4e3-f32a465eb12f",
    "managerIds": ["9e91204a-d03d-46cd-83b5-a5b40ff36e5e"]
  }'
```
