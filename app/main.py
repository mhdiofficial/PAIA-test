import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.db.session import init_models

settings = get_settings()
logging.basicConfig(level=logging.INFO if not settings.debug else logging.DEBUG)

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_models()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
