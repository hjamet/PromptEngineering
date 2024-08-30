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
    main_title = dmc.Title(
        "Learn Prompt Engineering", order=1, style={"textAlign": "center"}
    )
    sub_title = dmc.Title(
        "Level 1", order=2, style={"color": "dimmed", "textAlign": "center"}
    )

    # Creation of the accordion with sliders and settings icon
    accordion = dmc.Accordion(
        chevronPosition="left",
        variant="separated",
        children=[
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        "Model Parameters",
                        icon=DashIconify(
                            icon="tabler:settings",
                            color=dmc.DEFAULT_THEME["colors"]["blue"][6],
                            width=20,
                        ),
                    ),
                    dmc.AccordionPanel(
                        dmc.SimpleGrid(
                            cols=2,
                            spacing="xl",
                            children=[
                                dmc.Alert(
                                    title="Repeat Penalty",
                                    color="indigo",
                                    variant="light",
                                    children=[
                                        dmc.Slider(
                                            id="repeat-penalty-slider",
                                            min=1,
                                            max=2,
                                            step=0.01,
                                            value=1.1,
                                            marks=[
                                                {"value": 1, "label": "1"},
                                                {"value": 2, "label": "2"},
                                            ],
                                            color="indigo",
                                            size="lg",
                                            labelAlwaysOn=True,
                                            style={"width": "100%"},
                                        )
                                    ],
                                ),
                                dmc.Alert(
                                    title="Temperature",
                                    color="teal",
                                    variant="light",
                                    children=[
                                        dmc.Slider(
                                            id="temperature-slider",
                                            min=0,
                                            max=2,
                                            step=0.01,
                                            value=0.7,
                                            marks=[
                                                {"value": 0, "label": "0"},
                                                {"value": 2, "label": "2"},
                                            ],
                                            color="teal",
                                            size="lg",
                                            labelAlwaysOn=True,
                                            style={"width": "100%"},
                                        )
                                    ],
                                ),
                                dmc.Alert(
                                    title="Top-K",
                                    color="grape",
                                    variant="light",
                                    children=[
                                        dmc.Slider(
                                            id="top-k-slider",
                                            min=0,
                                            max=100,
                                            step=1,
                                            value=40,
                                            marks=[
                                                {"value": 0, "label": "0"},
                                                {"value": 100, "label": "100"},
                                            ],
                                            color="grape",
                                            size="lg",
                                            labelAlwaysOn=True,
                                            style={"width": "100%"},
                                        )
                                    ],
                                ),
                                dmc.Alert(
                                    title="Top-P",
                                    color="cyan",
                                    variant="light",
                                    children=[
                                        dmc.Slider(
                                            id="top-p-slider",
                                            min=0,
                                            max=1,
                                            step=0.01,
                                            value=0.95,
                                            marks=[
                                                {"value": 0, "label": "0"},
                                                {"value": 1, "label": "1"},
                                            ],
                                            color="cyan",
                                            size="lg",
                                            labelAlwaysOn=True,
                                            style={"width": "100%"},
                                        )
                                    ],
                                ),
                            ],
                        )
                    ),
                ],
                value="model-parameters",
            ),
        ],
        mt="xl",
        mb="xl",
    )

    question_input = Keyboard(
        id="keyboard",
        captureKeys=[{"key": "Enter", "ctrlKey": False, "shiftKey": False}],
        children=[
            dmc.Textarea(
                id="question-input",
                placeholder="Type your question here...",
                style={"width": "100%", "resize": "vertical"},
                autosize=True,
                minRows=2,
            )
        ],
        style={"width": "100%"},
    )

    submit_button = dmc.Button(
        "Send",
        id="submit-button",
        variant="gradient",
        gradient={"from": "indigo", "to": "cyan"},
        style={"width": "30%", "height": "50px"},  # Modifié
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
            dcc.Markdown(
                id="model-response",
                style={
                    "width": "100%",  # Modifié
                    "marginTop": "20px",
                    "minHeight": "100px",
                    "border": "1px solid #dee2e6",
                    "borderRadius": "4px",
                    "padding": "10px",
                    "backgroundColor": "white",
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
        style={
            "width": "100%",
            "maxWidth": "60vw",
        },
        children=[
            accordion,  # Ajout des sliders ici
            question_input,
            dmc.Center(submit_button),
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

    history_drawer = dmc.Drawer(
        id="history-drawer",
        size="xl",
        padding="md",
        title="Chat History",
        children=[
            dmc.ScrollArea(
                id="history-content",
                style={"height": "calc(100vh - 60px)"},
                children=[],  # Contenu sera rempli par le callback
            )
        ],
    )

    return dmc.Box(
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "minHeight": "100vh",  # Changé de "height" à "minHeight"
            "backgroundColor": "#f8f9fa",
        },
        children=[
            dmc.Container(
                size="xl",  # Changé de "lg" à "xl"
                style={
                    "width": "100%",
                    "maxWidth": "60vw",
                },  # Ajouté pour limiter la largeur à 60% de l'écran
                children=[
                    dmc.Stack(
                        align="stretch",  # Changé de "center" à "stretch"
                        justify="center",
                        gap="xl",
                        children=[main_title, sub_title, welcome_alert, paper_content],
                        style={"width": "100%"},
                    )
                ],
            ),
            username_modal,
            hidden_div,
            *session_stores,  # Utiliser l'unpacking pour ajouter les deux stores
            history_drawer,  # Ajout du drawer ici
        ],
    )
