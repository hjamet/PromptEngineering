from typing import Dict, Any, Tuple, List, Union
import dash
from dash import html, set_props
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from src.Chat import Chat
from src.Logger import Logger
from src.levels.level_1 import Level1
from src.levels.level_2 import Level2
from src.levels.level_3 import Level3
from cache_manager import get_user_data, update_user_data

logger = Logger(__name__).get_logger()

LEVELS = {
    1: Level1(),
    2: Level2(),
    3: Level3(),
}

MAX_LEVEL = max(LEVELS.keys())


def process_input_and_evaluate(
    n_clicks: int,
    n_keydowns: int,
    user_prompt: str,
    session_id: str,
    repeat_penalty: float,
    temperature: float,
    top_k: int,
    top_p: float,
    current_modal_children,
    cache,
):
    if (n_clicks or n_keydowns) and user_prompt and session_id:
        user_data = get_user_data(cache, session_id)
        chat = user_data["chat"]
        current_level = user_data.get("level", 1)

        # Obtenir le niveau actuel
        level = LEVELS.get(current_level, Level1())

        # Mettre à jour le system prompt si nécessaire
        if level.system_prompt != chat.system_prompt:
            chat.system_prompt = level.system_prompt
            chat.messages = [msg for msg in chat.messages if msg.role != "system"]
            if chat.system_prompt:
                chat.add_message("system", chat.system_prompt)

        # Get AI response
        model_response = chat.ask(
            user_prompt,
            temperature=temperature,
            repeat_penalty=repeat_penalty,
            top_k=top_k,
            top_p=top_p,
        )

        # Evaluate the level
        result = level(user_prompt, model_response)

        # Add the score to the chat
        if chat.add_score_to_last_exchange(result.total_score):
            logger.info(f"Added score {result.total_score} to last exchange")
        else:
            logger.error("Failed to add score to last exchange")

        try:
            # First, add a "clean" notification to remove all existing notifications
            notifications = [
                dmc.Notification(
                    id="clean-notifications",
                    message="",
                    action="clean",
                    autoClose=False,
                )
            ]

            # Then, add the new notifications
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
                    for i, msg in enumerate(result.messages)
                ]
            )
            logger.info(f"Created {len(result.messages)} notifications")
        except AttributeError as e:
            logger.error(f"AttributeError in creating notifications: {str(e)}")
            notifications = []
        except Exception as e:
            logger.error(f"Unexpected error in creating notifications: {str(e)}")
            notifications = []

        logger.info(f"Result messages: {result.messages}")
        logger.info(f"Created notifications: {notifications}")

        if result.total_score >= level.min_score_to_pass:
            current_level += 1
            user_data["level"] = current_level

            if current_level > MAX_LEVEL:
                # L'utilisateur a terminé tous les niveaux
                congratulations_message = html.Div(
                    [
                        html.H2(
                            "Félicitations !",
                            style={"textAlign": "center", "color": "green"},
                        ),
                        html.P(
                            "Vous avez terminé tous les niveaux !",
                            style={"textAlign": "center"},
                        ),
                    ],
                    style={"marginBottom": "20px"},
                )
                set_props(
                    "scores-modal",
                    {
                        "closeOnClickOutside": False,
                        "closeOnEscape": False,
                        "withCloseButton": False,
                    },
                )

                if not any(
                    isinstance(child, html.Div)
                    and "Félicitations !" in child.children[0].children
                    for child in current_modal_children
                ):
                    current_modal_children = [
                        congratulations_message
                    ] + current_modal_children

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
                    dash.no_update,
                    dash.no_update,
                    True,  # Ouvrir le modal des scores
                    current_modal_children,
                )
            else:
                next_level = LEVELS.get(current_level, Level1())
                instructions = next_level.instructions

                # Effacer l'historique du chat en cas de level up
                chat = Chat(
                    model=chat.model,
                    replicate_model=chat.replicate_model,
                    system_prompt=next_level.system_prompt,
                )
                logger.info(
                    f"User leveled up to level {current_level}. Chat history cleared."
                )

                # Ajouter le message de succès personnalisé
                success_message = level.on_success(result.total_score)
                notifications.append(
                    dmc.Notification(
                        id="level-up-notification",
                        title=f"Level {current_level-1} Completed!",
                        message=success_message,
                        color="green",
                        icon=DashIconify(icon="check-circle"),
                        autoClose=False,
                        action="show",
                    )
                )
        else:
            instructions = dash.no_update

            # Ajouter le message d'échec personnalisé si le score est inférieur à 100
            if result.total_score < 100:
                failure_message = level.on_failure(result.total_score)
                notifications.append(
                    dmc.Notification(
                        id="level-failure-notification",
                        title=f"Level {current_level} Feedback",
                        message=failure_message,
                        color="blue",
                        icon=DashIconify(icon="info-circle"),
                        autoClose=False,
                        action="show",
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
            f"Level {current_level}",
            False,  # Ne pas ouvrir le modal des scores
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
        False,  # Ne pas ouvrir le modal des scores
        dash.no_update,
    )


def update_repeat_penalty_badge(value: float) -> str:
    return f"{value:.2f}"


def update_temperature_badge(value: float) -> str:
    return f"{value:.2f}"


def update_top_k_badge(value: int) -> str:
    return str(int(value))


def update_top_p_badge(value: float) -> str:
    return f"{value:.2f}"
