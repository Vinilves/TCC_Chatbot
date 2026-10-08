from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_embedding_model() -> SentenceTransformer:

    return SentenceTransformer(MODEL_NAME)


def calculate_embedding_similarity(questions: list[str], answers: list[str], model: SentenceTransformer, batch_size: int = 32) -> list[float]:

    if len(questions) != len(answers):
        raise ValueError(
            "A quantidade de perguntas deve ser igual à quantidade de respostas."
        )

    if not questions:
        return []

    question_embeddings = model.encode(
        questions,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=batch_size,
        show_progress_bar=False,
    )

    answer_embeddings = model.encode(
        answers,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=batch_size,
        show_progress_bar=False,
    )

    similarities = cosine_similarity(
        question_embeddings,
        answer_embeddings,
    )

    return similarities.diagonal().tolist()