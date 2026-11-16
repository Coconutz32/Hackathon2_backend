"""Try the post-checkup AI in the terminal:  python post_checkup_terminal.py [visit_id]"""

import sys

from dotenv import load_dotenv

from PostCheckup_AI import PostCheckupAI
from PostCheckup_AI.sample_data import SAMPLE_NOTES


def main():
    load_dotenv()
    visit_id = sys.argv[1] if len(sys.argv) > 1 else "V001"
    note = SAMPLE_NOTES.get(visit_id)
    if note is None:
        sys.exit(f"Unknown visit id. Available: {', '.join(SAMPLE_NOTES)}")

    ai = PostCheckupAI(note)
    print(ai.build_report().to_text())
    print("\nAsk me anything about your doctor's advice. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit", "done"):
            break
        print(f"Assistant: {ai.ask(question).answer}\n")


if __name__ == "__main__":
    main()
