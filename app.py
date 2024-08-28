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
USERS = [
    {"name": "John Doe", "level": 1, "chat": Chat()},
]


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

    paper_content = dmc.Paper(
        shadow="sm",
        p="xl",
        withBorder=True,
        style={"width": "100%", "maxWidth": "500px"},
        children=[question_input, submit_button, output_text, model_response],
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
        user = next((user for user in USERS if user["name"] == username), None)
        if not user:
            # Create new user if not found
            USERS.append({"name": username, "level": 1, "chat": Chat()})

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
    global USERS
    if (n_clicks or n_submit) and username:
        if not any(user["name"] == username for user in USERS):
            USERS.append({"name": username, "level": 1, "chat": Chat()})
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
def update_output(n_clicks, n_keydowns, value, session_data):
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
    if (n_clicks or n_keydowns) and value and session_data:
        username = session_data.get("username")
        user = next((user for user in USERS if user["name"] == username), None)
        if user:
            response = user["chat"].ask(value)
            # Update model response
            dash.set_props("model-response", {"children": response})
        else:
            dash.set_props("model-response", {"children": "User not found"})
    else:
        # Re-enable input if no response
        dash.set_props("question-input", {"disabled": False})
        dash.set_props("model-response", {"children": ""})

    return ""  # Trigger clientside callback


# Ajoutez ce callback clientside
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
    dash.Input("submit-button", "n_clicks"),
    dash.dependencies.Input("question-input", "n_submit"),
    dash.dependencies.State("question-input", "value"),
    prevent_initial_call=True,
)
def update_output(n_clicks: int, n_submit: int, value: str):
    """
    Update the output div when the submit button is clicked or Enter is pressed.

    Args:
        n_clicks (int): Number of times the button has been clicked.
        n_submit (int): Number of times the Enter key has been pressed in the input.
        value (str): The input value from the text box.
    """
    if (n_clicks or n_submit) and value:
        dash.set_props("output-div", {"children": f"Question envoyée : {value}"})
        dash.set_props("question-input", {"value": ""})
    else:
        dash.set_props("output-div", {"children": ""})


if __name__ == "__main__":
    app.run(debug=True)
