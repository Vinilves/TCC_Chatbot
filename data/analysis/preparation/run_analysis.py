from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from data.analysis.preparation.preparation import (load_data_in_batches, load_answers, load_sessions, prepare_data,)

from data.analysis.preparation.pipeline import calculate_metrics
from data.analysis.metrics.thematic_consistency import load_embedding_model


INTERACTIONS_PATH = Path(
    "data/analysis/raw/interactions_raw.parquet"
)

ANSWERS_PATH = Path(
    "data/analysis/raw/answers_snapshot.parquet"
)

SESSIONS_PATH = Path(
    "data/analysis/raw/sessions_raw.parquet"
)

OUTPUT_PATH = Path(
    "data/analysis/processed/interactions_metrics.parquet"
)

BATCH_SIZE = 500


def main() -> None:

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    answers = load_answers(
        answers_path=str(ANSWERS_PATH),
    )

    sessions = load_sessions(
        sessions_path=str(SESSIONS_PATH)
    )

    model = load_embedding_model()

    writer = None
    total_processed = 0

    try:

        for interactions_batch in load_data_in_batches(
            interactions_path=str(INTERACTIONS_PATH),
            batch_size=BATCH_SIZE):

            df = prepare_data(
                interactions=interactions_batch,
                answers=answers,
                sessions=sessions
            )

            df = calculate_metrics(
                df=df,
                model=model,
            )

            table = pa.Table.from_pandas(
                df,
                preserve_index=False,
            )

            if writer is None:
                writer = pq.ParquetWriter(
                    OUTPUT_PATH,
                    table.schema,
                )

            writer.write_table(table)

            total_processed += len(df)

            print(
                f"Lote processado: {len(df)} | "
                f"Total: {total_processed}"
            )

    finally:

        if writer is not None:
            writer.close()

    print(
        f"\nAnálise concluída: {OUTPUT_PATH}"
    )

    print(
        f"Interações analisadas: {total_processed}"
    )


if __name__ == "__main__":
    main()