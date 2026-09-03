import re
import unicodedata

from rank_bm25 import BM25Okapi

from src.preprocessing.scope import extract_python_terms
from src.preprocessing.stopwords import STOPWORDS_PT


PYTHON_SYNTAX_PATTERN = (
    r"""\\(?:[nrt\\'"]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})"""
)


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


def extract_python_syntax(text: str):

    return re.findall(
        PYTHON_SYNTAX_PATTERN,
        text
    )


def tokenize_for_bm25(text: str, python_terms=None):

    text = normalize_for_bm25(text)

    if python_terms:

        normalized_terms = sorted(
            (
                normalize_for_bm25(term)
                for term in python_terms
                if term
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

    python_syntax = extract_python_syntax(text)

    text_without_syntax = re.sub(
        PYTHON_SYNTAX_PATTERN,
        " ",
        text
    )

    tokens = re.findall(
        r"\b\w+\b",
        text_without_syntax
    )

    tokens = [
        token
        for token in tokens
        if token not in STOPWORDS_PT
    ]

    tokens.extend(python_syntax)

    return tokens


def normalize_scores(scores):

    scores = [
        float(score)
        for score in scores
    ]

    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [1.0 for _ in scores]

    return [
        (score - min_score) / (max_score - min_score)
        for score in scores
    ]


def rerank_candidates(question, candidates, similarities):

    if not candidates:
        return []

    question_terms = extract_python_terms(question)

    question_tokens = tokenize_for_bm25(question, question_terms)

    question_syntax = set(extract_python_syntax(question))

    corpus = []

    candidate_syntax = []

    for candidate in candidates:

        candidate_question = candidate[1]

        candidate_terms = extract_python_terms(candidate_question)

        candidate_tokens = tokenize_for_bm25(candidate_question, candidate_terms)

        corpus.append(candidate_tokens)

        candidate_syntax.append(
            set(
                extract_python_syntax(
                    candidate_question
                )
            )
        )

    bm25 = BM25Okapi(corpus)

    bm25_scores = bm25.get_scores(question_tokens)

    semantic_scores = [
        float(score)
        for score in similarities
    ]

    lexical_scores = normalize_scores(bm25_scores)

    compatible_indexes = []

    if question_syntax:

        for index, syntax in enumerate(candidate_syntax):

            if question_syntax.intersection(syntax):

                compatible_indexes.append(index)

    else:

        for index, syntax in enumerate(candidate_syntax):

            if not syntax:
                compatible_indexes.append(index)

    if compatible_indexes:

        ranking_indexes = compatible_indexes

    else:

        ranking_indexes = list(
            range(len(candidates))
        )

    results = []

    for index in ranking_indexes:

        candidate = candidates[index]

        semantic_score = semantic_scores[index]

        lexical_score = lexical_scores[index]

        original_similarity = similarities[index]

        final_score = (0.5 * semantic_score + 0.5 * lexical_score)

        results.append(
            (
                float(final_score),
                float(original_similarity),
                candidate
            )
        )

    results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return results