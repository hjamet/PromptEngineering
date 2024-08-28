import ollama
from collections import namedtuple
import requests
from requests.exceptions import RequestException
import time
import subprocess
import os
import signal
from src.Logger import Logger
import pickle

Message = namedtuple("Message", ["role", "content"])
Message.__new__.__defaults__ = (None,) * len(Message._fields)


def _asdict(self):
    return {"role": self.role, "content": self.content}


Message._asdict = _asdict


class Chat:
    def __init__(self, model="llama3:instruct", max_retries=3, retry_delay=1):
        """
        Initialize the Chat instance.

        Args:
            model (str): The name of the Ollama model to use.
            max_retries (int): Maximum number of connection attempts.
            retry_delay (int): Delay in seconds between retries.
        """
        self.logger = Logger(__name__).get_logger()
        self.messages = []
        self.model = model
        self.ollama_process = None

        self.start_ollama_server()

        for attempt in range(max_retries):
            try:
                ollama.show(model)
                self.logger.info(
                    f"Successfully connected to Ollama server and loaded model '{model}'."
                )
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                else:
                    self.logger.error(
                        f"Unable to connect to Ollama server or load model '{model}' after {max_retries} attempts."
                    )
                    self.logger.error(f"Details: {str(e)}")
                    raise

    def start_ollama_server(self):
        """
        Start the Ollama server in a subprocess if it's not running.
        """
        try:
            # Try to start Ollama server
            self.logger.info("Attempting to start Ollama server...")
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)  # Give some time for the server to start
            self.logger.info("Ollama server started or was already running.")
        except Exception as e:
            self.logger.warning(
                f"Failed to start Ollama server: {str(e)}. It might already be running."
            )

    def __getstate__(self):
        """
        Prepare object for serialization.
        """
        state = self.__dict__.copy()
        # Remove non-serializable attributes
        state["ollama_process"] = None
        state["logger"] = None
        return state

    def __setstate__(self, state):
        """
        Restore object after deserialization.
        """
        self.__dict__.update(state)
        self.logger = Logger(__name__).get_logger()
        # Don't restart Ollama server, assume it's already running

    def __del__(self):
        """
        Cleanup method, now only logs a message.
        """
        self.logger.info("Chat instance is being destroyed.")

    def add_message(self, role, content):
        self.messages.append(Message(role, content))

    def get_messages(self):
        return self.messages

    def ask(self, message: str, streamline: bool = False) -> str:
        """
        Ask a message to the chat.

        Args:
            message (str): The message to ask.
            streamline (bool): If True, display tokens in console as they are produced.

        Returns:
            str: The answer to the message.
        """
        self.add_message("user", message)
        response_content = ""

        self.logger.debug(f"Sending message to Ollama: {message}")
        for response in ollama.chat(
            model=self.model,
            messages=[
                {"role": msg.role, "content": msg.content} for msg in self.messages
            ],
            stream=True,
        ):
            chunk = response["message"]["content"]
            response_content += chunk
            if streamline:
                print(chunk, end="", flush=True)

        if streamline:
            print()  # New line after streaming

        self.logger.debug(f"Received response from Ollama: {response_content}")
        self.add_message("assistant", response_content)
        return response_content


if __name__ == "__main__":
    chat = Chat()
    chat.ask("Hello, how are you?", streamline=True)
