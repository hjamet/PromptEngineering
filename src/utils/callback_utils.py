from src.callbacks.user_management import manage_modal_display, handle_username_input
from src.callbacks.chat_management import (
    process_input_and_evaluate,
    clean_chat,
    toggle_history_drawer,
)
from src.callbacks.level_management import update_level_info
from src.callbacks.ui_updates import (
    update_repeat_penalty_badge,
    update_temperature_badge,
    update_top_k_badge,
    update_top_p_badge,
    toggle_scores_modal,
    update_donut_chart,
)

from src.levels.level_1 import Level1
from src.levels.level_2 import Level2
from src.levels.level_3 import Level3
import dash_mantine_components as dmc
from dash_iconify import DashIconify

LEVELS = {
    1: Level1(),
    2: Level2(),
    3: Level3(),
}

MAX_LEVEL = max(LEVELS.keys())


def register_callbacks(app):
    cache = next(iter(app.server.extensions["cache"].values()))

    app.callback(
        Output("username-modal", "opened"),
        Output("welcome-alert", "style"),
        Output("welcome-alert", "children"),
        Output("session-id", "data"),
        Input("session-store", "data"),
        prevent_initial_call=False,
    )(lambda session_data: manage_modal_display(session_data, cache))

    app.callback(
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
    )(lambda *args: handle_username_input(*args, cache))

    app.callback(
        Output("model-response", "children"),
        Output("user-prompt", "value"),
        Output("user-prompt", "disabled"),
        Output("user-prompt", "focus"),
        Output("prompt-check-badge", "children"),
        Output("prompt-similarity-badge", "children"),
        Output("answer-check-badge", "children"),
        Output("answer-similarity-badge", "children"),
        Output("notifications-container", "children"),
        Output("level-instructions-markdown", "children", allow_duplicate=True),
        Output("sub-title", "children"),
        Output("clean-chat-button", "disabled"),
        Output("clean-chat-button", "children"),
        Input("submit-button", "n_clicks"),
        Input("user-prompt-keyboard", "n_keydowns"),
        State("user-prompt", "value"),
        State("session-id", "data"),
        State("repeat-penalty-slider", "value"),
        State("temperature-slider", "value"),
        State("top-k-slider", "value"),
        State("top-p-slider", "value"),
        prevent_initial_call=True,
    )(lambda *args: process_input_and_evaluate(*args, cache))

    app.callback(
        Output("clean-chat-button", "children"),
        Input("clean-chat-button", "n_clicks"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )(lambda *args: clean_chat(*args, cache))

    app.callback(
        Output("history-drawer", "opened"),
        Output("history-drawer", "children"),
        Input("history-button", "n_clicks"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )(lambda *args: toggle_history_drawer(*args, cache))

    app.callback(
        Output("level-instructions-markdown", "children"),
        Output("sub-title", "children"),
        Output("clean-chat-button", "style"),
        Output("history-button", "style"),
        Output("submit-button", "style"),
        Input("session-id", "data"),
        State("session-store", "data"),
        prevent_initial_call=True,
    )(lambda *args: update_level_info(*args, cache))

    app.callback(
        Output("repeat-penalty-badge", "children"),
        Input("repeat-penalty-slider", "value"),
    )(update_repeat_penalty_badge)

    app.callback(
        Output("temperature-badge", "children"),
        Input("temperature-slider", "value"),
    )(update_temperature_badge)

    app.callback(
        Output("top-k-badge", "children"),
        Input("top-k-slider", "value"),
    )(update_top_k_badge)

    app.callback(
        Output("top-p-badge", "children"),
        Input("top-p-slider", "value"),
    )(update_top_p_badge)

    app.callback(
        Output("scores-modal", "opened"),
        Output("scores-modal", "children"),
        Input("scores-modal", "opened"),
        Input("scores-modal", "n_clicks"),
        prevent_initial_call=True,
    )(toggle_scores_modal)

    app.callback(
        Output("donut-chart", "children"),
        Input("interval-component", "n_intervals"),
        Input("scores-modal", "opened"),
        prevent_initial_call=True,
    )(lambda *args: update_donut_chart(*args, cache))
