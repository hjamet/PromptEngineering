import os
from dash import Dash, Input, Output, callback
import dash_mantine_components as dmc

# Set React version
os.environ["REACT_VERSION"] = "18.2.0"

app = Dash(
    __name__,
    external_stylesheets=[
        # Add required CSS extensions
        "https://cdn.jsdelivr.net/npm/@mantine/core@5.10.4/dist/mantine.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dates@5.10.4/dist/mantine-dates.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dropzone@5.10.4/dist/mantine-dropzone.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/spotlight@5.10.4/dist/mantine-spotlight.min.css",
    ],
)


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
            )
        ],
    )


# Wrap the entire app layout with MantineProvider
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"}, children=[create_layout()]
)


@callback(
    Output("output-div", "children"),
    Input("submit-button", "n_clicks"),
    Input("question-input", "value"),
)
def update_output(n_clicks: int, value: str) -> str:
    """
    Update the output div when the submit button is clicked.

    Args:
        n_clicks: Number of times the button has been clicked.
        value: The input value from the text box.

    Returns:
        A message indicating the question has been sent.
    """
    if n_clicks and value:
        return f"Question envoyée : {value}"
    return ""


if __name__ == "__main__":
    app.run(debug=True)
