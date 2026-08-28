from src.preprocessing.scope import extract_python_terms


def rerank_candidates(question: str, candidates: list, similarities):

    python_terms = extract_python_terms(question)

    ranked_candidates = []

    for candidate, similarity in zip(candidates, similarities):

        candidate_question = candidate[1]

        question_lower = candidate_question.lower()

        term_match = any(
            term.lower() in question_lower
            for term in python_terms
        )

        similarity = float(similarity)

        score = similarity

        if term_match:
            score += 0.10

        ranked_candidates.append(
            (
                score,
                similarity,
                candidate
            )
        )

    ranked_candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return ranked_candidates