import pandas as pd

from data.analysis.metrics.semantic_similarity import calculate_bertscore
from data.analysis.metrics.diversity import calculate_diversity_metrics
from data.analysis.metrics.thematic_consistency import (calculate_embedding_similarity)


def calculate_metrics(df: pd.DataFrame, model) -> pd.DataFrame:

    df = df.copy()

    df["bertscore_f1"] = calculate_bertscore(
        candidates=df["answer"].tolist(),
        references=df["reference_answer"].tolist(),
        batch_size=16,
    )

    diversity = df["answer"].apply(
        calculate_diversity_metrics
    )

    diversity_df = pd.DataFrame(
        diversity.tolist(),
        index=df.index,
    )

    df = pd.concat(
        [df, diversity_df],
        axis=1,
    )

    df["embedding_cosine"] = calculate_embedding_similarity(
        questions=df["question"].tolist(),
        answers=df["answer"].tolist(),
        model=model,
        batch_size=32,
    )

    return df