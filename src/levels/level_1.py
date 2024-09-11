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

    @property
    def correct_question(self) -> str:
        return "Please provide a response on any topic, but keep it under 30 words."

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
