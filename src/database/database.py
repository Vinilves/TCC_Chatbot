import os
import psycopg

DATABASE_URL = os.environ["DATABASE_URL"]


def connect() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL)


def create_interactions_table(conn: psycopg.Connection) -> None:

    cursor = conn.cursor()

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

    conn.commit()


def register_interaction(conn: psycopg.Connection, session_id: str, mode: str, question: str, processed_question: str | None = None, answer: str | None = None, answer_id: int | None = None, similarity: float | None = None, sentiment: str | None = None, sentiment_confidence: float | None = None) -> None:

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
            sentiment_confidence
        )
    )

    conn.commit()


def search_answers(conn: psycopg.Connection, ids):
    
    cursor = conn.cursor()

    if len(ids) == 0:
        return []

    placeholders = ",".join(["%s"] * len(ids))

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