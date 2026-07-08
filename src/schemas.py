from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str = Field(alias="ConversationID", min_length=1)
    jwt: str = Field(alias="JWT", min_length=1)
    company_id: str = Field(alias="companyId", min_length=1)
    manager_ids: list[str] = Field(alias="managerIds", min_length=1)


class ChatContext(BaseModel):
    conversation_id: str
    jwt: str
    company_id: str
    manager_ids: list[str]


class ChatResponse(BaseModel):
    response: str
