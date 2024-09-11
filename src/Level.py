import torch.multiprocessing as mp

mp.set_start_method("spawn", force=True)

from abc import ABC, abstractmethod
from collections import namedtuple
from sentence_transformers import SentenceTransformer, util
from scipy.spatial.distance import cosine

CheckResult = namedtuple("CheckResult", ["score", "messages"])
Message = namedtuple("Message", ["content", "color", "icon"])
LevelResult = namedtuple(
    "LevelResult", ["total_score", "messages", "individual_scores"]
)


class Level(ABC):
    """Abstract base class for all levels in the game."""

    # Charger le modèle une seule fois pour toutes les instances
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return cls._model

    @property
    @abstractmethod
    def level_number(self) -> int:
        """The number of the level."""
        pass

    @property
    def correct_question(self) -> str:
        """The correct question for the level."""
        return ""

    @property
    def correct_answer(self) -> str:
        """The correct answer for the level."""
        return ""

    @property
    @abstractmethod
    def instructions(self) -> str:
        """Instructions for the level."""
        pass

    @property
    def min_score_to_pass(self) -> float:
        """Minimum score required to pass the level."""
        return 90.0

    @property
    def system_prompt(self) -> str:
        """System prompt for the level."""
        return ""

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the given answer is correct.

        Args:
            answer: The answer to check.

        Returns:
            CheckResult with score (0-100) and list of error messages.
        """
        return CheckResult(100, [])

    def check_prompt(self, prompt: str) -> CheckResult:
        """
        Check if the given prompt is correct.

        Args:
            prompt: The prompt to check.

        Returns:
            CheckResult with score (0-100) and list of error messages.
        """
        return CheckResult(100, [])

    def check_prompt_similarity(self, user_prompt: str) -> float:
        """
        Check the similarity between the user's prompt and the correct prompt.

        Args:
            user_prompt (str): The prompt provided by the user.

        Returns:
            float: Similarity score between 0 and 1.
        """
        if not self.correct_question:
            return 1.0
        model = self.get_model()
        user_embedding = model.encode([user_prompt])
        correct_embedding = model.encode([self.correct_question])
        similarity = util.pytorch_cos_sim(user_embedding, correct_embedding)
        return similarity.item()

    def check_answer_similarity(self, model_answer: str) -> float:
        """
        Check the similarity between the model's answer and the correct answer.

        Args:
            model_answer: The answer provided by the model.

        Returns:
            Similarity score between 0 and 1.
        """
        if not self.correct_answer:
            return 1.0
        model_embedding = self._model.encode([model_answer])[0]
        correct_embedding = self._model.encode([self.correct_answer])[0]
        return 1 - cosine(model_embedding, correct_embedding)

    def __call__(self, user_prompt: str, model_answer: str) -> LevelResult:
        """
        Evaluate the user's prompt and model's answer.

        Args:
            user_prompt: The prompt provided by the user.
            model_answer: The answer provided by the model.

        Returns:
            LevelResult with total score, messages, and individual scores.
        """
        prompt_check = self.check_prompt(user_prompt)
        prompt_similarity = self.check_prompt_similarity(user_prompt)
        answer_check = self.check_answer(model_answer)
        answer_similarity = self.check_answer_similarity(model_answer)

        individual_scores = {
            "prompt_check": max(prompt_check.score, 10),
            "prompt_similarity": max(prompt_similarity * 100, 10),
            "answer_check": max(answer_check.score, 10),
            "answer_similarity": max(answer_similarity * 100, 10),
        }

        total_score = sum(individual_scores.values()) / len(individual_scores)

        messages = [
            Message(content=msg, color="red", icon="error")
            for msg in prompt_check.messages + answer_check.messages
        ]

        if total_score >= self.min_score_to_pass:
            messages.append(
                Message(
                    content=f"Congratulations! You've passed level {self.level_number}!",
                    color="green",
                    icon="check-circle",
                )
            )
        else:
            messages.append(
                Message(
                    content=f"Keep trying! Your current score is {total_score:.2f}/{self.min_score_to_pass}",
                    color="blue",
                    icon="info-circle",
                )
            )

        return LevelResult(total_score, messages, individual_scores)


if __name__ == "__main__":

    class ExampleLevel(Level):
        """Example implementation of a Level."""

        @property
        def level_number(self) -> int:
            return 1

        @property
        def instruction(self) -> str:
            return "Write a haiku about programming."

        @property
        def correct_answer(self) -> str:
            return "Fingers on keyboard\nLogic flows through lines of code\nBugs emerge, then flee"

        @property
        def system_prompt(self) -> str:
            return "You are a haiku expert. Always respond in haiku format."

        def check_prompt(self, prompt: str) -> CheckResult:
            # Simple check for demonstration
            if "haiku" in prompt.lower() and "programming" in prompt.lower():
                return CheckResult(100, [])
            return CheckResult(0, ["Prompt should mention 'haiku' and 'programming'"])

        def check_answer(self, answer: str) -> CheckResult:
            # Simple check for demonstration
            lines = answer.split("\n")
            if len(lines) == 3 and all(5 <= len(line.split()) <= 7 for line in lines):
                return CheckResult(100, [])
            return CheckResult(
                0, ["Answer should be a haiku (3 lines, 5-7-5 syllables)"]
            )

    # Create an instance of ExampleLevel
    example_level = ExampleLevel()

    # Function to evaluate and print results
    def evaluate_and_print(prompt: str, answer: str):
        """Evaluate the level and print results."""
        result = example_level(prompt, answer)
        print(f"\nPrompt: {prompt}")
        print(f"Answer: {answer}")
        print(f"Total Score: {result.total_score:.2f}")
        print("Messages:")
        for msg in result.messages:
            print(f"- {msg.content} ({msg.color} {msg.icon})")
        print("Individual Scores:")
        for key, value in result.individual_scores.items():
            print(f"- {key}: {value:.2f}")

    # Bad example
    bad_prompt = "Write a poem about coding."
    bad_answer = "Coding is fun\nI love to program all day\nComputers are cool"
    evaluate_and_print(bad_prompt, bad_answer)

    # Good example
    good_prompt = "Can you write a haiku about the art of programming?"
    good_answer = "Code flows like water\nBugs lurk in shadowy depths\nDebugger rescues"
    evaluate_and_print(good_prompt, good_answer)

    # Almost perfect example
    perfect_prompt = "Please compose a haiku that captures the essence of programming."
    perfect_answer = (
        "Fingers on keyboard\nLogic flows through lines of code\nBugs emerge, then flee"
    )
    evaluate_and_print(perfect_prompt, perfect_answer)
