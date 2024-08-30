import ollama
from collections import namedtuple
from src.Logger import Logger
import subprocess
import time

Message = namedtuple("Message", ["role", "content"])


def start_ollama_server():
    """
    Start the Ollama server in a subprocess if it's not running.
    """
    logger = Logger(__name__).get_logger()
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


class Chat:
    def __init__(self, model="llama3:instruct"):
        """
        Initialize the Chat instance.

        Args:
            model (str): The name of the Ollama model to use.
        """
        self.logger = Logger(__name__).get_logger()
        self.messages = []
        self.model = model
        self.client = ollama.Client()
        self.logger.info(f"Chat instance initialized with model: {model}")

    def add_message(self, role, content):
        self.messages.append(Message(role, content))

    def get_messages(self):
        return self.messages

    def ask(
        self,
        message: str,
        temperature: float = 0.7,
        repeat_penalty: float = 1.1,
        top_k: int = 40,
        top_p: float = 0.95,
        streamline: bool = False,
    ) -> str:
        """
        Ask a message to the chat.

        Args:
            message (str): The message to ask.
            temperature (float): Controls randomness in generation. Higher values make output more random.
            repeat_penalty (float): Penalty for repeating tokens. Higher values make repetitions less likely.
            top_k (int): Limits the next token selection to the K most probable tokens.
            top_p (float): Selects tokens with cumulative probability above this threshold.
            streamline (bool): If True, display tokens in console as they are produced.

        Returns:
            str: The answer to the message.
        """
        self.add_message("user", message)
        response_content = ""

        self.logger.debug(
            f"""Sending message to Ollama: {message}
            - Temperature: {temperature}
            - Repeat Penalty: {repeat_penalty}
            - Top K: {top_k}
            - Top P: {top_p}
            """
        )

        chat_params = {
            "model": self.model,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in self.messages
            ],
            "options": {
                "temperature": temperature,
                "repeat_penalty": repeat_penalty,
                "top_k": top_k,
                "top_p": top_p,
            },
        }

        if streamline:
            chat_params["stream"] = True
            for response in self.client.chat(**chat_params):
                chunk = response["message"]["content"]
                response_content += chunk
                print(chunk, end="", flush=True)
            print()  # New line after streaming
        else:
            response = self.client.chat(**chat_params)
            response_content = response["message"]["content"]

        self.logger.debug(f"Received response from Ollama: {response_content}")
        self.add_message("assistant", response_content)
        return response_content

    def to_dict(self):
        """
        Convert the Chat instance to a dictionary for serialization.
        """
        return {
            "model": self.model,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in self.messages
            ],
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Chat instance from a dictionary.
        """
        chat = cls(model=data["model"])
        for msg in data["messages"]:
            chat.add_message(msg["role"], msg["content"])
        return chat


if __name__ == "__main__":
    chat = Chat()
    chat.ask("Hello, how are you?", streamline=True)
