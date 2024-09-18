from flask_caching import Cache
from src.Chat import Chat
from src.Logger import Logger
import json
import uuid

logger = Logger(__name__).get_logger()


def configure_cache(app):
    """
    Configure Flask-Caching with a filesystem backend.

    Args:
        app: The Flask app instance.

    Returns:
        Cache: Configured cache instance.
    """
    logger.info("Configuring cache")
    cache = Cache(
        app.server,
        config={
            "CACHE_TYPE": "filesystem",
            "CACHE_DIR": "cache-directory",
            "CACHE_THRESHOLD": 200,
            "CACHE_DEFAULT_TIMEOUT": 365 * 24 * 60 * 60,  # 31536000,
        },
    )
    logger.debug("Cache configured successfully")
    return cache


def get_user_data(cache, session_id):
    """
    Get user data from cache.

    Args:
        cache: The cache instance.
        session_id: The session ID.

    Returns:
        dict: User data.
    """
    logger.debug(f"Getting user data for session {session_id}")
    data = cache.get(session_id)
    if data:
        logger.debug(f"User data found for session {session_id}")
        data = json.loads(data)
        data["chat"] = Chat.from_dict(data["chat"])
    else:
        logger.info(f"No user data found for session {session_id}, creating new data")
        data = {"chat": Chat(), "level": 1}
    return data


def update_user_data(cache, session_id, user_data):
    """
    Update user data in cache.

    Args:
        cache: The cache instance.
        session_id: The session ID.
        user_data: The user data to update.
    """
    logger.debug(f"Updating user data for session {session_id}")
    serializable_data = user_data.copy()
    serializable_data["chat"] = user_data["chat"].to_dict()
    cache.set(session_id, json.dumps(serializable_data))
    logger.info(f"User data updated for session {session_id}")


def generate_session_id():
    """Generate a unique session ID."""
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated new session ID: {session_id}")
    return session_id


def get_all_users_data(cache):
    """
    Recovers data from all users.

    Args:
        cache: The cache instance.

    Returns:
        dict: A dictionary containing the data of all users.
    """
    logger.info("Retrieving data for all users")
    all_sessions = json.loads(cache.get("all_sessions") or "{}")
    all_users_data = {}

    for session_id, session_data in all_sessions.items():
        logger.debug(f"Processing data for session {session_id}")
        user_data = get_user_data(cache, session_id)
        all_users_data[session_id] = {
            "username": session_data.get("username"),
            "level": user_data.get("level", 1),
            "chat": user_data.get("chat"),
        }

    logger.info(f"Retrieved data for {len(all_users_data)} users")
    return all_users_data


def reset_cache(cache):
    """
    Resets the cache completely, deleting all user data.

    Args:
        cache: The cache instance to reset.
    """
    logger.warning("Resetting cache")
    # Deletes all cache entries
    cache.clear()

    # Reset session list
    cache.set("all_sessions", json.dumps({}))

    logger.info("Cache successfully reset")
