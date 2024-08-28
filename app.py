import os
import dash
import dash_mantine_components as dmc

# Set React version
os.environ["REACT_VERSION"] = "18.2.0"

app = dash.Dash(
    __name__,
    external_stylesheets=[
        # Add required CSS extensions
        "https://cdn.jsdelivr.net/npm/@mantine/core@5.10.4/dist/mantine.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dates@5.10.4/dist/mantine-dates.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dropzone@5.10.4/dist/mantine-dropzone.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/spotlight@5.10.4/dist/mantine-spotlight.min.css",
    ],
)

# ---------------------------------------------------------------------------- #
#                                 DEFINE USERS                                 #
# ---------------------------------------------------------------------------- #
USERS = [
    {"name": "John Doe", "level": 1},
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

    question_input = dmc.TextInput(
        id="question-input",
        placeholder="Tapez votre question ici...",
        style={"width": "100%"},
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

    paper_content = dmc.Paper(
        shadow="sm",
        p="xl",
        withBorder=True,
        style={"width": "100%", "maxWidth": "500px"},
        children=[question_input, submit_button, output_text],
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
                        children=[main_title, sub_title, paper_content],
                    )
                ],
            ),
            username_modal,
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
    dash.Output("username-modal", "opened"),
    dash.Output("output-div", "children"),
    dash.Input("session-store", "data"),
    prevent_initial_call=False,
)
def check_username(session_data):
    """
    Check if the user has a username in the session data and open the modal if not.

    Args:
        session_data (dict): Current session data.

    Returns:
        tuple: (bool, str) Modal opened state and welcome message.
    """
    if session_data and "username" in session_data:
        return False, f"Bienvenue, {session_data['username']}!"
    return True, ""


@app.callback(
    dash.dependencies.Input("confirm-username", "n_clicks"),
    dash.dependencies.Input("username-input", "n_submit"),
    dash.dependencies.State("username-input", "value"),
    dash.dependencies.State("session-store", "data"),
    prevent_initial_call=False,
)
def handle_username_modal(n_clicks, n_submit, username, session_data):
    """
    Handle the username modal opening/closing and display welcome message.

    Args:
        n_clicks (int): Number of confirm button clicks.
        n_submit (int): Number of Enter key presses in input.
        username (str): Input value from username text box.
        session_data (dict): Current session data.
    """
    global USERS
    ctx = dash.callback_context
    if not ctx.triggered:
        if session_data and "username" in session_data:
            dash.set_props("username-modal", {"opened": False})
            dash.set_props(
                "output-div", {"children": f"Bienvenue, {session_data['username']}!"}
            )
            return
        else:
            dash.set_props("username-modal", {"opened": True})
            return

    if (n_clicks or n_submit) and username:
        if not any(user["name"] == username for user in USERS):
            USERS.append({"name": username, "level": 1})
            dash.set_props("username-modal", {"opened": False})
            dash.set_props("username-input", {"error": None})
            dash.set_props("session-store", {"data": {"username": username}})
            dash.set_props("output-div", {"children": f"Bienvenue, {username}!"})
        else:
            dash.set_props("username-modal", {"opened": True})
            dash.set_props("username-input", {"error": "Username already exists"})
    else:
        dash.set_props("username-modal", {"opened": True})


@app.callback(
    dash.dependencies.Input("submit-button", "n_clicks"),
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
