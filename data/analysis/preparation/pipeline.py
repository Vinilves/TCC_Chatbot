import pandas as pd

from data.analysis.metrics.semantic_similarity import calculate_bertscore
from data.analysis.metrics.diversity import calculate_diversity_metrics
from data.analysis.metrics.thematic_consistency import (calculate_embedding_similarity)


def calculate_metrics(df: pd.DataFrame, model) -> pd.DataFrame:

    df = df.copy()

    required_columns = {
        "question",
        "answer",
        "reference_answer",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Colunas necessárias para calcular as métricas ausentes: "
            f"{sorted(missing_columns)}"
        )

    if df.empty:
        df["bertscore_f1"] = pd.Series(
            index=df.index,
            dtype="float64",
        )
        df["ttr"] = pd.Series(index=df.index, dtype="float64")
        df["distinct_2"] = pd.Series(index=df.index, dtype="float64")
        df["distinct_3"] = pd.Series(index=df.index, dtype="float64")
        df["embedding_cosine"] = pd.Series(
            index=df.index,
            dtype="float64",
        )

        return df

    for column in ["question", "answer"]:
        invalid = (
            df[column].isna()
            | ~df[column].map(lambda value: isinstance(value, str))
            | df[column].map(
                lambda value: (
                    isinstance(value, str) and not value.strip()
                )
            )
        )

        if invalid.any():
            raise ValueError(
                f"A coluna '{column}' contém "
                f"{int(invalid.sum())} valores nulos, inválidos ou vazios."
            )

    df["bertscore_f1"] = float("nan")

    valid_reference = (
        df["reference_answer"].notna()
        & df["reference_answer"].map(
            lambda value: isinstance(value, str)
            and bool(value.strip())
        )
    )

    if valid_reference.any():
        candidates = df.loc[valid_reference, "answer"].tolist()
        references = df.loc[
            valid_reference,
            "reference_answer",
        ].tolist()

        scores = calculate_bertscore(
            candidates=candidates,
            references=references,
            batch_size=16,
        )

        if len(scores) != len(candidates):
            raise ValueError(
                "A quantidade de valores BERTScore retornados "
                "não corresponde à quantidade de respostas avaliadas."
            )

        df.loc[valid_reference, "bertscore_f1"] = scores

    diversity = df["answer"].apply(calculate_diversity_metrics)

    diversity_df = pd.DataFrame(
        diversity.tolist(),
        index=df.index,
    )

    expected_diversity_columns = {
        "ttr",
        "distinct_2",
        "distinct_3",
    }

    missing_diversity_columns = (
        expected_diversity_columns - set(diversity_df.columns)
    )

    if missing_diversity_columns:
        raise ValueError(
            "A função de diversidade não retornou as métricas esperadas: "
            f"{sorted(missing_diversity_columns)}"
        )

    df = pd.concat(
        [
            df.drop(
                columns=[
                    column
                    for column in expected_diversity_columns
                    if column in df.columns
                ],
                errors="ignore",
            ),
            diversity_df,
        ],
        axis=1,
    )

    embedding_scores = calculate_embedding_similarity(
        questions=df["question"].tolist(),
        answers=df["answer"].tolist(),
        model=model,
        batch_size=32,
    )

    if len(embedding_scores) != len(df):
        raise ValueError(
            "A quantidade de valores de similaridade cosseno retornados "
            "não corresponde à quantidade de interações."
        )

    df["embedding_cosine"] = embedding_scores

    return df