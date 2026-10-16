from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.src.database.database import (open_pool, close_pool, create_tables, register_session, get_session, end_session as finish_session, SessionUnavailableError, SessionSequenceError)

from backend.src.session.session import create_session_id
from backend.src.modes.base import to_respond as respond_base
from backend.src.modes.adaptive import to_respond as respond_adaptive


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()

    try:
        create_tables()
        yield
    finally:
        close_pool()


app = FastAPI(
    title="API do Chatbot de Ensino de Python",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

PYTHON_REFERENCE = "https://docs.python.org/pt-br/3/tutorial/"


class StartSessionRequest(BaseModel):
    participant_id: UUID
    condition: str = Field(pattern="^[AB]$")


class MessageRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=5000)


def parse_session_id(session_id: str) -> str:
    try:
        return str(UUID(session_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Identificador de sessão inválido.",
        ) from None


def get_condition(mode: str) -> str:
    if mode == "base":
        return "A"

    if mode == "adaptive":
        return "B"

    raise HTTPException(
        status_code=500,
        detail="Modo de sessão inválido no banco de dados.",
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/sessions")
def start_session(data: StartSessionRequest):
    session_id = str(create_session_id())

    mode = "base" if data.condition == "A" else "adaptive"

    try:
        register_session(
            session_id=session_id,
            participant_id=str(data.participant_id),
            mode=mode,
        )
    except SessionSequenceError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from None
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível iniciar a sessão.",
        ) from None

    return {
        "session_id": session_id,
        "participant_id": str(data.participant_id),
        "condition": data.condition,
    }


@app.post("/api/chat/messages")
def send_message(data: MessageRequest, debug: bool = Query(default=False)):
    session_id = parse_session_id(data.session_id)

    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="A mensagem não pode estar vazia.",
        )

    try:
        session = get_session(session_id)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar a sessão.",
        ) from None

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada.",
        )

    mode = session[2]
    status = session[3]

    if status != "active":
        raise HTTPException(
            status_code=409,
            detail="A sessão está encerrada e não aceita novas mensagens.",
        )

    if mode == "base":
        respond = respond_base
    elif mode == "adaptive":
        respond = respond_adaptive
    else:
        raise HTTPException(
            status_code=500,
            detail="Modo de sessão inválido no banco de dados.",
        )

    include_debug = debug and mode == "adaptive"

    try:
        if include_debug:
            result = respond(
                question=question,
                session_id=session_id,
                include_debug=True,
            )
        else:
            result = respond(
                question=question,
                session_id=session_id,
            )

    except SessionUnavailableError:
        raise HTTPException(
            status_code=409,
            detail="A sessão foi encerrada antes do registro da interação.",
        ) from None

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível processar a mensagem.",
        ) from None

    similarity = result.get("similarity")

    if similarity is not None:
        similarity = float(similarity)

    response = {
        "session_id": str(result["session_id"]),
        "answer": result["answer"],
        "code": result.get("code"),
        "source": result.get("source"),
        "similarity": similarity,
    }

    if result.get("id") is not None:
        response["documentation_url"] = PYTHON_REFERENCE

    if include_debug and result.get("debug") is not None:
        response["debug"] = result["debug"]

    return response


@app.post("/api/sessions/{session_id}/end")
def end_session(session_id: str):
    session_id = parse_session_id(session_id)

    try:
        result = finish_session(session_id)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível encerrar a sessão.",
        ) from None

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou já encerrada.",
        )

    participant_id, mode, status, duration_seconds = result

    return {
        "status": status,
        "session_id": session_id,
        "participant_id": str(participant_id),
        "condition": get_condition(mode),
        "duration_seconds": duration_seconds,
    }