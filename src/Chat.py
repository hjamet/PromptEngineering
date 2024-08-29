import ollama
from collections import namedtuple
from src.Logger import Logger

Message = namedtuple("Message", ["role", "content"])


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
        self.logger.info(f"Chat instance initialized with model: {model}")

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
