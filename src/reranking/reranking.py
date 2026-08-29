import re
import unicodedata

from rank_bm25 import BM25Okapi

from src.preprocessing.scope import extract_python_terms


def normalize_for_bm25(text: str) -> str:

    text = text.lower().strip()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


def tokenize_for_bm25(text: str, python_terms=None):

    text = normalize_for_bm25(text)

    if python_terms:

        normalized_terms = sorted(
            (
                normalize_for_bm25(term)
                for term in python_terms
            ),
            key=len,
            reverse=True
        )

        for term in normalized_terms:

            tokenized_term = term.replace(
                " ",
                "_"
            )

            pattern = (
                r"(?<!\w)"
                + re.escape(term)
                + r"(?!\w)"
            )

            text = re.sub(
                pattern,
                tokenized_term,
                text
            )

    return re.findall(
        r"\b\w+\b",
        text
    )


def rerank_candidates(question, candidates, similarities):

    if not candidates:
        return []

    question_terms = extract_python_terms(question)

    question_tokens = tokenize_for_bm25(
        question,
        question_terms
    )

    corpus = []

    for candidate in candidates:

        candidate_question = candidate[1]

        candidate_terms = extract_python_terms(
            candidate_question
        )

        candidate_tokens = tokenize_for_bm25(
            candidate_question,
            candidate_terms
        )

        corpus.append(candidate_tokens)

    bm25 = BM25Okapi(corpus)

    bm25_scores = bm25.get_scores(question_tokens)

    results = []

    for candidate, similarity, bm25_score in zip(
        candidates,
        similarities,
        bm25_scores
    ):

        results.append(
            (
                float(bm25_score),
                float(similarity),
                candidate
            )
        )

    results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return results