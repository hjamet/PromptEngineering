from abc import ABC, abstractmethod
from typing import NamedTuple, List
from collections import namedtuple
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

CheckResult = namedtuple("CheckResult", ["score", "error_messages"])
LevelResult = namedtuple(
    "LevelResult", ["total_score", "messages", "individual_scores"]
)


class Level(ABC):
    """Abstract base class for all levels in the game."""

    # Charger le modèle une seule fois pour toutes les instances
    _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    @property
    @abstractmethod
    def level_number(self) -> int:
        """The number of the level."""
        pass

    @property
    @abstractmethod
    def instruction(self) -> str:
        """The instruction for the level."""
        pass

    @property
    @abstractmethod
    def correct_answer(self) -> str:
        """The correct answer for the level."""
        pass

    @property
    @abstractmethod
    def instructions(self) -> str:
        """Instructions for the level."""
        pass

    @abstractmethod
    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the given answer is correct.

        Args:
            answer: The answer to check.

        Returns:
            CheckResult with score (0-100) and list of error messages.
        """
        pass

    @abstractmethod
    def check_prompt(self, prompt: str) -> CheckResult:
        """
        Check if the given prompt is correct.

        Args:
            prompt: The prompt to check.

        Returns:
            CheckResult with score (0-100) and list of error messages.
        """
        pass

    def check_prompt_similarity(self, user_prompt: str) -> float:
        """
        Check the similarity between the user's prompt and the correct prompt.

        Args:
            user_prompt: The prompt provided by the user.

        Returns:
            Similarity score between 0 and 1.
        """
        user_embedding = self._model.encode([user_prompt])[0]
        correct_embedding = self._model.encode([self.instruction])[0]
        return 1 - cosine(user_embedding, correct_embedding)

    def check_answer_similarity(self, model_answer: str) -> float:
        """
        Check the similarity between the model's answer and the correct answer.

        Args:
            model_answer: The answer provided by the model.

        Returns:
            Similarity score between 0 and 1.
        """
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
            "prompt_check": prompt_check.score,
            "prompt_similarity": prompt_similarity * 100,
            "answer_check": answer_check.score,
            "answer_similarity": answer_similarity * 100,
        }

        total_score = sum(individual_scores.values()) / len(individual_scores)

        messages = (
            prompt_check.error_messages
            + answer_check.error_messages
            + [f"Prompt similarity: {prompt_similarity:.2f}"]
            + [f"Answer similarity: {answer_similarity:.2f}"]
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
            print(f"- {msg}")
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
