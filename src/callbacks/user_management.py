from typing import Dict, Any, Tuple, Optional, List
from dash import no_update, html
from src.Logger import Logger
from src.levels.LevelList import levels, max_level
from cache_manager import (
    generate_session_id,
    get_user_data,
    update_user_data,
)
import json

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
        level = levels.get(current_level, levels[1])
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
    session_id: str,
    session_data: Dict[str, Any],
    scores_modal_children: List[Any],
    cache,
) -> Tuple[str, str, bool, bool, bool, bool, List[Any]]:
    """
    Update level information based on user session.

    Args:
        session_id (str): User's session ID.
        session_data (Dict[str, Any]): User's session data.
        scores_modal_children (List[Any]): Scores modal children.
        cache: Cache object.

    Returns:
        Tuple[str, str, bool, bool, bool, bool, List[Any]]: Instructions, level title, modal state, modal close options, and modal children.
    """
    if not session_id or not session_data:
        return (
            "Please log in to start the game.",
            "Welcome",
            False,
            True,
            True,
            True,
            scores_modal_children,
        )

    user_data = get_user_data(cache, session_id)
    current_level = user_data.get("level", 1)
    game_completed = user_data.get("game_completed", False)

    if current_level > max_level or game_completed:
        user_data["game_completed"] = True
        update_user_data(cache, session_id, user_data)
        congratulations_message = html.Div(
            [
                html.H2(
                    "🎉 Congratulations! 🎉",
                    style={
                        "textAlign": "center",
                        "color": "#2ecc71",
                        "fontSize": "3em",
                        "marginBottom": "30px",
                        "fontWeight": "bold",
                        "textShadow": "2px 2px 4px rgba(0,0,0,0.1)",
                    },
                ),
                html.P(
                    "You've mastered all levels! Your journey through the challenges has been truly remarkable.",
                    style={
                        "textAlign": "center",
                        "fontSize": "1.4em",
                        "marginBottom": "20px",
                        "color": "#34495e",
                        "lineHeight": "1.6",
                    },
                ),
                html.P(
                    "🏆 Your dedication and problem-solving skills have shined brightly. Well done! 🌟",
                    style={
                        "textAlign": "center",
                        "fontSize": "1.4em",
                        "color": "#34495e",
                        "lineHeight": "1.6",
                    },
                ),
            ],
            style={
                "marginBottom": "40px",
                "padding": "30px",
                "backgroundColor": "#e8f8f5",
                "borderRadius": "15px",
                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
            },
        )
        return (
            "Congratulations! You have completed all levels!",
            "Game Completed",
            True,
            False,
            False,
            False,
            [congratulations_message] + scores_modal_children,
        )

    level = levels.get(current_level, levels[1])
    return (
        level.instructions,
        f"Level {current_level}",
        False,
        True,
        True,
        True,
        scores_modal_children,
    )


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
