from typing import Dict, Any, Tuple, List, Union
from dash import html, set_props, no_update
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from src.Chat import Chat
from src.Logger import Logger
from src.levels.LevelList import levels, max_level
from cache_manager import get_user_data, update_user_data

logger = Logger(__name__).get_logger()


def process_input_and_evaluate(
    n_clicks: int,
    n_keydowns: int,
    user_prompt: str,
    session_id: str,
    repeat_penalty: float,
    temperature: float,
    top_k: int,
    top_p: float,
    current_modal_children: List[Any],
    cache: Any,
) -> Tuple[
    Union[str, no_update],
    str,
    bool,
    Union[str, no_update],
    float,
    float,
    float,
    float,
    List[Any],
    Union[str, no_update],
    Union[str, no_update],
    bool,
    Union[List[Any], no_update],
]:
    """
    Process user input, evaluate it, and return updated UI components.
    """
    if not (n_clicks or n_keydowns) or not user_prompt or not session_id:
        return _handle_no_input()

    user_data = get_user_data(cache, session_id)

    # Check if the game is already completed
    if user_data.get("game_completed", False):
        return _handle_game_completion(
            None, current_modal_children, [], user_data, cache, session_id
        )

    chat, current_level = user_data["chat"], user_data.get("level", 1)
    level = levels.get(current_level, levels[1])

    _update_system_prompt(chat, level)
    model_response = chat.ask(
        user_prompt,
        temperature=temperature,
        repeat_penalty=repeat_penalty,
        top_k=top_k,
        top_p=top_p,
    )
    result = level(user_prompt, model_response)
    _add_score_to_chat(chat, result.total_score)

    notifications = _create_notifications(current_level, result.messages)

    if result.total_score >= level.min_score_to_pass:
        return _handle_level_up(
            user_data,
            current_level,
            result,
            chat,
            current_modal_children,
            notifications,
            model_response,
            cache,
            session_id,
        )
    else:
        return _handle_same_level(
            current_level,
            result,
            chat,
            user_data,
            cache,
            session_id,
            model_response,
            notifications,
            user_prompt,  # Ajout de user_prompt ici
        )


def update_repeat_penalty_badge(value: float) -> str:
    return f"{value:.2f}"


def update_temperature_badge(value: float) -> str:
    return f"{value:.2f}"


def update_top_k_badge(value: int) -> str:
    return str(int(value))


def update_top_p_badge(value: float) -> str:
    return f"{value:.2f}"


# ---------------------------------------------------------------------------- #
#                               PRIVATE FUNCTIONS                              #
# ---------------------------------------------------------------------------- #


def _update_system_prompt(chat: Chat, level: Any) -> None:
    """Update the system prompt if necessary."""
    if level.system_prompt != chat.system_prompt:
        chat.system_prompt = level.system_prompt
        chat.messages = [msg for msg in chat.messages if msg.role != "system"]
        if chat.system_prompt:
            chat.add_message("system", chat.system_prompt)


def _add_score_to_chat(chat: Chat, score: float) -> None:
    """Add score to the last exchange in the chat."""
    if chat.add_score_to_last_exchange(score):
        logger.info(f"Added score {score} to last exchange")
    else:
        logger.error("Failed to add score to last exchange")


def _create_notifications(
    current_level: int, messages: List[Any]
) -> List[dmc.Notification]:
    """Create notifications based on evaluation messages."""
    notifications = [
        dmc.Notification(
            id="clean-notifications", message="", action="clean", autoClose=False
        )
    ]
    notifications.extend(
        [
            dmc.Notification(
                id=f"notification-{i}",
                title=f"Level {current_level} Feedback",
                message=msg.content,
                color=msg.color,
                icon=DashIconify(icon=msg.icon),
                autoClose=False,
                action="show",
            )
            for i, msg in enumerate(messages)
        ]
    )
    logger.info(f"Created {len(messages)} notifications")
    return notifications


def _handle_level_up(
    user_data: Dict[str, Any],
    current_level: int,
    result: Any,
    chat: Chat,
    current_modal_children: List[Any],
    notifications: List[Any],
    model_response: str,
    cache: Any,
    session_id: str,
) -> Tuple[
    str,
    str,
    bool,
    str,
    float,
    float,
    float,
    float,
    List[Any],
    Union[str, no_update],
    str,
    bool,
    Union[List[Any], no_update],
]:
    """Handle the case when user levels up."""
    current_level += 1
    user_data["level"] = current_level

    if current_level > max_level:
        return _handle_game_completion(
            result, current_modal_children, notifications, user_data, cache, session_id
        )

    next_level = levels.get(current_level, levels[1])
    chat = Chat(
        system_prompt=next_level.system_prompt,
    )
    success_message = levels[current_level - 1].on_success(result.total_score)
    notifications.append(
        _create_level_notification(
            "Level Up", current_level - 1, success_message, "green", "check-circle"
        )
    )

    user_data["chat"] = chat
    update_user_data(cache, session_id, user_data)

    return _create_response(
        result,
        model_response,
        notifications,
        next_level.instructions,
        f"Level {current_level}",
        False,
        no_update,
        "",  # Passer une chaîne vide pour user_prompt
    )


