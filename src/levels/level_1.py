from src.Level import Level, CheckResult, LevelResult


class Level1(Level):
    @property
    def level_number(self) -> int:
        return 1

    @property
    def instructions(self) -> str:
        return """
        # Welcome to Level 1!
        
        Your task is simple:
        
        1. Ask the AI to respond with **anything**
        2. Make sure the response is **less than 30 words**
        """

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the answer is less than 30 words.

        Args:
            answer (str): The answer to check.

        Returns:
            CheckResult: The result of the check.
        """
        word_count = len(answer.split())
        if word_count < 30:
            return CheckResult(100, [])
        return CheckResult(
            0, [f"The response has {word_count} words. It should be less than 30."]
        )

    def on_success(self, score: float) -> str:
        return "Well done! Okay, this level wasn't particularly challenging, but let's make things a bit more complex..."

    def on_failure(self, score: float) -> str:
        return f"Almost there! You're at {score:.2f} points. Just a little more effort to reach 90 points!"
