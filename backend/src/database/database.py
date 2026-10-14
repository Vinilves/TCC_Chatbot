import os
from uuid import UUID
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


class SessionUnavailableError(Exception):
    """Indica que a sessão não está disponível para novas interações."""


def open_pool() -> None:
    pool.open(wait=True)


def close_pool() -> None:
    pool.close()


def create_sessions_table() -> None:
    
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id UUID PRIMARY KEY,
                    mode TEXT NOT NULL CHECK (mode IN ('base', 'adaptive')),
                    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'interrupted')),
                    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMPTZ,
                    duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
                    CHECK (
                        (
                            status = 'active' AND ended_at IS NULL AND duration_seconds IS NULL
                        )
                        OR
                        (
                            status IN ('completed', 'interrupted') AND ended_at IS NOT NULL AND duration_seconds IS NOT NULL
                        )
                    )
                )
                """
            )


def create_interactions_table() -> None:

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id BIGSERIAL PRIMARY KEY,
                    session_id UUID NOT NULL,
                    mode TEXT NOT NULL CHECK (mode IN ('base', 'adaptive')),
                    question TEXT NOT NULL,
                    processed_question TEXT,
                    answer TEXT,
                    answer_id INTEGER,
                    similarity REAL,
                    sentiment TEXT,
                    sentiment_confidence REAL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY (answer_id) REFERENCES answers(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_interactions_session_id
                ON interactions (session_id)
                """
            )


def create_tables() -> None:

    create_sessions_table()
    create_interactions_table()


def register_session(session_id: str, mode: str) -> None:

    session_uuid = UUID(session_id)

    if mode not in ("base", "adaptive"):
        raise ValueError("Modo de sessão inválido.")

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    mode
                )
                VALUES (%s, %s)
                """,
                (session_uuid, mode),
            )


def get_session(session_id: str) -> tuple | None:

    session_uuid = UUID(session_id)

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    session_id,
                    mode,
                    status,
                    started_at,
                    ended_at,
                    duration_seconds
                FROM sessions
                WHERE session_id = %s
                """,
                (session_uuid,),
            )

            return cursor.fetchone()


def end_session(session_id: str, status: str = "completed") -> tuple | None:

    session_uuid = UUID(session_id)

    if status not in ("completed", "interrupted"):
        raise ValueError("Status de encerramento inválido.")

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE sessions
                SET
                    status = %s,

                    ended_at = CURRENT_TIMESTAMP,

                    duration_seconds = GREATEST(
                        0,
                        FLOOR(
                            EXTRACT(
                                EPOCH FROM (
                                    CURRENT_TIMESTAMP - started_at
                                )
                            )
                        )::INTEGER
                    )

                WHERE session_id = %s
                  AND status = 'active'

                RETURNING mode, duration_seconds
                """,
                (status, session_uuid),
            )

            return cursor.fetchone()


def register_interaction(session_id: str, mode: str, question: str, processed_question: str | None = None, answer: str | None = None, answer_id: int | None = None, similarity: float | None = None, sentiment: str | None = None, sentiment_confidence: float | None = None) -> None:

    session_uuid = UUID(session_id)

    if mode not in ("base", "adaptive"):
        raise ValueError("Modo de interação inválido.")

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
                SELECT s.session_id, s.mode, %s, %s, %s, %s, %s, %s, %s
                FROM sessions AS s
                WHERE s.session_id = %s AND s.mode = %s AND s.status = 'active'
                """,
                (
                    question,
                    processed_question,
                    answer,
                    answer_id,
                    similarity,
                    sentiment,
                    sentiment_confidence,
                    session_uuid,
                    mode,
                ),
            )

            if cursor.rowcount == 0:
                raise SessionUnavailableError(
                    "Sessão inexistente, encerrada ou com modo incompatível."
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