import os
import dash
from dash_extensions import Keyboard
from flask_caching import Cache
import logging
import dash_mantine_components as dmc
from cache_manager import configure_cache
from layout import create_layout
from callbacks import register_callbacks
import subprocess
import time

# Set React version
os.environ["REACT_VERSION"] = "18.2.0"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def start_ollama_server():
    """
    Start the Ollama server in a subprocess if it's not running.
    """
    try:
        logger.info("Attempting to start Ollama server...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)  # Give some time for the server to start
        logger.info("Ollama server started or was already running.")
    except Exception as e:
        logger.warning(
            f"Failed to start Ollama server: {str(e)}. It might already be running."
        )


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
    ],
    background_callback_manager=background_callback_manager,
)

# Configure cache
cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        "CACHE_THRESHOLD": 200,
    },
)

# Set up app layout
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=[
        dash.dcc.Store(id="session-store", storage_type="session"),
        create_layout(),
    ],
)

# Register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
