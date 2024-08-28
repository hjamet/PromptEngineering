import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Keyboard


def create_layout():
    """
    Create and return the layout for the application.

    Returns:
        dmc.Box: The main layout component.
    """
    main_title = dmc.Title("Learn Prompt Engineering", order=1)
    sub_title = dmc.Title("Level 1", order=2, style={"color": "dimmed"})

    question_input = Keyboard(
        id="keyboard",
        captureKeys=["Enter"],
        children=[
            dmc.TextInput(
                id="question-input",
                placeholder="Type your question here...",
                style={"width": "100%"},
            )
        ],
    )

    submit_button = dmc.Button(
        "Send",
        id="submit-button",
        variant="gradient",
        gradient={"from": "indigo", "to": "cyan"},
        fullWidth=True,
        mt="md",
    )

    output_text = dmc.Text(id="output-div", ta="center", mt="lg")

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
        "History",
        id="history-button",
        leftSection=DashIconify(icon="mdi:history", width=20),
        variant="outline",
        color="blue",
        mt="md",
    )

    button_group = dmc.Group(
        [clean_chat_button, history_button], justify="center", gap="md"
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

    username_modal = dmc.Modal(
        title="Enter your username",
        id="username-modal",
        centered=True,
        closeOnClickOutside=False,
        closeOnEscape=False,
        withCloseButton=False,
        opened=False,
        children=[
            dmc.TextInput(
                id="username-input", placeholder="Your username", required=True
            ),
            dmc.Button("Confirm", id="confirm-username", fullWidth=True, mt="md"),
        ],
    )

    welcome_alert = dmc.Alert(
        id="welcome-alert",
        title="Welcome!",
        color="green",
        icon=DashIconify(icon="mdi:emoticon-happy-outline", width=26, color="green"),
        withCloseButton=True,
        style={"display": "none"},
    )

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
            hidden_div,
        ],
    )
