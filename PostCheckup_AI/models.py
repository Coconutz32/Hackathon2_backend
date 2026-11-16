"""Data classes for the post-checkup AI (target: the patient)."""

from dataclasses import asdict, dataclass, field


@dataclass
class DoctorNote:
    """What the doctor wrote after the checkup. This is the AI's only source."""

    visit_id: str
    patient_name: str
    patient_age: int
    doctor_name: str
    visit_date: str
    diagnosis: str
    advice: str  # the original doctor summary / advice, as written
    prescriptions: list[str] = field(default_factory=list)
    follow_up: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "DoctorNote":
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_text(self) -> str:
        prescriptions = "\n".join(f"  - {p}" for p in self.prescriptions) or "  - none"
        return "\n".join(
            [
                f"Patient: {self.patient_name}, {self.patient_age} years old",
                f"Doctor: {self.doctor_name}",
                f"Visit date: {self.visit_date}",
                f"Diagnosis: {self.diagnosis}",
                f"Doctor's advice: {self.advice}",
                f"Prescriptions:\n{prescriptions}",
                f"Follow-up: {self.follow_up or 'none'}",
            ]
        )


@dataclass
class PlanTask:
    """One step of the actionable plan (can feed the habit planner / tracker)."""

    task_id: str
    title: str
    description: str
    frequency: str  # "once" | "daily" | "weekly" | "as_needed"


@dataclass
class PostCheckupReport:
    """Shown to the patient after the checkup."""

    note: DoctorNote  # original doctor summary
    simple_summary: str  # easier-to-understand version
    key_points: list[str]
    plan: list[PlanTask]  # actionable plan
    ai_generated: bool = True  # False if Gemini failed and only the note is shown

    def to_dict(self) -> dict:
        return asdict(self)

    def to_text(self) -> str:
        points = "\n".join(f"  - {p}" for p in self.key_points) or "  - none"
        plan = (
            "\n".join(
                f"  [{t.task_id}] {t.title} ({t.frequency})\n       {t.description}"
                for t in self.plan
            )
            or "  (no tasks)"
        )
        return "\n".join(
            [
                "========== ORIGINAL DOCTOR SUMMARY ==========",
                self.note.to_text(),
                "",
                "========== EASY-TO-UNDERSTAND SUMMARY ==========",
                self.simple_summary,
                f"Key points:\n{points}",
                "",
                "========== YOUR ACTION PLAN ==========",
                plan,
                "==============================================",
            ]
        )

