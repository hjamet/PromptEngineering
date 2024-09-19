from src.Level import Level, CheckResult
import re


class MarkdownFormattingLevel(Level):
    """Level focused on Markdown formatting skills."""

    @property
    def level_number(self) -> int:
        return 3

    @property
    def min_score_to_pass(self) -> float:
        return 85.0

    @property
    def instructions(self) -> str:
        return """
        # 📝 Welcome to Level 3: Markdown Mastery! 📝

        Did you know that language models are often trained to respond in a language called Markdown? It's what manages the formatting of the response (like headings, bold, italic, links, etc.). For example, when you use ChatGPT and ask a question, the model will respond in Markdown, making the content more interesting and readable than plain text!

        Your mission:

        1. 🔍 Research Markdown syntax if you're not familiar with it.
        2. 📊 Create a prompt using Markdown to structure your request.
        3. 🎭 Ask the AI to respond with Markdown formatting.
        4. 💻 Request the AI to wrap its entire response in a code block.

        ## 💡 Pro Tips:
        - When models use tools (like DALL-E-3 for images or graph display), they simply incorporate a code block in their response describing what the tool should do!
        - Markdown is incredibly simple and practical for taking notes quickly. Learn more about Markdown syntax here: [Markdown Guide](https://www.markdownguide.org/basic-syntax/)

        Good luck, Markdown maestro!
        """

    def check_prompt(self, prompt: str) -> CheckResult:
        """
        Check if the prompt contains Markdown elements.

        Args:
            prompt (str): The user's prompt.

        Returns:
            CheckResult: The result of the check.
        """
        markdown_elements = [
            r"#{1,6}\s",  # Headers
            r"\*\*.+?\*\*",  # Bold
            r"_.+?_",  # Italic
            r"\[.+?\]\(.+?\)",  # Links
            r"```[\s\S]*?```",  # Code blocks
            r"- ",  # Unordered list
            r"\d+\. ",  # Ordered list
        ]

        score = sum(bool(re.search(pattern, prompt)) for pattern in markdown_elements)
        score = 20 + min(score * 20, 80)  # 20 points per element, max 100

        if score < 60:
            return CheckResult(
                score, ["Your prompt should use more Markdown elements."]
            )
        return CheckResult(score, ["Good use of Markdown in your prompt!"])

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the answer is entirely within a code block and contains Markdown.

        Args:
            answer (str): The AI's answer.

        Returns:
            CheckResult: The result of the check.
        """
        if not re.match(r"^\s*```[\s\S]*```\s*$", answer):
            return CheckResult(0, ["The entire response should be in a code block."])

        markdown_content = re.search(r"```([\s\S]*)```", answer)
        if not markdown_content:
            return CheckResult(0, ["No content found in the code block."])

        markdown_elements = [
            r"#{1,6}\s",  # Headers
            r"\*\*.+?\*\*",  # Bold
            r"_.+?_",  # Italic
            r"\[.+?\]\(.+?\)",  # Links
            r"- ",  # Unordered list
            r"\d+\. ",  # Ordered list
        ]

        score = sum(
            bool(re.search(pattern, markdown_content.group(1)))
            for pattern in markdown_elements
        )
        score = 20 + min(score * 20, 80)  # 20 points per element, max 100

        if score < 60:
            return CheckResult(
                score, ["The response should include more Markdown elements."]
            )
        return CheckResult(score, ["Great use of Markdown in the response!"])

    def on_success(self, score: float) -> str:
        return f"Bravo! You've mastered Markdown formatting with a score of {score:.2f}. Your structured prompts effectively guided the AI's output."

    def on_failure(self, score: float) -> str:
        return f"Nice try! Your current score is {score:.2f}. Make sure to use various Markdown elements in your prompt and check that the AI's response is in a code block with Markdown content. Keep practicing your Markdown skills!"
