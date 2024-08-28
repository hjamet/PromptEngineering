from flask_caching import Cache
import pickle
import logging
import copy

USERS_CACHE_KEY = "all_users"


def configure_cache(app):
    """
    Configure Flask-Caching with a more robust backend.

    Args:
        app: The Flask app instance.

    Returns:
        Cache: Configured cache instance.
    """
    cache = Cache(
        app.server,
        config={
            "CACHE_TYPE": "filesystem",
            "CACHE_DIR": "./cache",
            "CACHE_DEFAULT_TIMEOUT": 0,
        },
    )
    return cache


def get_cached_users(cache):
    """
    Retrieve users from cache.

    Args:
        cache: The cache instance.

    Returns:
        dict: A dictionary of users with their Chat instances.
    """
    users = cache.get(USERS_CACHE_KEY)
    if users is None:
        users = {}
    else:
        # Deserialize Chat objects
        for username, user_data in users.items():
            if "chat" in user_data:
                user_data["chat"] = pickle.loads(user_data["chat"])

    logging.debug(f"Retrieved users from cache: {users}")
    return users


def update_cached_users(cache, users):
    """
    Update users in cache.

    Args:
        cache: The cache instance.
        users (dict): A dictionary of users to update in the cache.
    """
    serialized_users = copy.deepcopy(users)
    for user_data in serialized_users.values():
        if "chat" in user_data:
            user_data["chat"] = pickle.dumps(user_data["chat"])

    cache[USERS_CACHE_KEY] = serialized_users
    logging.debug(f"Updated users in cache: {users}")
