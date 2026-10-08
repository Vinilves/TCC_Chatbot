import re
from pathlib import Path

from backend.src.preprocessing.normalizer import (normalize, normalize_for_comparison)


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


def extract_python_terms(question: str):

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

    found_terms = sorted(
        set(found_terms),
        key=lambda term: (
            len(normalize_for_comparison(term).split()),
            len(normalize_for_comparison(term))
        ),
        reverse=True
    )

    selected_terms = []

    for term in found_terms:

        normalized_term = normalize_for_comparison(term)

        if any(
            re.search(
                r"(?<!\w)"
                + re.escape(normalized_term)
                + r"(?!\w)",
                normalize_for_comparison(selected_term)
            )
            for selected_term in selected_terms):
            continue

        selected_terms.append(term)

    return selected_terms


def split_text_parts(text: str):

    text = normalize(text)

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def extract_out_of_scope_technologies(question: str):

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


def check_scope(question: str):

    out_of_scope_technologies = (extract_out_of_scope_technologies(question))

    return len(out_of_scope_technologies) == 0


def query_terms(question: str):

    terms = extract_python_terms(question)

    if not terms:
        return question

    context = " | ".join(terms)

    return (
        f"{context} | Python | {question}"
    )