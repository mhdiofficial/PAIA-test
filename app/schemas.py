from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatRequest(BaseModel):
    user_id: str = Field(..., example="user-123")
    message: str = Field(..., example="Hello, bot!")
    provider: str | None = Field(None, description="Optional LLM provider override")


class ChatMessageSchema(BaseModel):
    role: ChatRole
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    reply: str
    provider: str
    history: list[ChatMessageSchema]
