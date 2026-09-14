import faiss
import numpy as np


def search_best_similarity(index: faiss.Index, embedding: np.ndarray):

    distances, indices = index.search(
        embedding.reshape(1, -1),
        1
    )

    return (
        float(distances[0][0]),
        int(indices[0][0])
    )


def select_best_clause(index: faiss.Index, clauses: list[str], generate_embedding):

    if not clauses:
        return "", None

    if len(clauses) == 1:

        embedding = generate_embedding(clauses[0])

        similarity, _ = search_best_similarity(index, embedding)

        return clauses[0], similarity

    best_clause = clauses[0]

    best_similarity = float("-inf")

    for clause in clauses:

        clause = clause.strip()

        if not clause:
            continue

        embedding = generate_embedding(clause)

        similarity, _ = search_best_similarity(index, embedding)

        if similarity > best_similarity:

            best_similarity = similarity

            best_clause = clause

    return (best_clause, best_similarity)