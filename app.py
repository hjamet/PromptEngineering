import os
import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.Chat import Chat
from dash_extensions import Keyboard
from dash import callback, Input, Output, State

# Set React version
os.environ["REACT_VERSION"] = "18.2.0"

# Start background task manager
background_callback_manager = None
if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery

    celery_app = Celery(
        __name__,
        broker=os.environ["REDIS_URL"],
        backend=os.environ["REDIS_URL"],
    )
    background_callback_manager = dash.CeleryManager(celery_app)
else:
    # Diskcache for non-production apps when developing locally
    import diskcache

    cache = diskcache.Cache("./.cache")
    background_callback_manager = dash.DiskcacheManager(cache)

# Create the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        # Add required CSS extensions
        "https://cdn.jsdelivr.net/npm/@mantine/core@5.10.4/dist/mantine.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dates@5.10.4/dist/mantine-dates.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dropzone@5.10.4/dist/mantine-dropzone.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/spotlight@5.10.4/dist/mantine-spotlight.min.css",
    ],
    background_callback_manager=background_callback_manager,
)

# ---------------------------------------------------------------------------- #
#                                 DEFINE USERS                                 #
# ---------------------------------------------------------------------------- #
USERS = {
    "John Doe": {
        "chat": Chat(),
        "level": 1,
    }
}


# Define layout function
def create_layout():
    """
    Creates and returns the layout for the application.

    Returns:
        Box: The main layout component.
    """
    # Define individual components
    main_title = dmc.Title("Learn Prompt Engineering", order=1)
    sub_title = dmc.Title("Level 1", order=2, style={"color": "dimmed"})

    question_input = Keyboard(
        id="keyboard",
        captureKeys=["Enter"],
        children=[
            dmc.TextInput(
                id="question-input",
                placeholder="Tapez votre question ici...",
                style={"width": "100%"},
            )
        ],
    )

    submit_button = dmc.Button(
        "Envoyer",
        id="submit-button",
        variant="gradient",
        gradient={"from": "indigo", "to": "cyan"},
        fullWidth=True,
        mt="md",
    )

    output_text = dmc.Text(
        id="output-div",
        ta="center",
        mt="lg",
    )

    model_response = dmc.Paper(
        id="model-response",
        shadow="sm",
        p="md",
        withBorder=True,
        style={"width": "100%", "maxWidth": "500px", "marginTop": "20px"},
    )

    clean_chat_button = dmc.Button(
        "Clean chat",
        id="clean-chat-button",
        leftSection=DashIconify(icon="mdi:broom", width=20),
        variant="outline",
        color="red",
        mt="md",
    )

    history_button = dmc.Button(
        "Historique",
        id="history-button",
        leftSection=DashIconify(icon="mdi:history", width=20),
        variant="outline",
        color="blue",
        mt="md",
    )

    button_group = dmc.Group(
        [clean_chat_button, history_button],
        justify="center",
        gap="md",
    )

    paper_content = dmc.Paper(
        shadow="sm",
        p="xl",
        withBorder=True,
        style={"width": "100%", "maxWidth": "500px"},
        children=[
            question_input,
            submit_button,
            output_text,
            model_response,
            button_group,
        ],
    )

    # Modal for username input
    username_modal = dmc.Modal(
        title="Entrez votre pseudonyme",
        id="username-modal",
        centered=True,
        closeOnClickOutside=False,
        closeOnEscape=False,
        withCloseButton=False,
        opened=False,
        children=[
            dmc.TextInput(
                id="username-input",
                placeholder="Votre pseudonyme",
                required=True,
            ),
            dmc.Button(
                "Confirmer",
                id="confirm-username",
                fullWidth=True,
                mt="md",
            ),
        ],
    )

    # Add welcome alert
    welcome_alert = dmc.Alert(
        id="welcome-alert",
        title="Bienvenue!",
        color="green",
        icon=DashIconify(icon="mdi:emoticon-happy-outline", width=26, color="green"),
        withCloseButton=True,
        style={"display": "none"},
    )

    # Hidden div for storing data
    hidden_div = dash.html.Div(id="hidden-div", style={"display": "none"})

    return dmc.Box(
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "height": "100vh",
            "backgroundColor": "#f8f9fa",
        },
        children=[
            dmc.Container(
                size="sm",
                children=[
                    dmc.Stack(
                        align="center",
                        justify="center",
                        gap="xl",
                        children=[main_title, sub_title, welcome_alert, paper_content],
                    )
                ],
            ),
            username_modal,
            hidden_div,  # Added hidden_div to the layout
        ],
    )


# Wrap the entire app layout with MantineProvider
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=[
        dash.dcc.Store(id="session-store", storage_type="session"),
        create_layout(),
    ],
)

