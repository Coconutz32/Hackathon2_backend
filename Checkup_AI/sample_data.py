"""Demo data so the chatbot can run before the real checkup database exists."""

from Checkup_AI.models import Doctor, PatientCheckup

SAMPLE_DOCTORS = [
    Doctor("Dr. Sarah Lim", "General Practitioner", "Mon-Fri 08:00-12:00"),
    Doctor("Dr. Ahmad Rahman", "Cardiologist (heart and blood pressure)", "Mon/Wed 13:00-17:00"),
    Doctor("Dr. Mei Tanaka", "Endocrinologist (diabetes and hormones)", "Tue/Thu 09:00-15:00"),
    Doctor("Dr. Daniel Cruz", "Pulmonologist (lungs and breathing)", "Fri 09:00-16:00"),
]

SAMPLE_CHECKUPS = {
    "P001": PatientCheckup(
        patient_id="P001",
        name="Budi Santoso",
        age=52,
        sex="male",
        checkup_date="2026-11-16",
        vitals={
            "Blood pressure": "152/96 mmHg",
            "Heart rate": "88 bpm",
            "Temperature": "36.7 C",
            "Weight": "86 kg",
            "Height": "170 cm",
        },
        lab_results={
            "Fasting blood sugar": "118 mg/dL",
            "Total cholesterol": "245 mg/dL",
            "LDL cholesterol": "165 mg/dL",
        },
        symptoms=["Occasional headaches in the morning", "Gets tired climbing stairs"],
        medical_history=["Father had a heart attack at 60", "Smoker for 20 years"],
        medications=[],
        allergies=["Penicillin"],
        nurse_notes="Patient reports high-salt diet and little exercise.",
    ),
    "P002": PatientCheckup(
        patient_id="P002",
        name="Siti Aminah",
        age=34,
        sex="female",
        checkup_date="2026-11-16",
        vitals={
            "Blood pressure": "112/74 mmHg",
            "Heart rate": "76 bpm",
            "Temperature": "36.5 C",
            "Weight": "58 kg",
            "Height": "160 cm",
        },
        lab_results={"Fasting blood sugar": "92 mg/dL", "Hemoglobin": "11.2 g/dL"},
        symptoms=["Mild fatigue"],
        medical_history=[],
        medications=["Iron supplement"],
        allergies=[],
        nurse_notes="Routine annual checkup.",
    ),
}
