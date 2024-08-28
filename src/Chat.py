import ollama
from collections import namedtuple

Message = namedtuple("Message", ["role", "content"])


class Chat:
    def __init__(self, model="llama3:instruct"):
        self.messages = []
        self.model = model
        try:
            ollama.show(model)
            # Check if Ollama server is accessible and model exists
        except Exception as e:
            print(
                f"Error: Unable to connect to Ollama server or model '{model}' not found."
            )
            print(f"Details: {str(e)}")
            raise

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

        self.add_message("assistant", response_content)
        return response_content


if __name__ == "__main__":
    chat = Chat()
    chat.ask("Hello, how are you?", streamline=True)
