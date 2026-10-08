import pandas as pd
import pyarrow.parquet as pq


def load_data_in_batches(interactions_path: str, batch_size: int = 500):
    
    parquet_file = pq.ParquetFile(
        interactions_path
    )

    for batch in parquet_file.iter_batches(
        batch_size=batch_size):
        yield batch.to_pandas()


def load_answers(answers_path: str) -> pd.DataFrame:

    return pd.read_parquet(
        answers_path
    )


def prepare_data(interactions: pd.DataFrame, answers: pd.DataFrame) -> pd.DataFrame:

    df = interactions.copy()

    reference = answers[
        ["id", "answer"]
    ].rename(
        columns={
            "id": "answer_id",
            "answer": "reference_answer",
        }
    )

    df = df.merge(
        reference,
        on="answer_id",
        how="left",
    )

    return df