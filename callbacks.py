import dash
import dash_mantine_components as dmc
from dash import (
    Input,
    Output,
    State,
    set_props,
    html,
    callback_context,
)
from dash_iconify import DashIconify

import json
from cache_manager import (
    generate_session_id,
    get_user_data,
    update_user_data,
    get_all_users_data,
)
from src.Chat import Chat
from src.Logger import Logger

# -------------------------------- LOAD LEVELS ------------------------------- #
from src.levels.level_1 import Level1
from src.levels.level_2 import Level2
from src.levels.level_3 import Level3

from src.callbacks.user_management import (
    manage_modal_display,
    handle_username_input,
    update_level_info,
)
from src.callbacks.user_input import (
    process_input_and_evaluate,
    update_repeat_penalty_badge,
    update_temperature_badge,
    update_top_k_badge,
    update_top_p_badge,
)

logger = Logger(__name__).get_logger()

LEVELS = {
    1: Level1(),
    2: Level2(),
    3: Level3(),
}

MAX_LEVEL = max(LEVELS.keys())  # Définir le niveau maximum


def register_callbacks(app):
    # Récupérer l'objet Cache directement
    cache = next(iter(app.server.extensions["cache"].values()))

    @app.callback(
        Output("username-modal", "opened"),
        Output("welcome-alert", "style"),
        Output("welcome-alert", "children"),
        Output("session-id", "data"),
        Input("session-store", "data"),
        prevent_initial_call=False,
    )
    def manage_modal_display_callback(session_data):
        return manage_modal_display(session_data, cache)

    @app.callback(
        Output("session-store", "data"),
        Output("username-input", "error"),
        Output("username-modal", "opened", allow_duplicate=True),
        Output("level-instructions-markdown", "children", allow_duplicate=True),
        Output("sub-title", "children"),
        Input("confirm-username", "n_clicks"),
        Input("username-keyboard", "n_keydowns"),
        State("username-input", "value"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def handle_username_input_callback(n_clicks, n_keydowns, username, session_id):
        return handle_username_input(n_clicks, n_keydowns, username, session_id, cache)

    @app.callback(
        Output("model-response", "children"),
        Output("question-input", "value"),
        Output("loading-overlay", "visible"),
        Output("hidden-div", "children"),
        Output("prompt-check-progress", "value"),
        Output("prompt-similarity-progress", "value"),
        Output("answer-check-progress", "value"),
        Output("answer-similarity-progress", "value"),
        Output("notifications-container", "children"),
        Output("level-instructions-markdown", "children", allow_duplicate=True),
        Output("sub-title", "children", allow_duplicate=True),
        Output("scores-modal", "opened", allow_duplicate=True),
        Output("scores-modal", "children", allow_duplicate=True),
        Input("submit-button", "n_clicks"),
        Input("keyboard", "n_keydowns"),
        State("question-input", "value"),
        State("session-id", "data"),
        State("repeat-penalty-slider", "value"),
        State("temperature-slider", "value"),
        State("top-k-slider", "value"),
        State("top-p-slider", "value"),
        State("scores-modal", "children"),
        background=True,
        running=[
            (Output("question-input", "disabled"), True, False),
            (Output("submit-button", "disabled"), True, False),
            (Output("loading-overlay", "visible"), True, False),
        ],
        prevent_initial_call=True,
    )
    def process_input_and_evaluate_callback(*args):
        return process_input_and_evaluate(*args, cache)

    @app.callback(
        Output("repeat-penalty-badge", "children"),
        Input("repeat-penalty-slider", "value"),
    )
    def update_repeat_penalty_badge_callback(value):
        return update_repeat_penalty_badge(value)

    @app.callback(
        Output("temperature-badge", "children"), Input("temperature-slider", "value")
    )
    def update_temperature_badge_callback(value):
        return update_temperature_badge(value)

    @app.callback(Output("top-k-badge", "children"), Input("top-k-slider", "value"))
    def update_top_k_badge_callback(value):
        return update_top_k_badge(value)

    @app.callback(Output("top-p-badge", "children"), Input("top-p-slider", "value"))
    def update_top_p_badge_callback(value):
        return update_top_p_badge(value)

    # Clientside callback to handle focus
    app.clientside_callback(
        """
        function(trigger) {
            if(trigger === "trigger_focus") {
                setTimeout(() => {
                    const input = document.getElementById("question-input");
                    if (input) {
                        input.focus();
                        input.select();
                    }
                }, 100);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("question-input", "value", allow_duplicate=True),
        Input("hidden-div", "children"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("model-response", "children", allow_duplicate=True),
        Input("clean-chat-button", "n_clicks"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def clean_chat(n_clicks, session_id):
        if n_clicks and session_id:
            user_data = get_user_data(cache, session_id)
            user_data["chat"] = Chat()
            update_user_data(cache, session_id, user_data)
            logger.info(f"Cleaned chat for session {session_id}")
            return "Chat cleaned. You can start a new conversation."
        logger.warning("Failed to clean chat")
        return "Error while cleaning the chat."

    @app.callback(
        [Output("history-drawer", "opened"), Output("history-content", "children")],
        [Input("history-button", "n_clicks")],
        [State("session-id", "data")],
    )
    def toggle_history_drawer(n_clicks, session_id):
        """
        Toggle the history drawer and update its content.

        Args:
            n_clicks (int): Number of clicks on the history button.
            session_id (str): Session ID.

        Returns:
            tuple: (bool, list) Drawer opened state and history content.
        """
        if n_clicks is None:
            return False, []

        if session_id:
            user_data = get_user_data(cache, session_id)
            chat = user_data["chat"]
            history_blocks = []

            for msg in chat.messages:
                if msg.role == "user":
                    icon = DashIconify(
                        icon="emojione:smiling-face-with-sunglasses",
                        width=24,
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
                    icon = DashIconify(
                        icon="emojione:robot-face",
                        width=24,
                    )
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

            logger.debug(f"Retrieved history for session {session_id}")
            return True, history_blocks

        logger.warning("Failed to retrieve chat history")
        return False, [dmc.Text("Error while retrieving chat history.")]

    @app.callback(
        Output("level-instructions-markdown", "children", allow_duplicate=True),
        Output("sub-title", "children", allow_duplicate=True),
        Output("scores-modal", "opened", allow_duplicate=True),
        Output("scores-modal", "closeOnClickOutside"),
        Output("scores-modal", "closeOnEscape"),
        Input("session-id", "data"),
        State("session-store", "data"),
        prevent_initial_call=True,
    )
    def update_level_info_callback(session_id, session_data):
        return update_level_info(session_id, session_data, cache)

    @app.callback(
        Output("scores-modal", "opened"),
        Output("scores-update-interval", "disabled"),
        Input("scores-button", "n_clicks"),
        State("scores-modal", "opened"),
        prevent_initial_call=True,
    )
    def toggle_scores_modal(n_clicks, opened):
        if n_clicks:
            return not opened, False  # Activer l'intervalle quand le modal est ouvert
        return opened, opened  # Désactiver l'intervalle quand le modal est fermé

    @app.callback(
        Output("donut-chart-container", "children"),
        Input("scores-update-interval", "n_intervals"),
        Input("scores-modal", "opened"),
    )
    def update_donut_chart(n_intervals, modal_opened):
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
