from src.Level import Level, CheckResult
import re


class FibonacciLevel(Level):
    @property
    def level_number(self) -> int:
        return 3

    @property
    def min_score_to_pass(self) -> float:
        return 77.0

    @property
    def instructions(self) -> str:
        return """
        # 🧮 Welcome to Level 3: The Modified Fibonacci Sequence Challenge! 🧮

        Let's define our special sequence:
        - It starts with 0 and 3
        - Each subsequent number is the sum of the two preceding ones

        Your mission, should you choose to accept it:

        1. 🔢 Guide our AI buddy to calculate the 21st term of this sequence.
        2. 🎯 Make sure the correct answer is included. It's the star of our math show!
        3. 🧠 The AI should do the math, not you. No sneaky calculators allowed!

        ## 💡 Pro Tip:
        Encourage a step-by-step approach. We want to see the journey, not just the destination!
        """

    @property
    def correct_question(self) -> str:
        return """## AI Assistant Task

We have a mathematical task involving a modified sequence similar to the Fibonacci sequence. Here are the details:

### Fibonacci Sequence Definition:
The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones, usually starting with 0 and 1.

### Modified Sequence Definition:

- Starts with 0 and 3.
- Each subsequent term is the sum of the two preceding terms.

### Your Objectives:

1. Calculate the 21st term of this sequence.
2. Show all terms from the 1st to the 21st, following the format of the example below.
3. Explain briefly how this sequence differs from the traditional Fibonacci sequence.

### Example of Response Format:

Only include the calculations, one term per line, without any explanation:

---
1st term: 0  
2nd term: 3  
3rd term: 3 (0 + 3)  
4th term: 6 (3 + 3)  
...
21st term: [value] ([previous term] + [term before that])
---

Continue this pattern until you reach the 21st term. Make sure to include the calculation in parentheses for each term starting from the 3rd.
"""

    @property
    def correct_answer(self) -> str:
        return """To calculate the 21st term of this modified sequence, where we start with 0 and 3 and each subsequent term is the sum of the two preceding terms, let's work through it step-by-step:

Step-by-Step Calculation:
Initial Terms:

Term 1: 0
Term 2: 3
Subsequent Terms Calculation:

Term 3: 0 + 3 = 3
Term 4: 3 + 3 = 6
Term 5: 3 + 6 = 9
Term 6: 6 + 9 = 15
Term 7: 9 + 15 = 24
Term 8: 15 + 24 = 39
Term 9: 24 + 39 = 63
Term 10: 39 + 63 = 102
Term 11: 63 + 102 = 165
Term 12: 102 + 165 = 267
Term 13: 165 + 267 = 432
Term 14: 267 + 432 = 699
Term 15: 432 + 699 = 1131
Term 16: 699 + 1131 = 1830
Term 17: 1131 + 1830 = 2961
Term 18: 1830 + 2961 = 4791
Term 19: 2961 + 4791 = 7752
Term 20: 4791 + 7752 = 12543
Term 21: 7752 + 12543 = 20295
Explanation of the Sequence Difference:
This sequence is similar to the Fibonacci sequence, with each term being the sum of the two preceding terms. However, it differs from the traditional Fibonacci sequence in its initial terms. The traditional Fibonacci sequence starts with 0 and 1, whereas this modified sequence starts with 0 and 3. This change in initial terms alters all subsequent terms in the sequence."""

    def check_prompt(self, prompt: str) -> CheckResult:
        """
        Check if the prompt is correct and doesn't contain the answer.

        Args:
            prompt (str): The prompt to check.

        Returns:
            CheckResult: The result of the check.
        """
        lower_prompt = prompt.lower()
        if "20295" in lower_prompt:
            return CheckResult(0, ["The prompt should not contain the answer."])

        if (
            "fibonacci" not in lower_prompt
            or "21" not in lower_prompt
            or "1" not in lower_prompt
            or "3" not in lower_prompt
        ):
            return CheckResult(
                0,
                [
                    "The prompt should mention the modified Fibonacci sequence starting with 1 and 3, and ask for the 21st term."
                ],
            )

        return CheckResult(100, [])

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the answer contains the 21st term of the modified Fibonacci sequence and no larger numbers.

        Args:
            answer (str): The answer to check.

        Returns:
            CheckResult: The result of the check.
        """
        # Extract numbers from the answer, including those in markdown or adjacent to other characters
        numbers = [int(n) for n in re.findall(r"\d+", answer)]

        if 20295 in numbers and all(n <= 20295 for n in numbers):
            return CheckResult(100, [])
        elif 20295 not in numbers:
            return CheckResult(
                0,
                [
                    "Damned! The 21st term of the modified Fibonacci sequence is missing!"
                ],
            )
        else:
            return CheckResult(
                0, ["Hum...The answer contains numbers larger than the 21st term."]
            )

    def on_success(self, score: float) -> str:
        return f"Excellent! You've mastered the modified Fibonacci sequence challenge with a score of {score:.2f}."

    def on_failure(self, score: float) -> str:
        return f"Almost there! Your current score is {score:.2f}. Make sure to include the correct 21st term of the modified Fibonacci sequence (20295) and no larger numbers."
