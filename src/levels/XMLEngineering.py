from src.Level import Level, CheckResult
import re
from xml.etree import ElementTree as ET


class XMLEngineeringLevel(Level):
    @property
    def level_number(self) -> int:
        return 4

    @property
    def min_score_to_pass(self) -> float:
        return 90.0

    @property
    def instructions(self) -> str:
        return """
        # 🏗️ Welcome to Level 4: XML Engineering for Prompt Crafting! 🏗️

        Did you know that using XML tags in prompts can significantly enhance the structure and clarity of your instructions to AI models? Similar to Markdown, XML tags help organize different components of your prompt, leading to more accurate and higher-quality outputs.

        In this level, you'll use XML tags to structure your prompts and control the AI's output.

        Your mission:

        1. 📝 Create a prompt using XML tags to instruct the AI to write a short story.
        2. 🏷️ Use XML tags to specify two lists of words:
           - Words that MUST be included in the story: butterfly, moonlight, whisper, adventure, dream
           - Words that MUST NOT be used in the story: the, and, a, is, was
        3. 🎭 Include tags for `<character>`, `<setting>`, and `<genre>`.
        4. 🔍 Ensure your XML is well-formed (properly nested and closed tags).

        ## 💡 Pro Tips:
        - XML tags help separate different parts of your prompt, preventing the AI from mixing up instructions with examples or context.
        - Use consistent tag names throughout your prompt for clarity.
        - Nest tags for hierarchical content: `<outer><inner></inner></outer>`.
        - This technique is particularly effective for models like Claude.

        To learn more about using XML in prompt engineering, check out this guide: [Use XML tags to structure your prompts](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags).

        Be creative and precise in your prompt crafting!
        """

    def check_prompt(self, prompt: str) -> CheckResult:
        try:
            root = ET.fromstring(prompt)
        except ET.ParseError:
            return CheckResult(
                0,
                [
                    "The XML in your prompt is not well-formed. Please check for proper nesting and closing of tags."
                ],
            )

        required_tags = [
            "character",
            "setting",
            "genre",
            "include_words",
            "exclude_words",
        ]
        found_tags = [elem.tag.lower() for elem in root.iter()]

        missing_tags = [tag for tag in required_tags if tag not in found_tags]
        if missing_tags:
            return CheckResult(
                50,
                [
                    f"Your prompt is missing the following required tags: {', '.join(missing_tags)}"
                ],
            )

        include_words = root.find("include_words")
        exclude_words = root.find("exclude_words")

        if include_words is None or exclude_words is None:
            return CheckResult(
                75,
                [
                    "Make sure you have both <include_words> and <exclude_words> tags in your prompt."
                ],
            )

        if len(include_words.text.split()) != 5 or len(exclude_words.text.split()) != 5:
            return CheckResult(
                75,
                [
                    "Both <include_words> and <exclude_words> should contain exactly 5 words each."
                ],
            )

        return CheckResult(
            100,
            [
                "Great job! Your XML prompt is well-structured and includes all required elements."
            ],
        )

    def check_answer(self, answer: str) -> CheckResult:
        root = ET.fromstring(self.last_prompt)
        include_words = root.find("include_words").text.lower().split()
        exclude_words = root.find("exclude_words").text.lower().split()

        answer_lower = answer.lower()
        included_count = sum(word in answer_lower for word in include_words)
        excluded_count = sum(word in answer_lower for word in exclude_words)

        score = (included_count / 5) * 50 + ((5 - excluded_count) / 5) * 50
        messages = []

        if included_count < 5:
            messages.append(
                f"The story is missing {5 - included_count} required words."
            )
        if excluded_count > 0:
            messages.append(
                f"The story contains {excluded_count} words that should have been excluded."
            )

        if not messages:
            messages.append(
                "The AI's response correctly includes and excludes the specified words."
            )

        return CheckResult(score, messages)

    def on_success(self, score: float) -> str:
        return f"Excellent work! You've mastered XML prompt engineering with a score of {score:.2f}. Your structured prompts effectively controlled the AI's output."

    def on_failure(self, score: float) -> str:
        return f"Nice try! Your current score is {score:.2f}. Make sure to include all required XML tags and effectively control the words used in the AI's response. Keep practicing your XML prompt engineering skills!"
