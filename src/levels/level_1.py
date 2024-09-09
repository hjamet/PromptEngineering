from src.Level import Level, CheckResult, LevelResult


class Level1(Level):
    @property
    def level_number(self) -> int:
        return 1

    @property
    def instructions(self) -> str:
        return """
        Welcome to Level 1!
        
        Your task is simple: Ask the AI to respond with anything, but make sure the response is less than 30 words.
        
        Tips:
        - Be clear in your request
        - You can be creative with your prompt
        - Remember, the AI's response should be concise
        """

    def check_prompt(self, prompt: str) -> CheckResult:
        if "less than 30 words" in prompt.lower() or "under 30 words" in prompt.lower():
            return CheckResult(100, [])
        return CheckResult(
            0, ["Your prompt should specify a response of less than 30 words"]
        )

    def check_answer(self, answer: str) -> CheckResult:
        word_count = len(answer.split())
        if word_count < 30:
            return CheckResult(100, [])
        return CheckResult(
            0, [f"The response has {word_count} words. It should be less than 30."]
        )
