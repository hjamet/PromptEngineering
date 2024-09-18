from src.Level import Level, CheckResult


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
        # 🧮 Welcome to Level 3: The Fibonacci Sequence Challenge! 🧮

        Alright, number enthusiast, here's your exciting mission:

        1. 🔢 Guide our AI companion to calculate the 21st term of the Fibonacci sequence.
        2. 🎯 Ensure the answer includes the correct number. It's our star of the show!
        3. 🚫 Keep it precise - no numbers larger than the result should appear in the response.
        4. 🧠 No cheating: the AI should do the calculation, not you!

        ## 💡 Pro Tip:
        - Encourage a step-by-step calculation approach. It's not just about the final answer, but the journey to get there!
        """

    @property
    def correct_question(self) -> str:
        return """Please calculate the 21st term of the Fibonacci sequence. Follow these steps:
1. Start with the first two terms: 0 and 1.
2. Calculate each subsequent term by adding the two preceding terms.
3. Continue this process until you reach the 21st term.
4. Provide the final result and show your work.
Remember, the Fibonacci sequence starts with 0 and 1, and each number afterwards is the sum of the two preceding ones."""

    @property
    def correct_answer(self) -> str:
        return """
The Fibonacci sequence is a sequence of numbers where each term is the sum of the two preceding terms, typically with the first initial value defined as 0 (F(0) = 0) and the second initial value being 1 (F(1) = 1). This process is repeated for each subsequent term: the preceding term is added to the one that preceded it.

Step 1: Calculate F(2)

Using the given values of F(0) and F(1), we calculate F(2) as follows:

F(2) = F(1) + F(0) = 1 + 0 = 1

Step 2: Calculate F(3)

We now add the previous term (which is F(2)) to F(1) to find F(3) :

F(3) = F(2) + F(1) = 1 + 1 = 2

Step 3: Calculate F(4)

Now we take F(3), which is the previous term, and add it to F(2) to calculate F(4) :

F(4) = F(3) + F(2) = 2 + 1 = 3

Step 4: Calculate F(5)

Following the same logic, we now add F(4), which is the previous term, to F(3) to find F(5) :

F(5) = F(4) + F(3) = 3 + 2 = 5

Step 5: Calculate F(6)

To obtain F(6), we now add F(5), the previous term, to F(4) :

F(6) = F(5) + F(4) = 5 + 3 = 8

Step 6: Calculate F(7)

Continuing this process, we now add the previous term (which is F(6)) to F(5) to find F(7) :

F(7) = F(6) + F(5) = 8 + 5 = 13

Step 7: Calculate F(8)

To obtain F(8), we now add the previous term (which is F(7)) to F(6) :

F(8) = F(7) + F(6) = 13 + 8 = 21

Step 8: Calculate F(9)

Continuing, we now add the previous term (which is F(8)) to F(7) to find F(9) :

F(9) = F(8) + F(7) = 21 + 13 = 34

Step 9: Calculate F(10)

To obtain F(10), we now add the previous term (which is F(9)) to F(8) :

F(10) = F(9) + F(8) = 34 + 21 = 55

Step 10: Calculate F(11)

Continuing this process, we now add the previous term (which is F(10)) to F(9) to find F(11) :

F(11) = F(10) + F(9) = 55 + 34 = 89

Step 11: Calculate F(12)

To obtain F(12), we now add the previous term (which is F(11)) to F(10) :

F(12) = F(11) + F(10) = 89 + 55 = 144

Step 12: Calculate F(13)

Continuing, we now add the previous term (which is F(12)) to F(11) to find F(13) :

F(13) = F(12) + F(11) = 144 + 89 = 233

Step 13: Calculate F(14)

To obtain F(14), we now add the previous term (which is F(13)) to F(12) :

F(14) = F(13) + F(12) = 233 + 144 = 377

Step 14: Calculate F(15)

Continuing this process, we now add the previous term (which is F(14)) to F(13) to find F(15) :

F(15) = F(14) + F(13) = 377 + 233 = 610

Step 15: Calculate F(16)

To obtain F(16), we now add the previous term (which is F(15)) to F(14) :

F(16) = F(15) + F(14) = 610 + 377 = 987

Step 16: Calculate F(17)

Continuing, we now add the previous term (which is F(16)) to F(15) to find F(17) :

F(17) = F(16) + F(15) = 987 + 610 = 1597

Step 17: Calculate F(18)

To obtain F(18), we now add the previous term (which is F(17)) to F(16) :

F(18) = F(17) + F(16) = 1597 + 987 = 2584

Step 18: Calculate F(19)

Continuing this process, we now add the previous term (which is F(18)) to F(17) to find F(19) :

F(19) = F(18) + F(17) = 2584 + 1597 = 4181

Step 19: Calculate F(20)

To obtain F(20), we now add the previous term (which is F(19)) to F(18) :

F(20) = F(19) + F(18) = 4181 + 2584 = 6765

Step 20: Calculate F(21)

Finally, to find the 21st term of the Fibonacci sequence, we now add the previous term (which is F(20)) to F(19) :

F(21) = F(20) + F(19) = 6765 + 4181 = 10946

The 21st term of the Fibonacci sequence is therefore :

10946.

This exercise helps you understand the evolution of a well-known sequence, and each step demonstrates the logical process of adding the two previous terms to obtain the next term.
"""

    def check_prompt(self, prompt: str) -> CheckResult:
        """
        Check if the prompt is correct and doesn't contain the answer.

        Args:
            prompt (str): The prompt to check.

        Returns:
            CheckResult: The result of the check.
        """
        lower_prompt = prompt.lower()
        if "10946" in lower_prompt:
            return CheckResult(0, ["The prompt should not contain the answer (10946)."])

        if "fibonacci" not in lower_prompt or "21" not in lower_prompt:
            return CheckResult(
                0,
                ["The prompt should mention the Fibonacci sequence and the 21st term."],
            )

        return CheckResult(100, [])

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the answer contains 10946 and no larger numbers.

        Args:
            answer (str): The answer to check.

        Returns:
            CheckResult: The result of the check.
        """
        numbers = [int(n) for n in answer.split() if n.isdigit()]
        if 10946 in numbers and all(n <= 10946 for n in numbers):
            return CheckResult(100, [])
        elif 10946 not in numbers:
            return CheckResult(0, ["Damned ! The 21st Fibonacci number is missing !"])
        else:
            return CheckResult(
                0, ["Hum...The answer contains numbers larger than 10946."]
            )

    def on_success(self, score: float) -> str:
        return f"Excellent! You've mastered the Fibonacci sequence challenge with a score of {score:.2f}."

    def on_failure(self, score: float) -> str:
        return f"Almost there! Your current score is {score:.2f}. Make sure to include the correct 21st Fibonacci number (10946) and no larger numbers."
