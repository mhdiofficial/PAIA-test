import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import ApiKey
from app.db.session import AsyncSessionLocal, get_session


settings = get_settings()
api_key_header = APIKeyHeader(name=settings.api_key_header_name, auto_error=False)


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


async def get_api_key(  # noqa: D401 - FastAPI dependency
    api_key: Annotated[str | None, Security(api_key_header)]
) -> ApiKey | None:
    """Validate the API key if provided; return matching record or None."""

    if api_key is None:
        return None

    hashed = hash_key(api_key)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ApiKey).where(ApiKey.hashed_key == hashed, ApiKey.is_active.is_(True))
        )
        record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return record


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ApiKeyDep = Annotated[ApiKey | None, Depends(get_api_key)]
