"""Data classes shared by the checkup chatbot (AI #1) and the doctor side (AI #2)."""

from dataclasses import asdict, dataclass, field


@dataclass
class Doctor:
    name: str
    specialty: str
    schedule: str = ""


@dataclass
class PatientCheckup:
    """Everything recorded during the checkup the patient does before the visit."""

    patient_id: str
    name: str
    age: int
    sex: str
    checkup_date: str
    vitals: dict[str, str] = field(default_factory=dict)
    lab_results: dict[str, str] = field(default_factory=dict)
    symptoms: list[str] = field(default_factory=list)
    medical_history: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    nurse_notes: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "PatientCheckup":
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_text(self) -> str:
        """Readable version of the checkup, used in prompts and in the summary."""

        def block(title: str, items) -> str:
            if not items:
                return f"{title}: none recorded"
            if isinstance(items, dict):
                lines = [f"  - {key}: {value}" for key, value in items.items()]
            else:
                lines = [f"  - {item}" for item in items]
            return f"{title}:\n" + "\n".join(lines)

        return "\n".join(
            [
                f"Patient: {self.name} (ID {self.patient_id}), {self.age} years old, {self.sex}",
                f"Checkup date: {self.checkup_date}",
                block("Vitals", self.vitals),
                block("Lab results", self.lab_results),
                block("Symptoms", self.symptoms),
                block("Medical history", self.medical_history),
                block("Current medications", self.medications),
                block("Allergies", self.allergies),
                f"Nurse notes: {self.nurse_notes or 'none'}",
            ]
        )


@dataclass
class QuestionAnswer:
    question: str
    answer: str


@dataclass
class PreVisitSummary:
    """Final result of the chat: shown to the patient and sent to the doctor."""

    checkup: PatientCheckup
    doctor: Doctor
    doctor_reason: str
    checkup_overview: str
    key_concerns: list[str]
    conversation: list[QuestionAnswer]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_text(self) -> str:
        concerns = "\n".join(f"  - {c}" for c in self.key_concerns) or "  - none"
        questions = (
            "\n".join(
                f"  Q{i}: {qa.question}\n  A{i}: {qa.answer}"
                for i, qa in enumerate(self.conversation, start=1)
            )
            or "  (no questions asked)"
        )
        doctor_line = f"{self.doctor.name} - {self.doctor.specialty}"
        if self.doctor.schedule:
            doctor_line += f" ({self.doctor.schedule})"
        return "\n".join(
            [
                "========== PRE-VISIT SUMMARY ==========",
                self.checkup.to_text(),
                "",
                f"Overview: {self.checkup_overview}",
                f"Key concerns for the doctor:\n{concerns}",
                "",
                f"Questions asked before the visit:\n{questions}",
                "",
                f"Your doctor: {doctor_line}",
                f"Why this doctor: {self.doctor_reason}",
                "=======================================",
            ]
        )
