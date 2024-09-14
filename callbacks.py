from dash import (
    Input,
    Output,
    State,
)
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
from src.callbacks.user_control import (
    clean_chat,
    toggle_history_drawer,
    update_donut_chart,
    toggle_scores_modal,
    update_user_table,
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
    def clean_chat_callback(n_clicks, session_id):
        return clean_chat(n_clicks, session_id, cache)

    @app.callback(
        [Output("history-drawer", "opened"), Output("history-content", "children")],
        [Input("history-button", "n_clicks")],
        [State("session-id", "data")],
    )
    def toggle_history_drawer_callback(n_clicks, session_id):
        return toggle_history_drawer(n_clicks, session_id, cache)

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
    def toggle_scores_modal_callback(n_clicks, opened):
        return toggle_scores_modal(n_clicks, opened)

    @app.callback(
        Output("donut-chart-container", "children"),
        Input("scores-update-interval", "n_intervals"),
        Input("scores-modal", "opened"),
    )
    def update_donut_chart_callback(n_intervals, modal_opened):
        return update_donut_chart(n_intervals, modal_opened, cache)

    @app.callback(
        Output("user-table-container", "children"),
        Input("scores-update-interval", "n_intervals"),
        Input("scores-modal", "opened"),
        State("session-id", "data"),
    )
    def update_user_table_callback(n_intervals, modal_opened, session_id):
        return update_user_table(n_intervals, modal_opened, cache, session_id)
