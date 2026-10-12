from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.src.database.database import (open_pool, close_pool, create_interactions_table)
from backend.src.session.session import create_session_id
from backend.src.modes.base import to_respond as respond_base
from backend.src.modes.adaptive import to_respond as respond_adaptive


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()

    try:
        create_interactions_table()
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

active_sessions = {}


class StartSessionRequest(BaseModel):
    condition: str = Field(pattern="^[AB]$")


class MessageRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=5000)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/sessions")
def start_session(data: StartSessionRequest):
    session_id = str(create_session_id())

    respond = (
        respond_base
        if data.condition == "A"
        else respond_adaptive
    )

    active_sessions[session_id] = {
        "condition": data.condition,
        "respond": respond,
        "started_at": monotonic(),
    }

    return {
        "session_id": session_id,
        "condition": data.condition,
    }


@app.post("/api/chat/messages")
def send_message(data: MessageRequest, debug: bool = Query(default=False)):
    session = active_sessions.get(data.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou encerrada.",
        )

    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="A mensagem não pode estar vazia.",
        )

    include_debug = (
        debug
        and session["condition"] == "B"
    )

    try:
        if include_debug:
            result = session["respond"](
                question=question,
                session_id=data.session_id,
                include_debug=True,
            )
        else:
            result = session["respond"](
                question=question,
                session_id=data.session_id,
            )

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
    session = active_sessions.get(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou já encerrada.",
        )

    duration_seconds = max(
        0,
        int(monotonic() - session["started_at"]),
    )

    active_sessions.pop(session_id)

    return {
        "status": "ended",
        "session_id": session_id,
        "condition": session["condition"],
        "duration_seconds": duration_seconds,
    }