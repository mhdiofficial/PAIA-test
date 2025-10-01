import secrets

from app.api.dependencies import hash_key


def generate_api_key(name: str) -> tuple[str, str]:
    """Generate a plain API key and its hash for insertion into the database."""
    plain = secrets.token_urlsafe(32)
    hashed = hash_key(plain)
    return plain, hashed