def _handle_game_completion(
    result: Any,
    current_modal_children: List[Any],
    notifications: List[Any],
    user_data: Dict[str, Any],
    cache: Any,
    session_id: str,
) -> Tuple[
    str,
    str,
    bool,
    str,
    float,
    float,
    float,
    float,
    List[Any],
    no_update,
    no_update,
    bool,
    List[Any],
]:
    """Handle the case when user completes all levels."""
    # Increment the user's level to MAX_LEVEL + 1
    user_data["level"] = max_level + 1
    user_data["game_completed"] = True
    update_user_data(cache, session_id, user_data)

    set_props(
        "scores-modal",
        {
            "closeOnClickOutside": False,
            "closeOnEscape": False,
            "withCloseButton": False,
        },
    )
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

    if not any(
        isinstance(child, html.Div) and "Félicitations !" in child.children[0].children
        for child in current_modal_children
    ):
        current_modal_children = [congratulations_message] + current_modal_children

    return _create_response(
        result,
        "",
        notifications,
        no_update,
        no_update,
        True,
        current_modal_children,
        "",  # Passer une chaîne vide pour user_prompt
    )


def _handle_same_level(
    current_level: int,
    result: Any,
    chat: Chat,
    user_data: Dict[str, Any],
    cache: Any,
    session_id: str,
    model_response: str,
    notifications: List[Any],
    user_prompt: str,  # Ajout du paramètre user_prompt
) -> Tuple[
    str,
    str,
    bool,
    str,
    float,
    float,
    float,
    float,
    List[Any],
    no_update,
    str,
    bool,
    no_update,
]:
    """Handle the case when user remains at the same level."""
    if result.total_score < 100:
        failure_message = levels[current_level].on_failure(result.total_score)
        notifications.append(
            _create_level_notification(
                "Feedback", current_level, failure_message, "blue", "info-circle"
            )
        )

    user_data["chat"] = chat
    update_user_data(cache, session_id, user_data)

    return _create_response(
        result,
        model_response,
        notifications,
        no_update,
        f"Level {current_level}",
        False,
        no_update,
        user_prompt,  # Passer user_prompt à _create_response
    )


def _handle_no_input() -> Tuple[
    no_update,
    str,
    bool,
    no_update,
    int,
    int,
    int,
    int,
    List[Any],
    no_update,
    no_update,
    bool,
    no_update,
]:
    """Handle the case when there's no user input."""
    return (
        no_update,
        "",
        False,
        no_update,
        0,
        0,
        0,
        0,
        [],
        no_update,
        no_update,
        False,
        no_update,
    )


def _create_level_notification(
    title: str, level: int, message: str, color: str, icon: str
) -> dmc.Notification:
    """Create a notification for level events."""
    return dmc.Notification(
        id=f"{title.lower().replace(' ', '-')}-notification",
        title=f"{title}: Level {level}",
        message=message,
        color=color,
        icon=DashIconify(icon=icon),
        autoClose=False,
        action="show",
    )


def _create_response(
    result: Any,
    model_response: str,
    notifications: List[Any],
    instructions: Union[str, no_update],
    subtitle: Union[str, no_update],
    open_modal: bool,
    modal_children: Union[List[Any], no_update],
    user_prompt: str,  # Ajout du paramètre user_prompt
) -> Tuple[
    str,
    str,
    bool,
    str,
    float,
    float,
    float,
    float,
    List[Any],
    Union[str, no_update],
    Union[str, no_update],
    bool,
    Union[List[Any], no_update],
]:
    """Create a standardized response tuple."""
    return (
        str(model_response),
        user_prompt,  # Retourner user_prompt au lieu d'une chaîne vide
        False,
        "trigger_focus",
        result.individual_scores.get("prompt_check", 0) / 4,
        result.individual_scores.get("prompt_similarity", 0) / 4,
        result.individual_scores.get("answer_check", 0) / 4,
        result.individual_scores.get("answer_similarity", 0) / 4,
        notifications,
        instructions,
        subtitle,
        open_modal,
        modal_children,
    )
