import dash
from dash import Input, Output, State, callback
from src.Chat import Chat
from cache_manager import get_user_data, update_user_data, generate_session_id
from src.Logger import Logger

logger = Logger(__name__).get_logger()


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
    def manage_modal_display(session_data):
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

    @app.callback(
        Output("session-store", "data"),
        Output("username-input", "error"),
        Input("confirm-username", "n_clicks"),
        Input("username-input", "n_submit"),
        State("username-input", "value"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def handle_username_input(n_clicks, n_submit, username, session_id):
        if (n_clicks or n_submit) and username:
            user_data = get_user_data(cache, session_id)
            user_data["username"] = username
            update_user_data(cache, session_id, user_data)
            logger.info(f"Username set for session {session_id}: {username}")
            return {"username": username}, None
        logger.warning("Empty username input")
        return dash.no_update, "Please enter a username"

    @app.callback(
        Output("model-response", "children"),
        Output("question-input", "value"),
        Output("loading-overlay", "visible"),
        Input("submit-button", "n_clicks"),
        Input("keyboard", "n_keydowns"),
        State("question-input", "value"),
        State("session-id", "data"),
        background=True,
        running=[
            (Output("question-input", "disabled"), True, False),
            (Output("submit-button", "disabled"), True, False),
            (Output("loading-overlay", "visible"), True, False),
        ],
        prevent_initial_call=True,
    )
    def update_output(n_clicks: int, n_keydowns: int, value: str, session_id: str):
        if (n_clicks or n_keydowns) and value and session_id:
            user_data = get_user_data(cache, session_id)
            chat = user_data["chat"]
            logger.info(f"User sent message: {value}")
            response = chat.ask(value)
            user_data["chat"] = chat
            update_user_data(cache, session_id, user_data)
            logger.debug(f"Updated chat for session {session_id}")
            return response, "", False
        logger.warning("Invalid input for update_output")
        return dash.no_update, dash.no_update, False

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
        Output("model-response", "children", allow_duplicate=True),
        Input("history-button", "n_clicks"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def show_history(n_clicks, session_id):
        if n_clicks and session_id:
            user_data = get_user_data(cache, session_id)
            chat = user_data["chat"]
            history = "\n\n".join(
                [
                    (f"Q: {msg.content}" if msg.role == "user" else f"A: {msg.content}")
                    for msg in chat.messages
                ]
            )
            logger.debug(f"Retrieved history for session {session_id}: {history}")
            return history
        logger.warning("Failed to retrieve chat history")
        return "Error while retrieving chat history."
