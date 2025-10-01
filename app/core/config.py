from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "LlamaIndex Chatbot"
    environment: str = Field("local", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")

    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/chatbot", env="DATABASE_URL"
    )

    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    google_api_key: str | None = Field(default=None, env="GOOGLE_API_KEY")

    default_llm_provider: str = Field("openai", env="DEFAULT_LLM_PROVIDER")
    max_history_messages: int = Field(15, env="MAX_HISTORY_MESSAGES")

    api_key_header_name: str = Field("X-API-Key", env="API_KEY_HEADER_NAME")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
