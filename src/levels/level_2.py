from src.Level import Level, CheckResult, LevelResult


class Level2(Level):
    @property
    def level_number(self) -> int:
        return 2

    @property
    def instructions(self) -> str:
        return """
        # Welcome to Level 2!
        
        Your task for this level is to make the AI respond with **exactly** the following phrase:
        
        ```
        This is my answer
        ```
        
        Nothing more, nothing less.
        
        ## Tips:
        - Be **very specific** in your instructions
        - Think about how to phrase your request to get an *exact* response
        - Remember, any deviation from the exact phrase will **not** be considered correct
        """

    def check_answer(self, answer: str) -> CheckResult:
        if answer.strip() == "This is my answer":
            return CheckResult(100, [])
        return CheckResult(
            0,
            [
                f"The response should be exactly 'This is my answer'. Got: '{answer[:min(100, len(answer))]}'"
            ],
        )

    def on_success(self, score: float) -> str:
        return "Not bad! This one was a bit more challenging, and you handled it like a pro!"

    def on_failure(self, score: float) -> str:
        return f"Close, but not quite there! Your score is {score:.2f}. Remember, precision is key in this level!"
