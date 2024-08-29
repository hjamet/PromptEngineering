import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Keyboard
from dash import dcc


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

    model_response_area = dmc.Stack(
        pos="relative",
        children=[
            dmc.LoadingOverlay(
                loaderProps={"type": "dots", "color": "blue", "size": "xl"},
                overlayProps={"backgroundOpacity": 0.3},
                visible=False,
                id="loading-overlay",
            ),
            dmc.Paper(
                id="model-response",
                shadow="sm",
                p="md",
                withBorder=True,
                style={
                    "width": "100%",
                    "maxWidth": "500px",
                    "marginTop": "20px",
                    "minHeight": "100px",
                },
            ),
        ],
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
            model_response_area,
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

    session_stores = [
        dcc.Store(id="session-id", storage_type="session"),
        dcc.Store(id="session-store", storage_type="session"),
    ]

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
            *session_stores,  # Utiliser l'unpacking pour ajouter les deux stores
        ],
    )
