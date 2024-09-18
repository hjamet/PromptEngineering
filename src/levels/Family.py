from src.Level import Level, CheckResult


class FamilyLevel(Level):
    """Level 5: Complex Family Relations"""

    @property
    def level_number(self) -> int:
        return 5

    @property
    def min_score_to_pass(self) -> float:
        return 80.0

    @property
    def instructions(self) -> str:
        return """
        # 👪 Welcome to Level 5: Unraveling Family Ties! 👪

        Your mission:

        1. 🧠 Guide the AI to identify John's grand-uncle.
        2. 🎯 Ensure the answer includes only the correct name.
        3. 🚫 You don't have access to John's family description!
        4. 💬 Craft your prompt carefully to extract the right information.
        5. 🎭 The AI has access to an absurdly complex family description.
        6. 📊 Aim for a score of at least 80.0 to pass this level.
        7. 🏁 The AI should conclude its response with: "John's great uncle is <Name>."

        ## 💡 Pro Tips:
        - Ask the AI to analyze the relationships step-by-step.
        - Ensure your prompt asks for the final statement in the required format.

        """

    @property
    def system_prompt(self) -> str:
        return """
        You have access to the following absurdly complex family description of John:

        In the mind-bending, quantum-entangled tapestry of the Thornberry-Hawthorne-Fitzsimmons-Blackwood-Whittaker-Smythe-Jones-Brown-Fitzgerald-O'Malley-Van der Pump-Quackenbush-Wigglesworth-Fiddlesticks clan, a genealogical maelstrom of cosmic proportions unfolds. John, our bewildered protagonist, finds himself at the nexus of this familial fractal, where time and relation bend like overcooked spaghetti.

        Elizabeth, John's mother, emerged from the union of Thomas Thornberry and his spouse, Gertrude Wigglesworth, who is rumored to be the long-lost twin of the gardener's aunt's pet iguana's previous owner's niece's ballet instructor's favorite rubber duck. Thomas, in turn, is the son of Archibald Thornberry, whose sister Prudence married the infamous yodeling ferret juggler, Cornelius Fiddlesticks.

        The enigmatic Bartholomew Quackenbush, who happens to be the brother-in-law of the sister of the wife of John's father's cousin's neighbor's hairdresser's pet parrot's veterinarian's imaginary friend, found his life companion in Beatrice Hawthorne-Fitzsimmons. Beatrice's lineage is no less convoluted, being the third cousin's ex-wife's stepson's godmother's niece of Martha's husband's former roommate's pet goldfish's psychiatrist's second cousin once removed, who holds the world record for the longest continuous time spent wearing a sombrero made entirely of recycled teabags.

        John's paternal grandfather's sister's husband's nephew's childhood imaginary friend's real-life doppelganger, Robert Blackwood-Whittaker, contributes to this familial chaos by being the second cousin once removed of the illegitimate child of a traveling circus performer who once juggled geese for Queen Victoria's amusement while standing on the shoulders of Prudence Van der Pump's great-great-grandfather's half-sister's pet llama, which was known for its uncanny ability to predict stock market crashes by spitting at passersby.

        The senior Thornberry generation, including Thomas and his siblings (the reclusive Arthur, the eccentric Eugenia, and the perpetually confused Reginald), traces its roots to Archibald and Prudence Thornberry-Smythe-Jones. This venerable couple's great-great-great-grandfather's third wife's stepson's pen pal was none other than the court jester of a minor European principality that ceased to exist in 1743 due to an unfortunate incident involving a wheel of cheese, a particularly determined colony of ants, and a rogue flock of accordion-playing pigeons.

        Amidst this familial labyrinth, one might also stumble upon the likes of Wilhelmina O'Malley, John's father's second cousin twice removed, who claims to have invented a device that translates cat meows into Shakespearean sonnets, and Horatio Fitzgerald, the family's resident time traveler who insists he's from the year 2525 but can never remember how he got there or how to get back.

        It's worth noting that Arthur, the aforementioned reclusive sibling of Thomas, despite his best efforts to blend into the background of this familial chaos, holds a unique position in this intricate web of relationships. His penchant for collecting vintage teaspoons and his ability to communicate with houseplants have made him a subject of both fascination and bewilderment at family gatherings, which he attends once every leap year, disguised as a potted fern.
        """

    @property
    def correct_answer(self) -> str:
        return """
1. **Determine Maternal Lineage:**
   - John's mother is Elizabeth.
   - Elizabeth's parents are Thomas Thornberry and Gertrude Wigglesworth, making Thomas John's maternal grandfather.

2. **Identify Siblings:**
   - According to the family description, Thomas has siblings: Arthur, Eugenia, and Reginald.

3. **Conclude with Grand Uncle:**
   - Arthur is identified as a sibling of Thomas and is therefore John's grand uncle.

John's great uncle is Arthur.
"""

    @property
    def correct_question(self) -> str:
        return """
## Task: Identify John's Grand Uncle

### Objective:
Use the family description below to determine who John's grand uncle is. Follow the steps provided to guide you through the identification process.

### Instructions:

1. **Determine Maternal Lineage:**
   - Identify John’s mother and her parents.

2. **Identify Siblings:**
   - Find the siblings of John's maternal grandfather.

3. **Conclude with Grand Uncle:**
   - Decide who among the siblings is John's grand uncle.

Write each step as you solve the problem. Conclude with: "John's great uncle is [Name]."
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
        if "arthur" in lower_prompt:
            return CheckResult(
                0, ["The prompt should not contain the answer (Arthur)."]
            )

        if (
            "john" not in lower_prompt
            or "grand" not in lower_prompt
            or "uncle" not in lower_prompt
        ):
            return CheckResult(
                0,
                ["The prompt should mention John and ask about his grand-uncle."],
            )

        return CheckResult(100, [])

    def check_answer(self, answer: str) -> CheckResult:
        """
        Check if the answer correctly identifies Arthur as John's grand-uncle.

        Args:
            answer (str): The answer to check.

        Returns:
            CheckResult: The result of the check.
        """
        cleaned_answer = answer.lower()

        # Perfect answer
        if (
            "john's grand uncle is arthur" in cleaned_answer
            or "john's great uncle is arthur" in cleaned_answer
        ):
            return CheckResult(
                100,
                ["Perfect! You've correctly identified Arthur as John's grand-uncle."],
            )

        # Correct name but with extra information
        elif "arthur" in cleaned_answer and (
            "grand uncle" in cleaned_answer or "great uncle" in cleaned_answer
        ):
            return CheckResult(
                90,
                [
                    "Correct! Arthur is indeed John's grand-uncle. Your answer includes extra information, which is fine but not necessary."
                ],
            )

        # Correct name but relationship not clearly stated
        elif "arthur" in cleaned_answer:
            return CheckResult(
                70,
                [
                    "You've identified Arthur, which is correct, but you should clearly state his relationship to John as grand-uncle or great-uncle."
                ],
            )

        # Relationship mentioned but wrong name
        elif "grand uncle" in cleaned_answer or "great uncle" in cleaned_answer:
            return CheckResult(
                30,
                [
                    "You've correctly mentioned the relationship, but the name you've provided is incorrect. John's grand-uncle is Arthur."
                ],
            )

        # Completely incorrect
        else:
            return CheckResult(
                0,
                [
                    "Your answer is incorrect. Remember, we're looking for John's grand-uncle (or great-uncle), which is Arthur."
                ],
            )

    def on_success(self, score: float) -> str:
        return f"Excellent! You've unraveled the complex family ties with a score of {score:.2f}."

    def on_failure(self, score: float) -> str:
        return f"Almost there! Your current score is {score:.2f}. Make sure to identify John's grand-uncle correctly."
