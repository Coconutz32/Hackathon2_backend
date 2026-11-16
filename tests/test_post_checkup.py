"""Tests use a fake Gemini client, so no API key or network is needed.
Run with:  python -m pytest tests
"""

from PostCheckup_AI.summarizer import (
    SUMMARY_UNAVAILABLE,
    PostCheckupAI,
    ReportDraft,
    TaskDraft,
)
from PostCheckup_AI.sample_data import SAMPLE_NOTES


class FakeClient:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def generate(self, system, messages, schema):
        self.calls.append((system, messages, schema))
        if self.fail:
            raise ConnectionError("no network")
        return ReportDraft(
            simple_summary="Your blood pressure and cholesterol are too high.",
            key_points=["Take your medicine every day"],
            tasks=[
                TaskDraft(title="Take Amlodipine 5 mg", description="Every morning.", frequency="daily"),
                TaskDraft(title="Book follow-up", description="In 4 weeks.", frequency="once"),
            ],
        )


def make_ai(client=None):
    return PostCheckupAI(SAMPLE_NOTES["V001"], client or FakeClient())


def test_report_has_original_note_easy_summary_and_plan():
    client = FakeClient()
    ai = make_ai(client)
    report = ai.build_report()
    assert report.note is SAMPLE_NOTES["V001"]
    assert report.simple_summary == "Your blood pressure and cholesterol are too high."
    assert [t.task_id for t in report.plan] == ["T1", "T2"]
    assert report.plan[0].frequency == "daily"
    # the doctor's note is what the model was given
    assert "Amlodipine 5 mg" in client.calls[0][1][0]["text"]
    text = report.to_text()
    assert "Stage 2 hypertension" in text and "[T2] Book follow-up (once)" in text
    assert report.to_dict()["plan"][0]["task_id"] == "T1"
    # built only once
    assert ai.build_report() is report and len(client.calls) == 1


def test_report_failure_still_shows_original_note():
    report = make_ai(FakeClient(fail=True)).build_report()
    assert report.ai_generated is False
    assert report.simple_summary == SUMMARY_UNAVAILABLE and report.plan == []
    assert "Atorvastatin 20 mg" in report.to_text()

