import re


def tokenize(text: str) -> list[str]:

    if not isinstance(text, str):
        return []

    return re.findall(r"\b\w+\b", text.lower())


def calculate_ttr(text: str) -> float:

    tokens = tokenize(text)

    if not tokens:
        return 0.0

    unique_tokens = set(tokens)

    return len(unique_tokens) / len(tokens)


def calculate_distinct_n(text: str, n: int) -> float:

    tokens = tokenize(text)

    if len(tokens) < n:
        return 0.0

    ngrams = [
        tuple(tokens[i:i + n])
        for i in range(len(tokens) - n + 1)
    ]

    if not ngrams:
        return 0.0

    distinct_ngrams = set(ngrams)

    return len(distinct_ngrams) / len(ngrams)


def calculate_diversity_metrics(text: str) -> dict[str, float]:

    return {
        "ttr": calculate_ttr(text),
        "distinct_2": calculate_distinct_n(text, 2),
        "distinct_3": calculate_distinct_n(text, 3),
    }