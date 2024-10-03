import os
import dash
from flask_caching import Cache
import logging
import dash_mantine_components as dmc
from layout import create_layout
from callbacks import register_callbacks
from src.Chat import start_ollama_server
from cache_manager import configure_cache, reset_cache
from datetime import timedelta

# Set React version
dash._dash_renderer._set_react_version("18.2.0")

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Start Ollama server
start_ollama_server()

# Initialize background task manager
background_callback_manager = None
if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery

    celery_app = Celery(
        __name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"]
    )
    background_callback_manager = dash.CeleryManager(celery_app)
else:
    # Use Diskcache for non-production apps when developing locally
    import diskcache

    cache = diskcache.Cache("./.cache")
    background_callback_manager = dash.DiskcacheManager(cache)

# Create the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/@mantine/core@5.10.4/dist/mantine.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dates@5.10.4/dist/mantine-dates.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/dropzone@5.10.4/dist/mantine-dropzone.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/spotlight@5.10.4/dist/mantine-spotlight.min.css",
        dmc.styles.NOTIFICATIONS,
        dmc.styles.CHARTS,
    ],
    background_callback_manager=background_callback_manager,
    prevent_initial_callbacks=True,
)


# Réinitialiser le model_queue au démarrage de l'application
def reset_model_queue():
    """Réinitialise le fichier model_queue.txt"""
    queue_file = "scratch/model_queue.txt"
    providers = ["OpenAI", "Replicate", "Ollama"]
    with open(queue_file, "w") as f:
        for provider in providers:
            f.write(f"{provider}: 0\n")


# Configure cache
cache = configure_cache(app)

# Réinitialiser le cache et le model_queue au démarrage de l'application
reset_cache(cache)
reset_model_queue()


# Set up app layout
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=[
        create_layout(),
    ],
)

# Register callbacks
register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