# ---------------------------------------------------------------------------- #
#                                CALLBACKS                                     #
# ---------------------------------------------------------------------------- #


@app.callback(
    dash.Input("session-store", "data"),
    prevent_initial_call=False,
)
def manage_modal_display(session_data: dict):
    """
    Manage the display of the username modal and welcome alert.

    Args:
        session_data (dict): Current session data.

    Returns:
        None
    """
    if session_data and "username" in session_data:
        username = session_data["username"]
        if username not in USERS:
            # Create new user if not found
            USERS[username] = {"chat": Chat(), "level": 1}

        dash.set_props("username-modal", {"opened": False})
        dash.set_props(
            "welcome-alert",
            {
                "children": f"Bienvenue, {username}!",
                "style": {"display": "block"},
            },
        )
    else:
        dash.set_props("username-modal", {"opened": True})
        dash.set_props("welcome-alert", {"style": {"display": "none"}})


@app.callback(
    dash.Input("confirm-username", "n_clicks"),
    dash.Input("username-input", "n_submit"),
    dash.State("username-input", "value"),
    dash.State("session-store", "data"),
    prevent_initial_call=True,
)
def handle_username_input(
    n_clicks: int, n_submit: int, username: str, session_data: dict
):
    """
    Handle username input and update session data.

    Args:
        n_clicks (int): Number of confirm button clicks.
        n_submit (int): Number of Enter key presses in input.
        username (str): Input value from username text box.
        session_data (dict): Current session data.

    Returns:
        None
    """
    if (n_clicks or n_submit) and username:
        if username not in USERS:
            USERS[username] = {"chat": Chat(), "level": 1}
            dash.set_props("username-input", {"error": None})
            dash.set_props("session-store", {"data": {"username": username}})
        else:
            dash.set_props("username-input", {"error": "Username already exists"})
    else:
        dash.set_props("username-input", {"error": "Please enter a username"})


@callback(
    Output("hidden-div", "children"),
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
def update_output(
    n_clicks: int, n_keydowns: int, value: str, session_data: dict
) -> str:
    """
    Update model response and refocus input.

    Args:
        n_clicks (int): Button click count.
        n_keydowns (int): Number of Enter key presses.
        value (str): Input text value.
        session_data (dict): Current session data.

    Returns:
        str: Empty string to trigger clientside callback.
    """
    global USERS
    if (n_clicks or n_keydowns) and value and session_data:
        username = session_data.get("username")
        if username in USERS:
            chat = USERS[username]["chat"]
            response = chat.ask(value)

            # Update model response
            dash.set_props("model-response", {"children": response})
        else:
            dash.set_props("model-response", {"children": "User not found"})
    else:
        # Re-enable input if no response
        dash.set_props("question-input", {"disabled": False})
        dash.set_props("model-response", {"children": ""})

    return ""  # Trigger clientside callback


# Trigger clientside callback
app.clientside_callback(
    """
    function(trigger) {
        if(trigger !== null) {
            document.getElementById("question-input").focus();
        }
        return null;
    }
    """,
    Output("question-input", "value"),
    Input("hidden-div", "children"),
)


@app.callback(
    Output("model-response", "children", allow_duplicate=True),
    Input("clean-chat-button", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True,
)
def clean_chat(n_clicks: int, session_data: dict) -> str:
    """
    Clean the chat for the current user.

    Args:
        n_clicks (int): Number of button clicks.
        session_data (dict): Current session data.

    Returns:
        str: Confirmation message.
    """
    if n_clicks and session_data:
        username = session_data.get("username")
        if username in USERS:
            USERS[username]["chat"] = Chat()
            return "Chat nettoyé. Vous pouvez commencer une nouvelle conversation."
    return "Erreur lors du nettoyage du chat."


@app.callback(
    Output("model-response", "children", allow_duplicate=True),
    Input("history-button", "n_clicks"),
    State("session-store", "data"),
    prevent_initial_call=True,
)
def show_history(n_clicks: int, session_data: dict) -> str:
    """
    Show chat history for the current user.

    Args:
        n_clicks (int): Number of button clicks.
        session_data (dict): Current session data.

    Returns:
        str: Chat history or error message.
    """
    if n_clicks and session_data:
        username = session_data.get("username")
        if username in USERS:
            history = USERS[username]["chat"].get_messages()
            return "\n\n".join(
                [
                    f"Q: {msg.content}" if msg.role == "user" else f"A: {msg.content}"
                    for msg in history
                ]
            )
    return "Erreur lors de la récupération de l'historique."


if __name__ == "__main__":
    app.run(debug=True)
