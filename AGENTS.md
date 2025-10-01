# AGENTS

## Repository guidelines
- Prefer explicit type hints for all new functions, class attributes, and public variables.
- Keep business logic inside the `app/services` package; FastAPI routes should stay thin and only orchestrate dependencies.
- Do not introduce blocking synchronous I/O inside request handlers—use async-friendly libraries instead.
- Update configuration defaults in `app/core/config.py` whenever new environment flags are required.
- Reflect any new developer-facing commands or environment variables in the `README.md`.

## Testing and tooling
- If you add Python dependencies, make sure `pyproject.toml` and any Docker tooling stay in sync.
- Prefer `pytest` (with `pytest-asyncio` for async tests) when adding automated tests.
- Run `ruff` before committing substantial Python changes when feasible.
