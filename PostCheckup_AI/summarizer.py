"""Post-checkup AI (target: the patient).

Purpose: help the patient understand the doctor's advice. It takes the
original doctor summary and produces:
  1. an easier-to-understand summary,
  2. an actionable plan (list of tasks).
"""

import os
from typing import Literal

from pydantic import BaseModel, Field

from PostCheckup_AI.models import DoctorNote, PlanTask, PostCheckupReport

DEFAULT_MODEL = "gemini-3.8-flash-lite"

SUMMARY_UNAVAILABLE = (
    "The simplified summary is not available right now. "
    "Please read the original doctor summary above."
)


# ---- Shapes the model must answer in (Gemini structured output) ----
class TaskDraft(BaseModel):
    title: str = Field(description="Short action, e.g. 'Take Amlodipine 5 mg'.")
    description: str = Field(description="How and when to do it, in simple words.")
    frequency: Literal["once", "daily", "weekly", "as_needed"]


class ReportDraft(BaseModel):
    simple_summary: str = Field(
        description="The doctor's note explained in simple everyday words, 3-6 sentences."
    )
    key_points: list[str] = Field(description="3-5 most important things to remember.")
    tasks: list[TaskDraft] = Field(
        description="Concrete steps the patient should do, taken only from the doctor's note."
    )


class GeminiClient:
    """Thin wrapper around the Gemini SDK that returns validated JSON objects."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        from google import genai  # imported here so tests can run without the SDK

        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Set the GEMINI_API_KEY environment variable")
        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self._client = genai.Client(api_key=api_key)

    def generate(self, system: str, messages: list[dict], schema: type[BaseModel]) -> BaseModel:
        """messages: [{"role": "user" | "model", "text": "..."}]"""
        from google.genai import types

        response = self._client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(role=m["role"], parts=[types.Part(text=m["text"])])
                for m in messages
            ],
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.2,
            ),
        )
        return schema.model_validate_json(response.text)


class PostCheckupAI:
    """Turns one doctor note into a patient-friendly report."""

    def __init__(self, note: DoctorNote, client: GeminiClient | None = None):
        self.note = note
        self.client = client or GeminiClient()
        self.report: PostCheckupReport | None = None

    def build_report(self) -> PostCheckupReport:
        """Original doctor summary + easy summary + actionable plan.
        Built once; later calls return the same report."""
        if self.report is not None and self.report.ai_generated:
            return self.report

        try:
            draft = self.client.generate(
                self._report_system_prompt(),
                [{"role": "user", "text": f"Doctor's note:\n{self.note.to_text()}"}],
                ReportDraft,
            )
        except Exception:
            # Never invent advice: on failure the patient still sees the original note.
            self.report = PostCheckupReport(self.note, SUMMARY_UNAVAILABLE, [], [], False)
            return self.report

        plan = [
            PlanTask(f"T{i}", t.title.strip(), t.description.strip(), t.frequency)
            for i, t in enumerate(draft.tasks, start=1)
        ]
        self.report = PostCheckupReport(
            self.note, draft.simple_summary.strip(), draft.key_points, plan
        )
        return self.report

    def _report_system_prompt(self) -> str:
        return """You help a patient understand what their doctor told them after a checkup.

Rules:
1. Use ONLY the doctor's note. Do not add new medical advice, medicines, doses, or \
diagnoses that the doctor did not write.
2. simple_summary: explain the note in simple everyday words, as if to someone with \
no medical knowledge. Explain any medical term the first time you use it.
3. tasks: turn the doctor's advice, prescriptions and follow-up into clear steps the \
patient can do. One action per task. Keep doses and timings exactly as the doctor wrote.
4. If the note has nothing actionable, return an empty task list.
5. Write in the same language as the doctor's note."""
