import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, clientside_callback, set_props, html
from dash_iconify import DashIconify
from dash import dcc

import json
from cache_manager import generate_session_id, get_user_data, update_user_data
from src.Chat import Chat
from src.Logger import Logger

# -------------------------------- LOAD LEVELS ------------------------------- #
from src.levels.level_1 import Level1
from src.levels.level_2 import Level2

logger = Logger(__name__).get_logger()

LEVELS = {
    1: Level1(),
    2: Level2(),
}


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
        Output("username-modal", "opened", allow_duplicate=True),
        Output("level-instructions-markdown", "children", allow_duplicate=True),
        Output("sub-title", "children"),
        Input("confirm-username", "n_clicks"),
        Input("username-keyboard", "n_keydowns"),
        State("username-input", "value"),
        State("session-id", "data"),
        prevent_initial_call=True,
    )
    def handle_username_input(n_clicks, n_keydowns, username, session_id):
        """
        Handle username input, update session data, and set level instructions.

        Args:
            n_clicks (int): Number of clicks on confirm button.
            n_keydowns (int): Number of keydown events.
            username (str): Entered username.
            session_id (str): Current session ID.

        Returns:
            tuple: Updated session data, error message (if any), modal state, level instructions, and subtitle.
        """
        if (n_clicks or n_keydowns) and username and session_id:
            # Check if the username is already taken
            all_sessions = json.loads(cache.get("all_sessions") or "{}")
            for sid, data in all_sessions.items():
                if sid != session_id and data.get("username") == username:
                    logger.warning(f"Username '{username}' is already taken")
                    return (
                        dash.no_update,
                        "This username is already taken. Please choose another.",
                        True,
                        dash.no_update,
                        dash.no_update,
                    )

            user_data = get_user_data(cache, session_id)
            user_data["username"] = username
            update_user_data(cache, session_id, user_data)

            # Update all_sessions in cache
            all_sessions[session_id] = {"username": username}
            cache.set("all_sessions", json.dumps(all_sessions))

            logger.info(f"Username set for session {session_id}: {username}")

            # Get the current level instructions
            current_level = user_data.get("level", 1)
            level = Level1()  # Pour l'instant, nous n'avons que le niveau 1
            instructions = level.instructions

            return (
                {"username": username},
                None,
                False,
                instructions,
                f"Level {current_level}",
            )
        logger.warning("Empty username input")
        return (
            dash.no_update,
            "Please enter a username",
            True,
            dash.no_update,
            dash.no_update,
        )

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
        Input("submit-button", "n_clicks"),
        Input("keyboard", "n_keydowns"),
        State("question-input", "value"),
        State("session-id", "data"),
        State("repeat-penalty-slider", "value"),
        State("temperature-slider", "value"),
        State("top-k-slider", "value"),
        State("top-p-slider", "value"),
        background=True,
        running=[
            (Output("question-input", "disabled"), True, False),
            (Output("submit-button", "disabled"), True, False),
            (Output("loading-overlay", "visible"), True, False),
        ],
        prevent_initial_call=True,
    )
    def process_input_and_evaluate(
        n_clicks: int,
        n_keydowns: int,
        user_prompt: str,
        session_id: str,
        repeat_penalty: float,
        temperature: float,
        top_k: int,
        top_p: float,
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
                next_level = LEVELS.get(current_level, Level1())
                instructions = next_level.instructions
            else:
                instructions = dash.no_update

            user_data["chat"] = chat
            update_user_data(cache, session_id, user_data)

            return (
                str(model_response),
                "",
                False,
                "trigger_focus",
                result.individual_scores["prompt_check"] / 4,
                result.individual_scores["prompt_similarity"] / 4,
                result.individual_scores["answer_check"] / 4,
                result.individual_scores["answer_similarity"] / 4,
                notifications,
                instructions,
                f"Level {current_level}",
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
        )

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
        Output("repeat-penalty-badge", "children"),
        Input("repeat-penalty-slider", "value"),
    )
    def update_repeat_penalty_badge(value):
        return f"{value:.2f}"

    @app.callback(
        Output("temperature-badge", "children"), Input("temperature-slider", "value")
    )
    def update_temperature_badge(value):
        return f"{value:.2f}"

    @app.callback(Output("top-k-badge", "children"), Input("top-k-slider", "value"))
    def update_top_k_badge(value):
        return str(int(value))

    @app.callback(Output("top-p-badge", "children"), Input("top-p-slider", "value"))
    def update_top_p_badge(value):
        return f"{value:.2f}"

    @app.callback(
        Output("level-instructions-markdown", "children", allow_duplicate=True),
        Output("sub-title", "children", allow_duplicate=True),
        Input("session-id", "data"),
        State("session-store", "data"),
        prevent_initial_call=True,
    )
    def update_level_info(session_id, session_data):
        """
        Update level information based on user session.

        Args:
            session_id (str): User's session ID.
            session_data (dict): User's session data.

        Returns:
            tuple: Markdown-formatted instructions and level title.
        """
        if not session_id or not session_data:
            return "Please log in to start the game.", "Welcome"

        user_data = get_user_data(cache, session_id)
        current_level = user_data.get("level", 1)

        # Pour l'instant, nous n'avons que le niveau 1
        level = Level1()

        return level.instructions, f"Level {current_level}"
