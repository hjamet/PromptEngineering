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
    def query_and_serialize_data():
        # Initialize user data with a new Chat instance and level 1
        user_data = {"chat": Chat(), "level": 1}
        return json.dumps(
            {"chat": user_data["chat"].to_dict(), "level": user_data["level"]}
        )

    cached_data = cache.get(session_id)
    if cached_data is None:
        cached_data = query_and_serialize_data()
        cache.set(session_id, cached_data)

    user_data = json.loads(cached_data)
    user_data["chat"] = Chat.from_dict(user_data["chat"])
    return user_data


def update_user_data(cache, session_id, user_data):
    cache.delete(session_id)
    cache.set(
        session_id,
        json.dumps({"chat": user_data["chat"].to_dict(), "level": user_data["level"]}),
    )


def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())
