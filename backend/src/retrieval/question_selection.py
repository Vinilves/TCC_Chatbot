import faiss
import numpy as np
from backend.src.preprocessing.scope import split_text_parts


def search_best_similarity(index: faiss.Index, embedding: np.ndarray):

    distances, indices = index.search(
        embedding.reshape(1, -1),
        1
    )

    return (
        float(distances[0][0]),
        int(indices[0][0])
    )


def select_technical_question(index: faiss.Index, text: str, generate_embedding):

    text = text.strip()

    if not text:
        return "", "", None


    sentences = split_text_parts(text)


    if len(sentences) > 1:

        best_sentence = sentences[0]
        best_similarity = float("-inf")

        for sentence in sentences:

            embedding = generate_embedding(sentence)

            similarity, _ = search_best_similarity(index, embedding)

            if similarity > best_similarity:

                best_similarity = similarity
                best_sentence = sentence


        context = " ".join(
            sentence
            for sentence in sentences
            if sentence != best_sentence
        ).strip()

        return (best_sentence, context, best_similarity)


    sentence = sentences[0] if sentences else text

    comma_parts = [
        part.strip()
        for part in sentence.split(",")
        if part.strip()
    ]


    if len(comma_parts) == 1:

        embedding = generate_embedding(sentence)

        similarity, _ = search_best_similarity(index, embedding)

        return (sentence, "", similarity)


    candidates = []


    for part in comma_parts:

        embedding = generate_embedding(part)

        similarity, _ = search_best_similarity(index, embedding)

        candidates.append(
            {
                "question": part,
                "similarity": similarity
            }
        )


    for start in range(len(comma_parts)):

        for end in range(start + 1, len(comma_parts)):

            candidate = ", ".join(
                comma_parts[start:end + 1]
            )

            embedding = generate_embedding(candidate)

            similarity, _ = search_best_similarity(index, embedding)

            candidates.append(
                {
                    "question": candidate,
                    "similarity": similarity
                }
            )


    best_candidate = max(
        candidates,
        key=lambda candidate: candidate["similarity"]
    )

    technical_question = best_candidate["question"]


    if technical_question == sentence:

        context = ""

    else:

        remaining = sentence.replace(
            technical_question,
            "",
            1
        )

        context = remaining.strip(" ,")


    return (technical_question, context, best_candidate["similarity"])