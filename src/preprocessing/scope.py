import re
from pathlib import Path

from src.preprocessing.normalizer import (normalize, normalize_for_comparison)


OUT_OF_SCOPE_TECHNOLOGIES = {
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "php",
    "ruby",
    "go",
    "rust",
    "kotlin",
    "swift",
    "dart",
    "scala",
    "cobol",
    "assembly",
    "elixir",
    "f#",
    "pascal",
    "delphi",
}

SCOPE_FILE = Path(__file__).with_name("python_vocabulary.txt")


def load_scope():

    with open(SCOPE_FILE, "r", encoding="utf-8") as file:

        return {
            line.strip()
            for line in file
            if line.strip()
        }


PYTHON_SCOPE = load_scope()


def extract_python_terms(question):

    normalized_question = normalize_for_comparison(question)

    found_terms = []

    for term in PYTHON_SCOPE:

        normalized_term = normalize_for_comparison(term)

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_term)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized_question):
            found_terms.append(term)

    return sorted(set(found_terms))


def extract_question(text: str) -> str:

    text = normalize(text)

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    parts = [
        part.strip()
        for part in parts
        if part.strip()
    ]

    question_index = None

    for i, part in enumerate(parts):

        if "?" in part:
            question_index = i
            break

    if question_index is None:
        return text

    question = parts[question_index]

    return question


def extract_out_of_scope_technologies(question):

    normalized_question = normalize_for_comparison(question)

    found_technologies = []

    for technology in OUT_OF_SCOPE_TECHNOLOGIES:

        normalized_technology = normalize_for_comparison(technology)

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_technology)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized_question):
            found_technologies.append(technology)

    return sorted(set(found_technologies))


def check_scope(question):

    out_of_scope_technologies = extract_out_of_scope_technologies(question)

    return len(out_of_scope_technologies) == 0


def query_terms(question):

    terms = extract_python_terms(question)

    if not terms:
        return question

    context = " | ".join(terms)

    return f"{context} | Python | {question}"