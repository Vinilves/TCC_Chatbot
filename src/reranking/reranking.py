import re
import unicodedata

from rank_bm25 import BM25Okapi

from src.preprocessing.scope import extract_python_terms
from src.preprocessing.stopwords import STOPWORDS_PT


PYTHON_SYNTAX_PATTERN = (
    r"""\\(?:[nrt\\'"]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})"""
)


def normalize_for_bm25(text):
    
    text = text.lower()

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = re.sub(r"[^\w\s]", " ", text)

    return text


def extract_python_syntax(text):

    return re.findall(PYTHON_SYNTAX_PATTERN, text)


def tokenize_for_bm25(text):
    
    text = normalize_for_bm25(text)

    tokens = text.split()

    return [
        token
        for token in tokens
        if token not in STOPWORDS_PT
    ]


def normalize_scores(scores):
    
    if not scores:
        return []

    minimum = min(scores)
    maximum = max(scores)

    if maximum == minimum:
        return [1.0 for _ in scores]

    return [
        (score - minimum) / (maximum - minimum)
        for score in scores
    ]


def calculate_lexical_overlap(query, candidate):
    
    query_tokens = set(tokenize_for_bm25(query))
    candidate_tokens = set(tokenize_for_bm25(candidate))

    if not query_tokens:
        return 0.0

    return len(query_tokens & candidate_tokens) / len(query_tokens)


def calculate_python_term_overlap(query_terms, candidate_terms):
    
    if not query_terms:
        return 0.0

    query_terms_set = set(query_terms)
    candidate_terms_set = set(candidate_terms)

    matched_terms = (
        query_terms_set & candidate_terms_set
    )

    return len(matched_terms) / len(query_terms_set)


def calculate_python_term_specificity(query_terms, candidate_terms):
    
    if not candidate_terms:
        return 0.0

    query_terms_set = set(query_terms)
    candidate_terms_set = set(candidate_terms)

    matched_terms = (
        query_terms_set & candidate_terms_set
    )

    if not matched_terms:
        return 0.0

    return len(matched_terms) / len(candidate_terms_set)


def calculate_python_syntax_overlap(query, candidate):
    
    query_syntax = set(extract_python_syntax(query))

    candidate_syntax = set(extract_python_syntax(candidate))

    if not query_syntax:
        return 0.0

    return len(query_syntax & candidate_syntax) / len(query_syntax)


def has_full_python_term_match(query_terms, candidate_terms):
    
    if not query_terms:
        return False

    query_terms_set = set(query_terms)
    candidate_terms_set = set(candidate_terms)

    return query_terms_set.issubset(candidate_terms_set)


def rerank_candidates(question, candidates, similarities):

    if not candidates:
        return []

    query_terms = extract_python_terms(question)

    candidate_terms = [
        extract_python_terms(candidate[1])
        for candidate in candidates
    ]

    lexical_scores = []

    tokenized_candidates = [
        tokenize_for_bm25(candidate[1])
        for candidate in candidates
    ]

    query_tokens = tokenize_for_bm25(question)

    if query_tokens:

        bm25 = BM25Okapi(tokenized_candidates)

        lexical_scores = bm25.get_scores(
            query_tokens
        ).tolist()

        lexical_scores = normalize_scores(
            lexical_scores
        )

    else:

        lexical_scores = [
            0.0
            for _ in candidates
        ]

    python_term_overlap_scores = [
        calculate_python_term_overlap(
            query_terms,
            terms
        )
        for terms in candidate_terms
    ]

    python_term_specificity_scores = [
        calculate_python_term_specificity(
            query_terms,
            terms
        )
        for terms in candidate_terms
    ]

    python_syntax_overlap_scores = [
        calculate_python_syntax_overlap(
            question,
            candidate[1]
        )
        for candidate in candidates
    ]

    full_term_match_scores = [
        has_full_python_term_match(
            query_terms,
            terms
        )
        for terms in candidate_terms
    ]

    ranking_indices = list(
        range(len(candidates))
    )

    ranking_indices.sort(
        key=lambda index: (
            full_term_match_scores[index],
            python_term_overlap_scores[index],
            python_term_specificity_scores[index],
            similarities[index],
            python_syntax_overlap_scores[index],
            lexical_scores[index],
        ),
        reverse=True,
    )

    results = []

    for index in ranking_indices:

        candidate = candidates[index]

        semantic_similarity = similarities[index]

        lexical_overlap = calculate_lexical_overlap(
            question,
            candidate[1]
        )

        results.append(
            (
                semantic_similarity,
                lexical_overlap,
                candidate,
            )
        )

    return results