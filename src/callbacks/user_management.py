import dash
from dash import Input, Output, State
from cache_manager import generate_session_id, get_user_data, update_user_data
from src.Logger import Logger
from src.levels.level_1 import Level1
import json

logger = Logger(__name__).get_logger()


def manage_modal_display(session_data, cache):
    """
    Gère l'affichage du modal d'utilisateur et initialise la session si nécessaire.
    """
    if not session_data:
        session_id = generate_session_id()
        user_data = get_user_data(cache, session_id)
        logger.info(f"New session created: {session_id}")
        return True, {"display": "none"}, "", session_id
    username = session_data.get("username")
    if username:
        logger.debug(f"User {username} logged in")
        return False, {"display": "block"}, f"Welcome, {username}!", dash.no_update
    logger.debug("No username in session, showing modal")
    return True, {"display": "none"}, "", dash.no_update


def handle_username_input(n_clicks, n_keydowns, username, session_id, cache):
    """
    Gère l'entrée du nom d'utilisateur et met à jour les données de session.
    """
    if (n_clicks or n_keydowns) and username and session_id:
        all_sessions = json.loads(cache.get("all_sessions") or "{}")
        for sid, data in all_sessions.items():
            if sid != session_id and data.get("username") == username:
                logger.warning(f"Username '{username}' is already taken")
                return (
                    dash.no_update,
                    "This username is already taken. Please choose another.",
                    True,
                    dash.no_update,
                    dash.no_update,
                )

        user_data = get_user_data(cache, session_id)
        user_data["username"] = username
        update_user_data(cache, session_id, user_data)

        all_sessions[session_id] = {
            "username": username,
            "level": user_data.get("level", 1),
        }
        cache.set("all_sessions", json.dumps(all_sessions))

        logger.info(f"Username set for session {session_id}: {username}")

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
        dash.no_update,
        "Please enter a username",
        True,
        dash.no_update,
        dash.no_update,
    )
