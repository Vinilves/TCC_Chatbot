from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "data" / "sqlite" / "banco_respostas.sqlite"


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_PATH)


def fetch_answers(conn: sqlite3.Connection, ids):
    cursor = conn.cursor()

    placeholders = ",".join("?" * len(ids))

    cursor.execute(
        f"""
        SELECT
            id,
            question,
            answer,
            code,
            source,
            language
        FROM answers
        WHERE id IN ({placeholders})
        """,
        [int(i) for i in ids]
    )

    results = cursor.fetchall()

    results_map = {row[0]: row for row in results}

    return [results_map[i] for i in ids if i in results_map]