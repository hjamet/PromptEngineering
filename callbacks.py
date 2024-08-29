import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, clientside_callback
from dash_iconify import DashIconify

from cache_manager import generate_session_id, get_user_data, update_user_data
from src.Chat import Chat
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
            # Check if the username is already taken
            all_sessions = cache.get("all_sessions") or {}
            for sid, data in all_sessions.items():
                if sid != session_id and data.get("username") == username:
                    logger.warning(f"Username '{username}' is already taken")
                    return (
                        dash.no_update,
                        "This username is already taken. Please choose another.",
                    )

            user_data = get_user_data(cache, session_id)
            user_data["username"] = username
            update_user_data(cache, session_id, user_data)

            # Update all_sessions in cache
            all_sessions[session_id] = user_data
            cache.set("all_sessions", all_sessions)

            logger.info(f"Username set for session {session_id}: {username}")
            return {"username": username}, None
        logger.warning("Empty username input")
        return dash.no_update, "Please enter a username"

    @app.callback(
        Output("model-response", "children"),
        Output("question-input", "value"),
        Output("loading-overlay", "visible"),
        Output("hidden-div", "children"),
        Input("submit-button", "n_clicks"),
        Input("keyboard", "n_keydowns"),
        State("question-input", "value"),
        State("session-id", "data"),
        background=True,
        running=[
            (Output("question-input", "disabled"), True, False),
            (Output("submit-button", "disabled"), True, False),
            (Output("loading-overlay", "visible"), True, False),
            (
                Output("model-response", "children"),
                "",
                "",
            ),  # Don't put no_update here, it will break the callback
        ],
        prevent_initial_call=True,
    )
    def update_output(n_clicks: int, n_keydowns: int, value: str, session_id: str):
        """
        Update the chat output based on user input.

        Args:
            n_clicks (int): Number of button clicks.
            n_keydowns (int): Number of key presses.
            value (str): User input text.
            session_id (str): Session identifier.

        Returns:
            tuple: Contains the model response, updated input value, loading state, and focus trigger.
        """
        if (n_clicks or n_keydowns) and value and session_id:
            user_data = get_user_data(cache, session_id)
            chat = user_data["chat"]
            logger.info(f"User sent message: {value}")
            response = chat.ask(value)
            user_data["chat"] = chat
            update_user_data(cache, session_id, user_data)
            logger.debug(f"Updated chat for session {session_id}")

            return str(response), "", False, "trigger_focus"
        return dash.no_update, "", False, dash.no_update

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
                        icon="emojione:smiling-face-with-sunglasses", width=24
                    )
                    color = "blue"
                else:
                    icon = DashIconify(icon="emojione:robot-face", width=24)
                    color = "green"

                history_blocks.append(
                    dmc.Blockquote(
                        msg.content, icon=icon, color=color, mt="md", ms="xs"
                    )
                )

            logger.debug(f"Retrieved history for session {session_id}")
            return True, history_blocks

        logger.warning("Failed to retrieve chat history")
        return False, [dmc.Text("Error while retrieving chat history.")]
