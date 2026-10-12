import os

from psycopg import Connection
from psycopg.rows import tuple_row
from psycopg_pool import ConnectionPool


DATABASE_URL = os.environ["DATABASE_URL"]


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    open=False,
    kwargs={"row_factory": tuple_row},
)


def open_pool() -> None:
    pool.open(wait=True)


def close_pool() -> None:
    pool.close()


def create_interactions_table() -> None:
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id BIGSERIAL PRIMARY KEY,
                    session_id UUID NOT NULL,
                    mode TEXT NOT NULL,
                    question TEXT NOT NULL,
                    processed_question TEXT,
                    answer TEXT,
                    answer_id INTEGER,
                    similarity REAL,
                    sentiment TEXT,
                    sentiment_confidence REAL,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (answer_id) REFERENCES answers(id)
                )
                """
            )


def register_interaction(session_id: str, mode: str, question: str, processed_question: str | None = None, answer: str | None = None, answer_id: int | None = None, similarity: float | None = None, sentiment: str | None = None, sentiment_confidence: float | None = None) -> None:

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO interactions (
                    session_id,
                    mode,
                    question,
                    processed_question,
                    answer,
                    answer_id,
                    similarity,
                    sentiment,
                    sentiment_confidence
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    mode,
                    question,
                    processed_question,
                    answer,
                    answer_id,
                    similarity,
                    sentiment,
                    sentiment_confidence,
                ),
            )


def search_answers(ids) -> list[tuple]:
    
    if len(ids) == 0:
        return []

    answer_ids = [int(answer_id) for answer_id in ids]

    placeholders = ",".join(["%s"] * len(answer_ids))

    with pool.connection() as conn:
        with conn.cursor() as cursor:
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
                answer_ids,
            )

            results = cursor.fetchall()

    result_map = {row[0]: row for row in results}

    return [
        result_map[answer_id]
        for answer_id in answer_ids
        if answer_id in result_map
    ]