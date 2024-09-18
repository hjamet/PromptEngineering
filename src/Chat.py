import ollama
import replicate
import os
from src.Logger import Logger
import subprocess
import time
from getpass import getpass
from openai import OpenAI


class Message:
    """
    Represents a chat message.

    Attributes:
        role (str): The role of the message sender.
        content (str): The content of the message.
        score (float, optional): The score of the message.
    """

    def __init__(self, role: str, content: str, score: float = None):
        self.role = role
        self.content = content
        self.score = score


def get_replicate_token():
    """Get Replicate API token from environment, file, or user input."""
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        token_file = "scratch/replicate_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token = f.read().strip()

        if not token:
            from getpass import getpass

            token = getpass("Enter your Replicate API token: ")
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, "w") as f:
                f.write(token)

        os.environ["REPLICATE_API_TOKEN"] = token

    return token


def get_openai_token():
    """Get OpenAI API token from environment, file, or user input."""
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        token_file = "scratch/openai_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token = f.read().strip()

        if not token:
            token = getpass("Enter your OpenAI API token: ")
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, "w") as f:
                f.write(token)

        os.environ["OPENAI_API_KEY"] = token

    return token


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

    def __init__(self, system_prompt: str = None, provider: str = "openai"):
        """
        Initialize the Chat instance.

        Args:
            system_prompt (str, optional): The system prompt to use.
            provider (str): The provider to use ('ollama', 'replicate', or 'openai'). Defaults to 'openai'.
        """
        self.logger = Logger(__name__).get_logger()
        self.messages = []
        self.system_prompt = system_prompt
        self.provider = provider.lower()

        if system_prompt:
            self.add_message("system", system_prompt)

        if self.provider == "ollama":
            self.model = "llama3.1"
            self.client = ollama.Client()
        elif self.provider == "replicate":
            self.replicate_model = "meta/meta-llama-3-8b-instruct"
            get_replicate_token()
        elif self.provider == "openai":
            self.model = "gpt-4o-mini"
            get_openai_token()
            self.openai_client = OpenAI()
        else:
            raise ValueError(
                "Invalid provider. Choose 'ollama', 'replicate', or 'openai'."
            )

        if self.provider == "ollama":
            start_ollama_server()

    def add_message(self, role, content, score=None):
        """
        Add a message to the chat history.

        Args:
            role (str): The role of the message sender.
            content (str): The content of the message.
            score (float, optional): The score of the message.
        """
        self.messages.append(Message(role, content, score))

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
            temperature (float): Controls randomness in generation. Range: 0-2.
            repeat_penalty (float): Penalty for repeating tokens.
            top_k (int): Limits token selection to top K options.
            top_p (float): Nucleus sampling threshold. Range: 0-1.
            streamline (bool): If True, stream the response.

        Returns:
            str: The answer to the message.
        """
        self.add_message("user", message, score=None)
        response_content = ""

        if self.provider == "openai":
            formatted_messages = [
                {"role": msg.role, "content": msg.content} for msg in self.messages
            ]

            try:
                completion = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=formatted_messages,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=repeat_penalty,
                    presence_penalty=0,
                    stream=streamline,
                )

                if streamline:
                    for chunk in completion:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            response_content += content
                            print(content, end="", flush=True)
                    print()  # New line after streaming
                else:
                    response_content = completion.choices[0].message.content

            except Exception as e:
                self.logger.error(f"Error with OpenAI API: {str(e)}")
                return f"Error: {str(e)}"

        elif self.provider == "replicate":
            formatted_prompt = ""
            for msg in self.messages:
                formatted_prompt += f"{msg.role}: {msg.content}\n"

            formatted_prompt += f"user: {message}\nassistant: "

            output = replicate.run(
                self.replicate_model,
                input={
                    "prompt": formatted_prompt,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_new_tokens": 500,
                    "repetition_penalty": repeat_penalty,
                },
            )
            response_content = "".join(output)
        elif self.provider == "ollama":
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

        self.logger.debug(f"Received response: {response_content}")
        self.add_message("assistant", response_content)
        return response_content

    def to_dict(self):
        """
        Convert the Chat instance to a dictionary for serialization.

        Returns:
            dict: A dictionary representation of the Chat instance.
        """
        return {
            "provider": self.provider,
            "model": getattr(self, "model", None),
            "system_prompt": self.system_prompt,
            "messages": [
                {"role": msg.role, "content": msg.content, "score": msg.score}
                for msg in self.messages
            ],
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Chat instance from a dictionary.

        Args:
            data (dict): A dictionary representation of the Chat instance.

        Returns:
            Chat: A new Chat instance created from the dictionary data.
        """
        chat = cls(provider=data["provider"], system_prompt=data.get("system_prompt"))
        chat.model = data.get("model")
        for msg in data["messages"]:
            chat.add_message(msg["role"], msg["content"], msg.get("score"))
        return chat

    def add_score_to_last_exchange(self, score: float) -> bool:
        """
        Add score to the last user message in the chat.

        Args:
            score (float): The score to add.

        Returns:
            bool: True if score was added successfully, False otherwise.
        """
        if len(self.messages) < 2:
            self.logger.error("Not enough messages to add score")
            return False

        for msg in reversed(self.messages):
            if msg.role == "user":
                msg.score = score
                self.logger.info(f"Added score {score} to user message")
                return True

        self.logger.error("Unable to find a user message")
        return False


if __name__ == "__main__":
    # chat_ollama = Chat(system_prompt="You must always answer in german")
    # chat_ollama.ask(
    #     "Hello, how are you?",
    #     streamline=True,
    #     temperature=0.1,
    #     repeat_penalty=1.1,
    #     top_k=40,
    #     top_p=0.95,
    # )

    # chat_replicate = Chat(
    #     replicate_model="meta/meta-llama-3-8b-instruct",
    #     system_prompt="You must always answer in german",
    # )
    # chat_replicate.ask(
    #     "Hello, how are you?",
    #     streamline=True,
    #     temperature=0.1,
    #     repeat_penalty=1.1,
    #     top_k=40,
    #     top_p=0.95,
    # )

    # Test with different providers
    providers = ["openai"]
    system_prompt = "You must always answer in German"

    for provider in providers:
        print(f"\nTesting {provider.capitalize()} provider:")
        chat = Chat(provider=provider, system_prompt=system_prompt)
        response = chat.ask(
            "Hello, how are you?",
            streamline=True,
            temperature=0.1,
            repeat_penalty=1.1,
            top_k=40,
            top_p=0.95,
        )
        print(f"{provider.capitalize()} response: {response}\n")

        # Add a score to the last exchange
        chat.add_score_to_last_exchange(0.8)

        # Print the chat history
        print("Chat history:")
        for msg in chat.get_messages():
            print(f"{msg.role}: {msg.content} (Score: {msg.score})")
