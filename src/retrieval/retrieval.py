from pathlib import Path
import faiss
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[2]

INDEX_PATH = BASE_DIR / "data" / "faiss" / "indice_faiss.index"


def load_index() -> faiss.Index:
    return faiss.read_index(str(INDEX_PATH))


def search_answers(
    index: faiss.Index,
    embedding: np.ndarray,
    k: int = 10
):
    distances, indices = index.search(
        embedding.reshape(1, -1),
        k
    )

    return distances, indices