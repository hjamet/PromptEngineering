import dash
from dash import Input, Output, State, callback
from src.Chat import Chat
from cache_manager import get_cached_users, update_cached_users
from src.Logger import Logger

logger = Logger(__name__).get_logger()


def register_callbacks(app):
    @app.callback(
        Output("username-modal", "opened"),
        Output("welcome-alert", "style"),
        Output("welcome-alert", "children"),
        Input("session-store", "data"),
        prevent_initial_call=False,
    )
    def manage_modal_display(session_data: dict):
        if session_data and "username" in session_data:
            username = session_data["username"]
            users = get_cached_users(app.server.extensions["cache"])
            if username not in users:
                users[username] = {"chat": Chat(), "level": 1}
                update_cached_users(app.server.extensions["cache"], users)
                logger.info(f"New user created: {username}")
            logger.debug(f"User {username} logged in")
            return False, {"display": "block"}, f"Welcome, {username}!"
        logger.debug("No username in session, showing modal")
        return True, {"display": "none"}, ""

    @app.callback(
        Output("session-store", "data"),
        Output("username-input", "error"),
        Input("confirm-username", "n_clicks"),
        Input("username-input", "n_submit"),
        State("username-input", "value"),
        State("session-store", "data"),
        prevent_initial_call=True,
    )
    def handle_username_input(
        n_clicks: int, n_submit: int, username: str, session_data: dict
    ):
        if (n_clicks or n_submit) and username:
            users = get_cached_users(app.server.extensions["cache"])
            if username not in users:
                users[username] = {"chat": Chat(), "level": 1}
                update_cached_users(app.server.extensions["cache"], users)
                logger.info(f"New user created: {username}")
                return {"username": username}, None
            logger.warning(f"Attempt to create existing username: {username}")
            return dash.no_update, "Username already exists"
        logger.warning("Empty username input")
        return dash.no_update, "Please enter a username"

    @callback(
        Output("model-response", "children"),
        Output("question-input", "value"),
        Input("submit-button", "n_clicks"),
        Input("keyboard", "n_keydowns"),
        State("question-input", "value"),
        State("session-store", "data"),
        background=True,
        running=[
            (Output("question-input", "disabled"), True, False),
            (Output("submit-button", "disabled"), True, False),
        ],
        prevent_initial_call=True,
    )
    def update_output(n_clicks: int, n_keydowns: int, value: str, session_data: dict):
        if (n_clicks or n_keydowns) and value and session_data:
            username = session_data.get("username")
            users = get_cached_users(app.server.extensions["cache"])
            if username in users:
                chat = users[username]["chat"]
                logger.info(f"User {username} sent message: {value}")
                response = chat.ask(value)
                users[username]["chat"] = chat
                update_cached_users(app.server.extensions["cache"], users)
                logger.debug(f"Updated chat for user {username}: {chat.messages}")
                return response, ""
            logger.error(f"User not found: {username}")
            return "User not found", ""
        logger.warning("Invalid input for update_output")
        return dash.no_update, dash.no_update

    @app.callback(
        Output("model-response", "children", allow_duplicate=True),
        Input("clean-chat-button", "n_clicks"),
        State("session-store", "data"),
        prevent_initial_call=True,
    )
    def clean_chat(n_clicks: int, session_data: dict) -> str:
        if n_clicks and session_data:
            username = session_data.get("username")
            users = get_cached_users(app.server.extensions["cache"])
            if username in users:
                users[username]["chat"] = Chat()
                update_cached_users(app.server.extensions["cache"], users)
                logger.info(f"Cleaned chat for user {username}")
                return "Chat cleaned. You can start a new conversation."
        logger.warning("Failed to clean chat")
        return "Error while cleaning the chat."

    @app.callback(
        Output("model-response", "children", allow_duplicate=True),
        Input("history-button", "n_clicks"),
        State("session-store", "data"),
        prevent_initial_call=True,
    )
    def show_history(n_clicks: int, session_data: dict) -> str:
        if n_clicks and session_data:
            username = session_data.get("username")
            users = get_cached_users(app.server.extensions["cache"])
            if username in users:
                chat = users[username]["chat"]
                history = "\n\n".join(
                    [
                        (
                            f"Q: {msg.content}"
                            if msg.role == "user"
                            else f"A: {msg.content}"
                        )
                        for msg in chat.messages
                    ]
                )
                logger.debug(f"Retrieved history for user {username}: {history}")
                return history
        logger.warning("Failed to retrieve chat history")
        return "Error while retrieving chat history."
