import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> np.ndarray:
    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return np.asarray(embedding, dtype=np.float32)