from src.Level import Level, CheckResult, LevelResult


class ChatterboxLevel(Level):
    @property
    def level_number(self) -> int:
        return 1

    @property
    def instructions(self) -> str:
        return """
        # 🎉 Welcome to Level 1: The Chatterbox Challenge! 🎉

        ## 🚨 Important Notes Before You Start:

        1. The model may have a system prompt that you can't access.
        2. The model has no memory - it doesn't remember your previous questions!
        3. We're using a smaller model than GPT-4, so expect lower performance. This is good because:
           - It makes the game more challenging (we're a bit evil 😈)
           - Techniques that work on small models will work even better on larger ones!
           - It keeps the game from being too easy 😉

        Alright, AI whisperer, here's your mission:

        1. 🗣️ Get our AI buddy to say **literally anything**. Yep, anything at all!
        2. 🤏 But here's the twist: keep it snappy! The response should be **under 30 words**.

        ## 💡 Pro Tips:
        - This is your warm-up lap. Easy peasy lemon squeezy!
        - Remember, brevity is the soul of wit (and passing this level)!

        Good luck, and let the prompt engineering begin!
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
