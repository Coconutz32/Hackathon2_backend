"""Tests use a fake Gemini client, so no API key or network is needed.
Run with:  python -m pytest tests
"""

from Checkup_AI.chatbot import (
    ERROR_MESSAGE,
    REJECTION_MESSAGE,
    ChatAnswer,
    CheckupChatbot,
    DoctorHandoff,
)
from Checkup_AI.sample_data import SAMPLE_CHECKUPS, SAMPLE_DOCTORS


class FakeClient:
    def __init__(self, doctor_name="Dr. Ahmad Rahman", fail=False):
        self.doctor_name = doctor_name
        self.fail = fail
        self.calls = []

    def generate(self, system, messages, schema):
        self.calls.append((system, messages, schema))
        if self.fail:
            raise ConnectionError("no network")
        if schema is ChatAnswer:
            question = messages[-1]["text"]
            if "football" in question:
                return ChatAnswer(is_health_related=False, answer="")
            return ChatAnswer(is_health_related=True, answer=f"Answer to: {question}")
        return DoctorHandoff(
            checkup_overview="High blood pressure and cholesterol.",
            key_concerns=["BP 152/96"],
            doctor_name=self.doctor_name,
            doctor_reason="Heart risk factors.",
        )


def make_bot(client=None, max_questions=3):
    return CheckupChatbot(
        SAMPLE_CHECKUPS["P001"], SAMPLE_DOCTORS, client or FakeClient(), max_questions
    )


def test_health_question_is_answered_and_counted():
    bot = make_bot()
    reply = bot.ask("Is my blood pressure high?")
    assert not reply.rejected
    assert reply.answer == "Answer to: Is my blood pressure high?"
    assert reply.questions_left == 2
    assert reply.summary is None


def test_checkup_data_is_sent_to_the_model():
    client = FakeClient()
    make_bot(client).ask("Is my blood pressure high?")
    system = client.calls[0][0]
    assert "152/96 mmHg" in system and "Penicillin" in system


def test_unrelated_question_is_rejected_and_not_counted():
    client = FakeClient()
    bot = make_bot(client)
    reply = bot.ask("Who won the football match?")
    assert reply.rejected
    assert reply.answer == REJECTION_MESSAGE
    assert reply.questions_left == 3
    assert bot.conversation == []
    # the rejected question is not kept in the history of later calls
    bot.ask("What is LDL?")
    assert all("football" not in m["text"] for m in client.calls[-1][1])


def test_summary_after_max_questions():
    bot = make_bot()
    bot.ask("q1")
    bot.ask("q2")
    reply = bot.ask("q3")
    assert bot.is_finished and reply.summary is not None
    assert reply.summary.doctor.name == "Dr. Ahmad Rahman"
    assert len(reply.summary.conversation) == 3
    text = reply.summary.to_text()
    assert "Budi Santoso" in text and "152/96 mmHg" in text and "Dr. Ahmad Rahman" in text
    assert reply.to_dict()["finished"] is True
    # further questions do not call the model again
    assert bot.ask("q4").summary is reply.summary


def test_finish_early():
    bot = make_bot()
    bot.ask("q1")
    summary = bot.finish()
    assert len(summary.conversation) == 1
    assert bot.finish() is summary


def test_unknown_doctor_falls_back_to_general_practitioner():
    bot = make_bot(FakeClient(doctor_name="Dr. Nobody"))
    assert bot.finish().doctor.specialty == "General Practitioner"


def test_model_failure_is_handled():
    bot = make_bot(FakeClient(fail=True))
    reply = bot.ask("Is my blood pressure high?")
    assert reply.answer == ERROR_MESSAGE and reply.questions_left == 3
    summary = bot.finish()
    assert summary.doctor.specialty == "General Practitioner"
    assert "152/96 mmHg" in summary.to_text()
