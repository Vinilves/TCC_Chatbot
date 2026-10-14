from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "template_models" / "embeddings"


model = SentenceTransformer(
    str(MODEL_PATH),
    local_files_only=True
)


def generate_embedding(text: str) -> np.ndarray:
    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return np.asarray(embedding, dtype=np.float32)