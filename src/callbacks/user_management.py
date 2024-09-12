from typing import Dict, Any, Tuple, Optional
from dash import no_update
from src.levels.level_1 import Level1
from src.levels.level_2 import Level2
from src.levels.level_3 import Level3
from src.Logger import Logger
from cache_manager import (
    generate_session_id,
    get_user_data,
    update_user_data,
)
import json

LEVELS = {
    1: Level1(),
    2: Level2(),
    3: Level3(),
}

MAX_LEVEL = max(LEVELS.keys())

logger = Logger(__name__).get_logger()


def manage_modal_display(
    session_data: Optional[Dict[str, Any]], cache
) -> Tuple[bool, Dict[str, str], str, Optional[str]]:
    """
    Manage modal display based on session data.

    Args:
        session_data (Optional[Dict[str, Any]]): Session data.
        cache: Cache object.

    Returns:
        Tuple[bool, Dict[str, str], str, Optional[str]]: Modal state, welcome alert style, welcome message, and session ID.
    """
    if not session_data:
        session_id = generate_session_id()
        get_user_data(cache, session_id)
        logger.info(f"New session created: {session_id}")
        return True, {"display": "none"}, "", session_id
    username = session_data.get("username")
    if username:
        logger.debug(f"User {username} logged in")
        all_sessions = json.loads(cache.get("all_sessions") or "{}")
        if username not in [data.get("username") for data in all_sessions.values()]:
            session_id = generate_session_id()
            _create_session(cache, session_id, username)
            return False, {"display": "block"}, f"Welcome back, {username}!", session_id
        return False, {"display": "block"}, f"Welcome, {username}!", no_update
    logger.debug("No username in session, showing modal")
    return True, {"display": "none"}, "", no_update


def handle_username_input(
    n_clicks: int, n_keydowns: int, username: str, session_id: str, cache
) -> Tuple[Dict[str, str], Optional[str], bool, str, str]:
    """
    Handle username input, update session data, and set level instructions.

    Args:
        n_clicks (int): Number of clicks on confirm button.
        n_keydowns (int): Number of keydown events.
        username (str): Entered username.
        session_id (str): Current session ID.
        cache: Cache object.

    Returns:
        Tuple[Dict[str, str], Optional[str], bool, str, str]: Updated session data, error message, modal state, instructions, and subtitle.
    """
    if (n_clicks or n_keydowns) and username and session_id:
        all_sessions = json.loads(cache.get("all_sessions") or "{}")
        for sid, data in all_sessions.items():
            if sid != session_id and data.get("username") == username:
                logger.warning(f"Username '{username}' is already taken")
                return (
                    no_update,
                    "This username is already taken. Please choose another.",
                    True,
                    no_update,
                    no_update,
                )

        user_data, _ = _create_session(cache, session_id, username)

        current_level = user_data.get("level", 1)
        level = Level1()
        instructions = level.instructions

        return (
            {"username": username},
            None,
            False,
            instructions,
            f"Level {current_level}",
        )
    logger.warning("Empty username input")
    return (
        no_update,
        "Please enter a username",
        True,
        no_update,
        no_update,
    )


def update_level_info(
    session_id: str, session_data: Dict[str, Any], cache
) -> Tuple[str, str, bool, bool, bool]:
    """
    Update level information based on user session.

    Args:
        session_id (str): User's session ID.
        session_data (Dict[str, Any]): User's session data.
        cache: Cache object.

    Returns:
        Tuple[str, str, bool, bool, bool]: Instructions, level title, modal state, and modal close options.
    """
    if not session_id or not session_data:
        return "Please log in to start the game.", "Welcome", False, True, True

    user_data = get_user_data(cache, session_id)
    current_level = user_data.get("level", 1)

    if current_level > MAX_LEVEL:
        return (
            "Félicitations ! Vous avez terminé tous les niveaux !",
            "Jeu terminé",
            True,
            False,
            False,
        )

    level = LEVELS.get(current_level, Level1())

    return level.instructions, f"Level {current_level}", False, True, True


# ---------------------------------------------------------------------------- #
#                               PRIVATE FUNCTIONS                              #
# ---------------------------------------------------------------------------- #


def _create_session(cache, session_id, username):
    """
    Create a new session for a user.

    Args:
        cache: Cache object.
        session_id (str): Session ID.
        username (str): Username.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: User data and all sessions data.
    """
    user_data = get_user_data(cache, session_id)
    user_data["username"] = username
    update_user_data(cache, session_id, user_data)

    all_sessions = json.loads(cache.get("all_sessions") or "{}")
    all_sessions[session_id] = {"username": username}
    cache.set("all_sessions", json.dumps(all_sessions))

    logger.info(f"New session created for user {username}: {session_id}")
    return user_data, all_sessions
