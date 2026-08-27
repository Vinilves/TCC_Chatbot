from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "data" / "sqlite" / "banco_respostas.sqlite"


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_PATH)


def create_interactions_table(conn: sqlite3.Connection) -> None:

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            question TEXT NOT NULL,
            processed_question TEXT,
            answer TEXT,
            answer_id INTEGER,
            similarity REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()


def register_interaction(conn: sqlite3.Connection, session_id: str, mode: str, question: str, processed_question: str | None = None, answer: str | None = None, answer_id: int | None = None, similarity: float | None = None) -> None:

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interactions (
            session_id,
            mode,
            question,
            processed_question,
            answer,
            answer_id,
            similarity
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            mode,
            question,
            processed_question,
            answer,
            answer_id,
            similarity
        )
    )

    conn.commit()


def search_sqlite(conn: sqlite3.Connection, ids):
    cursor = conn.cursor()

    if len(ids) == 0:
        return []

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

    result_map = {row[0]: row for row in results}

    return [result_map[i] for i in ids if i in result_map]


