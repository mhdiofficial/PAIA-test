# LlamaIndex Chatbot

This project implements a FastAPI-based chatbot backend orchestrated with **LlamaIndex**. It
supports conversation persistence in PostgreSQL using async SQLAlchemy, multiple LLM providers
(OpenAI and Google Gemini), and a lightweight Streamlit client for manual testing.

## Features

- `POST /api/chat` endpoint that accepts a `user_id` and message, returning a response from the
  selected LLM (OpenAI by default, Gemini available when configured).
- Conversation history stored durably in PostgreSQL and replayed on every request to maintain
  context across turns.
- Optional API key authentication via the `X-API-Key` header stored as hashed values in the
  database.
- Automatic table creation on startup (migrations-by-code).
- Docker and Docker Compose for local development.
- Streamlit UI for quick testing.

## Project Layout

```
app/
  api/               # FastAPI routers and dependencies
  core/              # Application configuration
  db/                # Async SQLAlchemy engine, models, and metadata
  services/          # LLM integration and memory utilities
  schemas.py         # Pydantic models shared across the API
  main.py            # FastAPI application entrypoint
streamlit_app.py     # Streamlit client for manual testing
Dockerfile           # Backend container definition
docker-compose.yml   # Orchestrates API, Streamlit UI, and PostgreSQL
pyproject.toml       # Project dependencies and tooling configuration
```

## Getting Started

### Prerequisites

- Docker and Docker Compose **or** Python 3.11+ with `pip`.
- API keys for the LLM providers you want to use:
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY` (optional unless using Gemini)

### Environment Variables

Create a `.env` file in the project root (or configure environment variables directly) with the
following values:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/chatbot
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
DEFAULT_LLM_PROVIDER=openai
MAX_HISTORY_MESSAGES=25
```

If you want to secure the API using keys, insert hashed keys into the database. You can generate a
plain/hashed key pair via:

```bash
python -c "from app.utils import generate_api_key; plain, hashed = generate_api_key('local'); print('plain:', plain); print('hashed:', hashed)"
```

Then store the hashed value in PostgreSQL:

```sql
INSERT INTO api_keys (id, name, hashed_key) VALUES (
    gen_random_uuid(),
    'local-dev',
    'hash-from-script'
);
```

### Local Development with Docker

```bash
docker compose up --build
```

- FastAPI service: http://localhost:8000/docs
- Streamlit UI: http://localhost:8501
- PostgreSQL: exposed on port 5432 with default credentials `postgres` / `postgres`.

### Running Locally with Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

For the Streamlit client, run:

```bash
streamlit run streamlit_app.py
```

Ensure PostgreSQL is running and reachable based on your `DATABASE_URL`.

## Streamlit Client

The Streamlit client is a simple interface to exercise the chatbot API. It allows you to provide a
user ID, message, optional API key, and LLM provider override before sending the request. Responses
are displayed along with the current stored conversation history.

## Testing the API

With the server running, you can test the chat endpoint via `curl`:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123", "message": "Hello there"}'
```

If API keys are enabled, include `-H "X-API-Key: your-key"`.

The response will include the assistant reply, the provider used, and the updated conversation
history for that user.

## Notes

- The repository intentionally keeps migrations simple by calling `create_all` on startup; for
  production usage consider integrating Alembic migrations.
- Configure logging level through the `DEBUG` environment variable.
- LlamaIndex will use whichever provider is configured via environment variables and the request's
  `provider` field.
