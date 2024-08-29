# Learn Prompt Engineering

## Description
Learn Prompt Engineering is an interactive web application designed to help users experiment with and learn prompt engineering using open-source language models. This application uses Dash for the user interface and Ollama for interaction with language models.

## Features
- Intuitive user interface with Dash and Mantine Components
- Interactive chat with a language model (default: llama3:instruct)
- User session management
- Conversation history
- Chat cleaning functionality
- Detailed logging for debugging

## Prerequisites
- Python 3.9+
- Ollama installed and configured on your system

## Installation
1. Clone this repository:
   ```
   git clone [REPO_URL]
   cd promptengineering
   ```

2. Install dependencies with Poetry:
   ```
   poetry install
   ```

## Configuration
- The application uses a filesystem cache by default. To use Redis, set the `REDIS_URL` environment variable.
- The default language model is "llama3:instruct". You can modify this in `src/Chat.py`.

## Usage
1. Start the application:
   ```
   poetry run python app.py
   ```

2. Open your browser and navigate to `http://localhost:8050`.

3. Enter a username when prompted.

4. Start interacting with the language model by asking questions in the text area.

## Project Structure
- `app.py`: Application entry point
- `layout.py`: User interface layout definition
- `callbacks.py`: User interaction handling
- `src/Chat.py`: Class for language model interaction
- `src/Logger.py`: Logging configuration
- `cache_manager.py`: Cache and user session management

## Development
- The application is configured for debugging. Modify `app.run(debug=True)` in `app.py` to disable debug mode in production.
- Logs are stored in the `logs/` folder.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.