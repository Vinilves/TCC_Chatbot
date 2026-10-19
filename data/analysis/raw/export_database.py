from pathlib import Path

import pandas as pd
import psycopg
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "analysis" / "raw"
ENV_FILE = PROJECT_ROOT / "backend" / ".env"

BATCH_SIZE = 10_000

load_dotenv(ENV_FILE)

import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "A variável DATABASE_URL não foi encontrada no arquivo .env."
    )


QUERIES = {
    "interactions_raw.parquet": """
        SELECT *
        FROM interactions
        ORDER BY id
    """,
    "answers_snapshot.parquet": """
        SELECT *
        FROM answers
        ORDER BY id
    """,
    "sessions_raw.parquet": """
        SELECT *
        FROM sessions
        ORDER BY session_id
    """,
}


def export_query_to_parquet(query: str, parquet_name: str) -> None:
    parquet_path = RAW_DIR / parquet_name
    temporary_path = parquet_path.with_suffix(".tmp.parquet")

    writer = None
    total_records = 0

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor(name="parquet_export_cursor") as cursor:
                cursor.execute(query)

                columns = [
                    column.name
                    for column in cursor.description
                ]

                while True:
                    rows = cursor.fetchmany(BATCH_SIZE)

                    if not rows:
                        break

                    chunk = pd.DataFrame(
                        rows,
                        columns=columns,
                    )

                    table = pa.Table.from_pandas(
                        chunk,
                        preserve_index=False,
                    )

                    if writer is None:
                        writer = pq.ParquetWriter(
                            temporary_path,
                            table.schema,
                        )

                    writer.write_table(table)
                    total_records += len(chunk)

        if writer is not None:
            writer.close()
            writer = None

            temporary_path.replace(parquet_path)

        else:
            empty_table = pa.table(
                {
                    column: pa.array([], type=pa.null())
                    for column in columns
                }
            )

            pq.write_table(
                empty_table,
                temporary_path,
            )

            temporary_path.replace(parquet_path)

        print(f"Exportado: {parquet_path}")
        print(f"Registros: {total_records}")

    except Exception:
        if writer is not None:
            writer.close()

        if temporary_path.exists():
            temporary_path.unlink()

        raise


def main() -> None:
    for parquet_name, query in QUERIES.items():
        export_query_to_parquet(
            query=query,
            parquet_name=parquet_name,
        )


if __name__ == "__main__":
    main()