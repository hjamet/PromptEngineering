from flask_caching import Cache
from src.Chat import Chat
import json
import uuid


def configure_cache(app):
    """
    Configure Flask-Caching with a filesystem backend.

    Args:
        app: The Flask app instance.

    Returns:
        Cache: Configured cache instance.
    """
    cache = Cache(
        app.server,
        config={
            "CACHE_TYPE": "filesystem",
            "CACHE_DIR": "cache-directory",
            "CACHE_THRESHOLD": 200,
        },
    )
    return cache


def get_user_data(cache, session_id):
    data = cache.get(session_id)
    if data:
        data = json.loads(data)
        data["chat"] = Chat.from_dict(data["chat"])
    else:
        data = {"chat": Chat(), "level": 1}
    return data


def update_user_data(cache, session_id, user_data):
    serializable_data = user_data.copy()
    serializable_data["chat"] = user_data["chat"].to_dict()
    cache.set(session_id, json.dumps(serializable_data))


def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())
