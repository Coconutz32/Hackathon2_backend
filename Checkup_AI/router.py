"""FastAPI endpoints for the checkup chatbot.

To enable them, add to main.py:
    from Checkup_AI.router import router as checkup_router
    app.include_router(checkup_router)
"""

import secrets

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from Checkup_AI.chatbot import CheckupChatbot
from Checkup_AI.sample_data import SAMPLE_CHECKUPS, SAMPLE_DOCTORS

router = APIRouter(prefix="/checkup-chat", tags=["Checkup chatbot"])

# Chat sessions live in memory (fine for the hackathon demo; lost on restart).
_sessions: dict[str, CheckupChatbot] = {}


class StartChat(BaseModel):
    patient_id: str


class Question(BaseModel):
    question: str


def _get_session(session_id: str) -> CheckupChatbot:
    bot = _sessions.get(session_id)
    if bot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat session not found.")
    return bot


@router.post("/start", status_code=status.HTTP_201_CREATED)
def start_chat(body: StartChat):
    # TODO: replace the sample data with the real checkup + doctor tables.
    checkup = SAMPLE_CHECKUPS.get(body.patient_id)
    if checkup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No checkup found for this patient.")
    try:
        bot = CheckupChatbot(checkup, SAMPLE_DOCTORS)
    except RuntimeError as error:  # missing GEMINI_API_KEY
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))
    session_id = secrets.token_hex(16)
    _sessions[session_id] = bot
    return {
        "session_id": session_id,
        "patient_name": checkup.name,
        "questions_left": bot.questions_left,
    }


@router.post("/{session_id}/ask")
def ask_question(session_id: str, body: Question):
    return _get_session(session_id).ask(body.question).to_dict()


@router.post("/{session_id}/finish")
def finish_chat(session_id: str):
    """End the chat early and get the summary + assigned doctor."""
    summary = _get_session(session_id).finish()
    return {"summary": summary.to_dict(), "summary_text": summary.to_text()}
