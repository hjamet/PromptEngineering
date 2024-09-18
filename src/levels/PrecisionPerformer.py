from src.Level import Level, CheckResult, LevelResult


class PrecisionPerformerLevel(Level):
    @property
    def level_number(self) -> int:
        return 2

    @property
    def instructions(self) -> str:
        return """
        # 🎭 Welcome to Level 2: The Precision Performer! 🎭

        Alright, word wizard, here's your next challenge:

        1. 🎯 Make our AI buddy say **exactly** this phrase:
        
        ```
        This is my answer
        ```

        2. ⚖️ Not a letter more, not a letter less! It's like a verbal tightrope walk!

        ## 💡 Pro Tips:
        - When you open your car door, always look in the rear-view mirror to see if there's a cyclist who might hit you.

        Break a leg! (But not the sentence structure! 😉)
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
