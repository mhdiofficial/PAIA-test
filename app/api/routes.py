from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import ApiKeyDep, SessionDep
from app.db.models import MessageRole
from app.schemas import ChatRequest, ChatResponse, ChatMessageSchema
from app.services.llm import LLMService
from app.services.memory import MemoryService

router = APIRouter()
llm_service = LLMService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    session: SessionDep,
    _: ApiKeyDep,
) -> ChatResponse:
    memory = MemoryService(session)
    history_records = await memory.fetch_history(payload.user_id)

    history_as_dicts = [
        {"role": record.role.value, "content": record.content} for record in history_records
    ]

    try:
        chat_history = llm_service.to_chat_messages(history_as_dicts)
        chat_response = llm_service.chat(
            history=chat_history,
            user_message=payload.message,
            provider=payload.provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    await memory.record_message(payload.user_id, MessageRole.USER, payload.message)
    reply_text = chat_response.message or ""
    await memory.record_message(payload.user_id, MessageRole.ASSISTANT, reply_text)
    await memory.prune_history(payload.user_id)

    history_records = await memory.fetch_history(payload.user_id)

    raw_payload = chat_response.raw if isinstance(chat_response.raw, dict) else {}
    provider = raw_payload.get(
        "model", payload.provider or llm_service.settings.default_llm_provider
    )

    return ChatResponse(
        reply=reply_text,
        provider=str(provider),
        history=[ChatMessageSchema.model_validate(item) for item in history_records],
    )
