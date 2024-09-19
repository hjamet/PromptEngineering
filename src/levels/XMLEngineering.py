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
           - Words that MUST NOT be used in the story: wing, night, voice, journey, sleep
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
        """
        Check if the prompt contains required XML tags and words.

        Args:
            prompt (str): The user's prompt.

        Returns:
            CheckResult: The result of the check.
        """
        try:
            root = ET.fromstring(prompt)
        except ET.ParseError:
            return CheckResult(0, ["Malformed XML. Check your tags."])

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
            return CheckResult(50, [f"Missing tags: {', '.join(missing_tags)}"])

        expected_words = {
            "include": ["butterfly", "moonlight", "whisper", "adventure", "dream"],
            "exclude": ["wing", "night", "voice", "journey", "sleep"],
        }

        missing_words = []
        for word in expected_words["include"] + expected_words["exclude"]:
            if not re.search(r"\b" + re.escape(word) + r"\b", prompt.lower()):
                missing_words.append(word)

        if missing_words:
            return CheckResult(0, [f"Missing words: {', '.join(missing_words)}"])

        return CheckResult(100, ["Well-structured XML with all required elements."])

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the answer contains required words and excludes forbidden words.

        Args:
            answer (str): The AI's answer.

        Returns:
            CheckResult: The result of the check.
        """
        include_words = ["butterfly", "moonlight", "whisper", "adventure", "dream"]
        exclude_words = ["wing", "night", "voice", "journey", "sleep"]

        answer_lower = answer.lower()
        included_words = []
        excluded_words = []

        for word in include_words:
            if not re.search(r"\b" + re.escape(word) + r"\b", answer_lower):
                included_words.append(word)
        for word in exclude_words:
            if re.search(r"\b" + re.escape(word) + r"\b", answer_lower):
                excluded_words.append(word)

        included_count = len(include_words) - len(included_words)
        excluded_count = len(excluded_words)

        score = (included_count / len(include_words)) * 50 + (
            (len(exclude_words) - excluded_count) / len(exclude_words)
        ) * 50
        messages = []

        if included_words:
            messages.append(
                f"{len(included_words)} required words missing: {', '.join(included_words)}"
            )
        if excluded_words:
            messages.append(
                f"{excluded_count} excluded words present: {', '.join(excluded_words)}"
            )

        if not messages:
            messages.append("Correct response with included/excluded words.")

        return CheckResult(score, messages)

    def on_success(self, score: float) -> str:
        return f"Excellent work! You've mastered XML prompt engineering with a score of {score:.2f}. Your structured prompts effectively controlled the AI's output."

    def on_failure(self, score: float) -> str:
        return f"Nice try! Your current score is {score:.2f}. Make sure to include all required XML tags and effectively control the words used in the AI's response. Keep practicing your XML prompt engineering skills!"
