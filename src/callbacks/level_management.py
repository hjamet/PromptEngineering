from dash import Input, Output, State
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


def register_callbacks(app):
    cache = next(iter(app.server.extensions["cache"].values()))

    app.callback(
        Output("username-modal", "opened"),
        Output("welcome-alert", "style"),
        Output("welcome-alert", "children"),
        Output("session-id", "data"),
        Input("session-store", "data"),
        prevent_initial_call=False,
    )(manage_modal_display)

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
    )(lambda *args: process_input_and_evaluate(*args, cache))

    app.callback(
        Output("model-response", "children", allow_duplicate=True),
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
        Output("level-completed", "display"),
        Output("level-instructions", "display"),
        Output("level-instructions-markdown", "display"),
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
        Input("scores-modal", "n_clicks"),
        State("scores-modal", "opened"),
        prevent_initial_call=True,
    )(toggle_scores_modal)

    app.callback(
        Output("scores-modal", "children"),
        Input("interval-component", "n_intervals"),
        State("scores-modal", "opened"),
        prevent_initial_call=True,
    )(lambda *args: update_donut_chart(*args, cache))
