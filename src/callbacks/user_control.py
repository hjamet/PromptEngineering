import dash
import dash_mantine_components as dmc
from dash import callback_context
from dash_iconify import DashIconify

from cache_manager import get_all_users_data, get_user_data, update_user_data
from src.Chat import Chat
from src.Logger import Logger

logger = Logger(__name__)

from typing import Tuple
import dash_mantine_components as dmc
from dash import html


def clean_chat(n_clicks: int, session_id: str, cache) -> str:
    """
    Clean the chat for a given session.

    Args:
        n_clicks (int): Number of clicks on the clean chat button.
        session_id (str): Unique identifier for the user session.
        cache: Cache object for storing user data.

    Returns:
        str: A message indicating the result of the operation.
    """
    if not n_clicks or not session_id:
        logger.warning("Failed to clean chat: Invalid n_clicks or session_id")
        return "Error while cleaning the chat."

    try:
        user_data = get_user_data(cache, session_id)
        user_data["chat"] = Chat()
        update_user_data(cache, session_id, user_data)
        logger.info(f"Successfully cleaned chat for session {session_id}")
        return "Chat cleaned. You can start a new conversation."
    except Exception as e:
        logger.error(f"Failed to clean chat for session {session_id}: {str(e)}")
        return "Error while cleaning the chat."


def toggle_history_drawer(n_clicks: int, session_id: str, cache) -> tuple[bool, list]:
    """
    Toggle the history drawer and update its content.

    Args:
        n_clicks (int): Number of clicks on the history button.
        session_id (str): Unique identifier for the user session.
        cache: Cache object for storing user data.

    Returns:
        tuple: A tuple containing:
            - bool: Drawer opened state (True if opened, False otherwise)
            - list: History content as a list of Dash Mantine Components
    """
    logger.debug(
        f"Toggling history drawer. n_clicks: {n_clicks}, session_id: {session_id}"
    )

    if n_clicks is None:
        logger.info("History drawer not toggled (n_clicks is None)")
        return False, []

    if not session_id:
        logger.warning("Failed to toggle history drawer: Invalid session_id")
        return False, [dmc.Text("Error: Invalid session ID")]

    try:
        user_data = get_user_data(cache, session_id)
        chat = user_data["chat"]
        history_blocks = []

        # Remove context from the chat
        chat.messages = list(filter(lambda x: x.role != "system", chat.messages))

        for msg in chat.messages:
            if msg.role == "user":
                icon = DashIconify(
                    icon="emojione:smiling-face-with-sunglasses", width=24
                )
                color = "blue"
                content = dmc.Group(
                    [
                        dmc.Text(msg.content),
                        dmc.Badge(
                            (
                                f"Score: {msg.score:.2f}"
                                if msg.score is not None
                                else "Pending"
                            ),
                            color="green",
                        ),
                    ]
                )
            else:
                icon = DashIconify(icon="emojione:robot-face", width=24)
                color = "green"
                content = msg.content

            history_blocks.append(
                dmc.Blockquote(
                    content,
                    icon=icon,
                    color=color,
                    mt="md",
                    ms="xs",
                )
            )

        logger.info(f"Successfully retrieved history for session {session_id}")
        return True, history_blocks

    except Exception as e:
        logger.error(
            f"Failed to retrieve chat history for session {session_id}: {str(e)}"
        )
        return False, [dmc.Text("Error while retrieving chat history.")]


def toggle_scores_modal(n_clicks: int, opened: bool) -> Tuple[bool, bool]:
    """
    Toggle the scores modal and manage the update interval.

    Args:
        n_clicks (int): Number of times the toggle button has been clicked.
        opened (bool): Current state of the modal (opened or closed).

    Returns:
        Tuple[bool, bool]: A tuple containing:
            - The new state of the modal (opened or closed)
            - The state of the update interval (enabled or disabled)

    """
    if n_clicks:
        new_state = not opened
        logger.info(
            f"Toggling scores modal. New state: {'opened' if new_state else 'closed'}"
        )
        return new_state, False  # Enable interval when modal is opened

    logger.debug("No click detected, maintaining current modal state")
    return opened, opened  # Disable interval when modal is closed


def update_donut_chart(n_intervals, modal_opened, cache):
    # Utiliser callback_context pour déterminer ce qui a déclenché le callback
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # Si le modal vient d'être ouvert, forcer la mise à jour
    force_update = triggered_id == "scores-modal" and modal_opened

    if n_intervals is None and not force_update:
        return dash.no_update

    # Utiliser la nouvelle fonction pour obtenir toutes les données des utilisateurs
    all_users_data = get_all_users_data(cache)
    level_counts = {}

    for user_data in all_users_data.values():
        level = user_data.get("level", 1)
        level_counts[level] = level_counts.get(level, 0) + 1

    data = [
        {
            "name": f"Level {level}",
            "value": count,
            "color": f"hsl({(level * 137.5) % 360}, 70%, 50%)",  # Using golden ratio for color distribution
        }
        for level, count in level_counts.items()
    ]

    return dmc.DonutChart(
        data=data,
        size=300,
        thickness=40,
        withTooltip=True,
        tooltipDataSource="segment",
        chartLabel=f"Total: {sum(level_counts.values())}",
        style={"margin": "auto"},
    )


def update_user_table(
    n_intervals: int | None, modal_opened: bool, cache, current_session_id: str
):
    """
    Update the user table with current levels and best scores.

    Args:
        n_intervals (int | None): Number of intervals passed.
        modal_opened (bool): Whether the modal is opened.
        cache: Cache object for storing user data.
        current_session_id (str): The session ID of the current user.

    Returns:
        dmc.Table: A table component with user data.
    """
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    force_update = triggered_id == "scores-modal" and modal_opened

    if n_intervals is None and not force_update:
        return dash.no_update

    all_users_data = get_all_users_data(cache)

    # Calculate best score for each user
    for user_data in all_users_data.values():
        chat = user_data.get("chat")
        if chat and isinstance(chat, Chat):
            best_score = max(
                (msg.score for msg in chat.messages if msg.score is not None), default=0
            )
            user_data["best_score"] = best_score

    sorted_users = sorted(
        all_users_data.items(),
        key=lambda x: (x[1].get("level", 1), x[1].get("best_score", 0)),
        reverse=True,
    )

    rows = []
    for session_id, user_data in sorted_users:
        username = user_data.get("username", "Unknown")
        level = user_data.get("level", 1)
        best_score = user_data.get("best_score", 0)
        is_current_user = session_id == current_session_id

        row = html.Tr(
            [
                html.Td(html.Strong(username) if is_current_user else username),
                html.Td(html.Strong(str(level)) if is_current_user else str(level)),
                html.Td(
                    html.Strong(f"{best_score:.2f}")
                    if is_current_user
                    else f"{best_score:.2f}"
                ),
            ],
            style={"fontWeight": "bold"} if is_current_user else {},
        )
        rows.append(row)

    return dmc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Username", style={"textAlign": "left"}),
                        html.Th("Level", style={"textAlign": "left"}),
                        html.Th("Best Score", style={"textAlign": "left"}),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        striped=True,
        highlightOnHover=True,
        withTableBorder=True,
        withColumnBorders=True,
        withRowBorders=True,
        horizontalSpacing="xs",
        verticalSpacing="xs",
        captionSide="top",
        stickyHeader=True,
        style={"width": "100%", "tableLayout": "fixed"},
    )
