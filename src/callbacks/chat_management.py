import dash
from dash import Input, Output, State, callback_context
from src.Chat import Chat
from src.Logger import Logger
from src.utils.callback_utils import (
    _create_notification,
    _update_user_level,
    _generate_history_blocks,
    LEVELS,
)
from cache_manager import get_user_data, update_user_data
import dash_mantine_components as dmc

logger = Logger(__name__).get_logger()


def process_input_and_evaluate(
    n_clicks,
    n_keydowns,
    user_prompt,
    session_id,
    repeat_penalty,
    temperature,
    top_k,
    top_p,
    cache,
):
    """
    Traite l'entrée de l'utilisateur, obtient la réponse du modèle et évalue le niveau.
    """
    if (n_clicks or n_keydowns) and user_prompt and session_id:
        user_data = get_user_data(cache, session_id)
        chat = user_data["chat"]
        current_level = user_data.get("level", 1)

        level = LEVELS.get(current_level, LEVELS[1])

        if level.system_prompt != chat.system_prompt:
            chat.system_prompt = level.system_prompt
            chat.messages = [msg for msg in chat.messages if msg.role != "system"]
            if chat.system_prompt:
                chat.add_message("system", chat.system_prompt)

        model_response = chat.ask(
            user_prompt,
            temperature=temperature,
            repeat_penalty=repeat_penalty,
            top_k=top_k,
            top_p=top_p,
        )

        result = level(user_prompt, model_response)

        if chat.add_score_to_last_exchange(result.total_score):
            logger.info(f"Added score {result.total_score} to last exchange")
        else:
            logger.error("Failed to add score to last exchange")

        notifications = [
            _create_notification("clean-notifications", "", "clean", False)
        ]
        notifications.extend(
            [
                _create_notification(
                    f"notification-{i}",
                    f"Level {current_level} Feedback",
                    msg.content,
                    msg.color,
                    msg.icon,
                )
                for i, msg in enumerate(result.messages)
            ]
        )

        new_level, level_up_notification = _update_user_level(
            user_data, result, level, current_level
        )

        if new_level:
            notifications.append(level_up_notification)
            instructions = LEVELS.get(new_level, LEVELS[1]).instructions
        else:
            instructions = dash.no_update

        if result.total_score < 100:
            failure_message = level.on_failure(result.total_score)
            notifications.append(
                _create_notification(
                    "level-failure-notification",
                    f"Level {current_level} Feedback",
                    failure_message,
                    "blue",
                    "info-circle",
                )
            )

        user_data["chat"] = chat
        update_user_data(cache, session_id, user_data)

        return (
            str(model_response),
            "",
            False,
            "trigger_focus",
            result.individual_scores.get("prompt_check", 0) / 4,
            result.individual_scores.get("prompt_similarity", 0) / 4,
            result.individual_scores.get("answer_check", 0) / 4,
            result.individual_scores.get("answer_similarity", 0) / 4,
            notifications,
            instructions,
            f"Level {new_level or current_level}",
            False,
            dash.no_update,
        )

    return (
        dash.no_update,
        "",
        False,
        dash.no_update,
        0,
        0,
        0,
        0,
        [],
        dash.no_update,
        dash.no_update,
        False,
        dash.no_update,
    )


def clean_chat(n_clicks, session_id, cache):
    """
    Nettoie l'historique du chat pour la session donnée.
    """
    if n_clicks and session_id:
        user_data = get_user_data(cache, session_id)
        user_data["chat"] = Chat()
        update_user_data(cache, session_id, user_data)
        logger.info(f"Cleaned chat for session {session_id}")
        return "Chat cleaned. You can start a new conversation."
    logger.warning("Failed to clean chat")
    return "Error while cleaning the chat."


def toggle_history_drawer(n_clicks, session_id, cache):
    """
    Bascule l'affichage du tiroir d'historique et met à jour son contenu.
    """
    if n_clicks is None:
        return False, []

    if session_id:
        user_data = get_user_data(cache, session_id)
        chat = user_data["chat"]
        history_blocks = _generate_history_blocks(chat)

        logger.debug(f"Retrieved history for session {session_id}")
        return True, history_blocks

    logger.warning("Failed to retrieve chat history")
    return False, [dmc.Text("Error while retrieving chat history.")]
