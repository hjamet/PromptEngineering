import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Keyboard
from dash import dcc
import dash.html


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
        "Welcome",
        order=2,
        style={"color": "dimmed", "textAlign": "center"},
        id="sub-title",
    )

    # Creation of the accordion with sliders and settings icon
    # Creation of the accordion with sliders and settings icon
    accordion_control = dmc.AccordionControl(
        "Model Parameters",
        icon=DashIconify(
            icon="tabler:settings",
            color=dmc.DEFAULT_THEME["colors"]["blue"][6],
            width=20,
        ),
    )

    repeat_penalty_alert = dmc.Alert(
        title=dmc.Group(
            [
                "Repeat Penalty",
                dmc.Badge(
                    id="repeat-penalty-badge",
                    variant="filled",
                    color="indigo",
                    size="lg",
                ),
            ],
            gap="xs",
            justify="space-between",
        ),
        color="indigo",
        variant="light",
        children=[
            dmc.Container(
                children=[
                    dcc.Slider(
                        id="repeat-penalty-slider",
                        min=1,
                        max=2,
                        step=0.01,
                        value=1.1,
                        marks={1: "1", 1.5: "1.5", 2: "2"},
                        tooltip={"placement": "top", "always_visible": False},
                        className="custom-slider custom-slider-indigo",
                    )
                ],
                style={"width": "100%"},
                p="xs",
                mb="xs",
                mt="xs",
            )
        ],
    )

    temperature_alert = dmc.Alert(
        title=dmc.Group(
            [
                "Temperature",
                dmc.Badge(
                    id="temperature-badge",
                    variant="filled",
                    color="teal",
                    size="lg",
                ),
            ],
            gap="xs",
            justify="space-between",
        ),
        color="teal",
        variant="light",
        children=[
            dmc.Container(
                children=[
                    dcc.Slider(
                        id="temperature-slider",
                        min=0,
                        max=2,
                        step=0.01,
                        value=0.7,
                        marks={0: "0", 1: "1", 2: "2"},
                        tooltip={"placement": "top", "always_visible": False},
                        className="custom-slider custom-slider-teal",
                    )
                ],
                style={"width": "100%"},
                p="xs",
                mb="xs",
                mt="xs",
            )
        ],
    )

    top_k_alert = dmc.Alert(
        title=dmc.Group(
            [
                "Top-K",
                dmc.Badge(
                    id="top-k-badge",
                    variant="filled",
                    color="grape",
                    size="lg",
                ),
            ],
            gap="xs",
            justify="space-between",
        ),
        color="grape",
        variant="light",
        children=[
            dmc.Container(
                children=[
                    dcc.Slider(
                        id="top-k-slider",
                        min=0,
                        max=100,
                        step=1,
                        value=40,
                        marks={0: "0", 50: "50", 100: "100"},
                        tooltip={"placement": "top", "always_visible": False},
                        className="custom-slider custom-slider-grape",
                    )
                ],
                style={"width": "100%"},
                p="xs",
                mb="xs",
                mt="xs",
            )
        ],
    )

    top_p_alert = dmc.Alert(
        title=dmc.Group(
            [
                "Top-P",
                dmc.Badge(
                    id="top-p-badge",
                    variant="filled",
                    color="cyan",
                    size="lg",
                ),
            ],
            gap="xs",
            justify="space-between",
        ),
        color="cyan",
        variant="light",
        children=[
            dmc.Container(
                children=[
                    dcc.Slider(
                        id="top-p-slider",
                        min=0,
                        max=1,
                        step=0.01,
                        value=0.95,
                        marks={0: "0", 0.5: "0.5", 1: "1"},
                        tooltip={"placement": "top", "always_visible": False},
                        className="custom-slider custom-slider-cyan",
                    )
                ],
                style={"width": "100%"},
                p="xs",
                mb="xs",
                mt="xs",
            )
        ],
    )

    accordion_panel = dmc.AccordionPanel(
        dmc.SimpleGrid(
            cols=2,
            spacing="xl",
            children=[
                repeat_penalty_alert,
                temperature_alert,
                top_k_alert,
                top_p_alert,
            ],
        )
    )

    accordion = dmc.Accordion(
        chevronPosition="left",
        variant="separated",
        children=[
            dmc.AccordionItem(
                [accordion_control, accordion_panel],
                value="model-parameters",
            ),
        ],
        mt="xl",
        mb="xl",
    )

    # Replace the existing score_progress with this new implementation
    score_progress = dmc.ProgressRoot(
        [
            dmc.ProgressSection(
                dmc.ProgressLabel("Prompt Check"),
                value=3,
                color="cyan",
                id="prompt-check-progress",
            ),
            dmc.ProgressSection(
                dmc.ProgressLabel("Prompt Similarity"),
                value=3,
                color="pink",
                id="prompt-similarity-progress",
            ),
            dmc.ProgressSection(
                dmc.ProgressLabel("Answer Check"),
                value=3,
                color="orange",
                id="answer-check-progress",
            ),
            dmc.ProgressSection(
                dmc.ProgressLabel("Answer Similarity"),
                value=3,
                color="green",
                id="answer-similarity-progress",
            ),
        ],
        size="xl",
        id="score-progress",
        mb="md",
    )

    # Add alert for level messages
    level_messages = dmc.Alert(
        children=[dcc.Markdown(id="level-messages-markdown")],
        id="level-messages",
        title="Level Messages",
        color="orange",
        variant="light",
        mb="md",
        style={"display": "none"},
        icon=DashIconify(icon="mdi:alert-outline", width=26, color="orange"),
        withCloseButton=True,
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

    level_instructions = dmc.Alert(
        id="level-instructions",
        title="Level Instructions",
        color="blue",
        variant="light",
        mb="md",
        children=[dcc.Markdown(id="level-instructions-markdown")],
    )

    paper_content = dmc.Paper(
        shadow="sm",
        p="xl",
        withBorder=True,
        style={
            "width": "100%",
            "maxWidth": "60vw",
        },
        id="paper-content",
        children=[
            level_instructions,
            accordion,
            score_progress,
            level_messages,
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
            Keyboard(
                id="username-keyboard",
                captureKeys=[{"key": "Enter", "ctrlKey": False, "shiftKey": False}],
                children=[
                    dmc.TextInput(
                        id="username-input", placeholder="Your username", required=True
                    )
                ],
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

    notifications_container = dash.html.Div(
        id="notifications-container",
        style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999},
    )

    return dmc.Box(
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "minHeight": "100vh",
            "backgroundColor": "#f8f9fa",
            "width": "100%",  # Ajoutez cette ligne
        },
        children=[
            dmc.Container(
                size="xl",
                className="main-container",
                p=0,  # Ajoutez cette ligne pour supprimer le padding par défaut
                style={"width": "100%"},  # Ajoutez cette ligne
                children=[
                    dmc.Stack(
                        align="stretch",
                        justify="center",
                        gap="xl",
                        children=[main_title, sub_title, welcome_alert, paper_content],
                        style={"width": "100%"},
                    )
                ],
            ),
            username_modal,
            hidden_div,
            *session_stores,
            history_drawer,
            notifications_container,
            dmc.NotificationProvider(),
        ],
    )
