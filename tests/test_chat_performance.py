import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multiprocessing
import time
import random
from statistics import mean, median, stdev
from src.Chat import Chat, start_ollama_server
import tiktoken
from datetime import datetime


def count_tokens(text):
    """Count the number of tokens in a given text."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def simulate_user_session(user_id, num_questions):
    """
    Simule une session utilisateur avec plusieurs requêtes.

    Args:
        user_id (int): Identifiant de l'utilisateur.
        num_questions (int): Nombre de questions à poser.

    Returns:
        list: Liste des temps de réponse et nombre de tokens pour chaque requête.
    """
    chat = Chat()
    results = []
    questions = [
        "Explain the concept of quantum computing.",
        "What are the main differences between renewable and non-renewable energy sources?",
        "Describe the process of neural network training in machine learning.",
        "What are the potential implications of CRISPR technology in medicine?",
        "How does blockchain technology work and what are its applications beyond cryptocurrency?",
    ]

    for question in questions[:num_questions]:
        start_time = time.time()
        response = chat.ask(question)
        end_time = time.time()
        response_time = end_time - start_time
        input_tokens = count_tokens(question)
        output_tokens = count_tokens(response)
        results.append(
            {
                "response_time": response_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }
        )
        print(
            f"User {user_id} got response to question {question} in {response_time:.2f} seconds"
        )
        time.sleep(random.uniform(0.5, 1.5))  # Reduced pause between questions

    return results


def run_performance_test(num_users, num_questions):
    """
    Exécute un test de performance avec plusieurs utilisateurs simultanés.

    Args:
        num_users (int): Nombre d'utilisateurs à simuler.
        num_questions (int): Nombre de questions par utilisateur.

    Returns:
        dict: Statistiques de performance.
    """
    pool = multiprocessing.Pool(processes=num_users)
    results = pool.starmap(
        simulate_user_session, [(i, num_questions) for i in range(num_users)]
    )
    pool.close()
    pool.join()

    all_results = [item for sublist in results for item in sublist]
    response_times = [r["response_time"] for r in all_results]
    input_tokens = [r["input_tokens"] for r in all_results]
    output_tokens = [r["output_tokens"] for r in all_results]
    total_tokens = [r["total_tokens"] for r in all_results]

    return {
        "num_users": num_users,
        "num_questions": num_questions,
        "total_requests": len(all_results),
        "response_time": {
            "mean": mean(response_times),
            "median": median(response_times),
            "min": min(response_times),
            "max": max(response_times),
            "std_dev": stdev(response_times),
        },
        "input_tokens": {
            "mean": mean(input_tokens),
            "median": median(input_tokens),
            "min": min(input_tokens),
            "max": max(input_tokens),
        },
        "output_tokens": {
            "mean": mean(output_tokens),
            "median": median(output_tokens),
            "min": min(output_tokens),
            "max": max(output_tokens),
        },
        "total_tokens": {
            "mean": mean(total_tokens),
            "median": median(total_tokens),
            "min": min(total_tokens),
            "max": max(total_tokens),
        },
    }


def generate_markdown_report(scenarios_results):
    """
    Génère un rapport Markdown à partir des résultats des scénarios.

    Args:
        scenarios_results (list): Liste des résultats pour chaque scénario.

    Returns:
        str: Rapport au format Markdown.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markdown = f"# Performance Test Results\n\nDate: {now}\n\n"

    for i, stats in enumerate(scenarios_results, 1):
        markdown += f"## Scenario {i}: {stats['num_users']} Users, {stats['num_questions']} Questions Each\n\n"
        markdown += f"Total requests: {stats['total_requests']}\n\n"

        markdown += "### Response Time (seconds)\n\n"
        markdown += "| Metric | Value |\n|--------|-------|\n"
        for key, value in stats["response_time"].items():
            markdown += f"| {key.capitalize()} | {value:.2f} |\n"

        markdown += "\n### Token Usage\n\n"
        markdown += (
            "| Metric | Input | Output | Total |\n|--------|-------|--------|-------|\n"
        )
        for key in ["mean", "median", "min", "max"]:
            markdown += f"| {key.capitalize()} | {stats['input_tokens'][key]:.2f} | {stats['output_tokens'][key]:.2f} | {stats['total_tokens'][key]:.2f} |\n"

        markdown += "\n---\n\n"

    return markdown


if __name__ == "__main__":
    start_ollama_server()

    scenarios = [
        {"num_users": 30, "num_questions": 3},
    ]

    scenarios_results = []

    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(
            f"Testing with {scenario['num_users']} concurrent users, {scenario['num_questions']} questions each"
        )
        print(f"{'='*50}")
        stats = run_performance_test(**scenario)
        scenarios_results.append(stats)

    markdown_report = generate_markdown_report(scenarios_results)

    with open("tests/results.md", "w") as f:
        f.write(markdown_report)

    print("Performance test results have been saved to tests/results.md")
