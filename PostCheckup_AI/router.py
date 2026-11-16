"""FastAPI endpoints for the post-checkup AI.

To enable them, add to main.py:
    from PostCheckup_AI.router import router as post_checkup_router
    app.include_router(post_checkup_router)
"""

import secrets

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from PostCheckup_AI.chatbot import PostCheckupAI
from PostCheckup_AI.sample_data import SAMPLE_NOTES

router = APIRouter(prefix="/post-checkup", tags=["Post checkup"])

# Sessions live in memory (fine for the hackathon demo; lost on restart).
_sessions: dict[str, PostCheckupAI] = {}


class StartSession(BaseModel):
    visit_id: str


class Question(BaseModel):
    question: str


def _get_session(session_id: str) -> PostCheckupAI:
    ai = _sessions.get(session_id)
    if ai is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found.")
    return ai


@router.post("/start", status_code=status.HTTP_201_CREATED)
def start_session(body: StartSession):
    """Returns the original doctor summary, the easy summary and the action plan."""
    # TODO: replace the sample data with the real doctor-note table.
    note = SAMPLE_NOTES.get(body.visit_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No doctor note found for this visit.")
    try:
        ai = PostCheckupAI(note)
    except RuntimeError as error:  # missing GEMINI_API_KEY
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))
    session_id = secrets.token_hex(16)
    _sessions[session_id] = ai
    return {"session_id": session_id, "report": ai.build_report().to_dict()}


@router.post("/{session_id}/ask")
def ask_question(session_id: str, body: Question):
    return _get_session(session_id).ask(body.question).to_dict()
