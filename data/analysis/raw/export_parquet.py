from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


RAW_DIR = Path("data/analysis/raw")

BATCH_SIZE = 10_000


def convert_csv_to_parquet(csv_name: str, parquet_name: str) -> None:

    csv_path = RAW_DIR / csv_name
    parquet_path = RAW_DIR / parquet_name

    writer = None
    total_records = 0

    try:

        for chunk in pd.read_csv(
            csv_path,
            encoding="latin1",
            chunksize=BATCH_SIZE):

            table = pa.Table.from_pandas(
                chunk,
                preserve_index=False,
            )

            if writer is None:
                writer = pq.ParquetWriter(
                    parquet_path,
                    table.schema,
                )

            writer.write_table(table)

            total_records += len(chunk)

    finally:

        if writer is not None:
            writer.close()

    print(
        f"Convertido: {csv_path} -> {parquet_path}"
    )

    print(
        f"Registros: {total_records}"
    )


def main() -> None:

    convert_csv_to_parquet(
        "interactions_raw.csv",
        "interactions_raw.parquet",
    )

    convert_csv_to_parquet(
        "answers_snapshot.csv",
        "answers_snapshot.parquet",
    )


if __name__ == "__main__":
    main()