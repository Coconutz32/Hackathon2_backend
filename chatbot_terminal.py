"""Try the checkup chatbot in the terminal:  python chatbot_terminal.py [patient_id]"""

import sys

from dotenv import load_dotenv

from Checkup_AI import CheckupChatbot
from Checkup_AI.sample_data import SAMPLE_CHECKUPS, SAMPLE_DOCTORS


def main():
    load_dotenv()
    patient_id = sys.argv[1] if len(sys.argv) > 1 else "P001"
    checkup = SAMPLE_CHECKUPS.get(patient_id)
    if checkup is None:
        sys.exit(f"Unknown patient id. Available: {', '.join(SAMPLE_CHECKUPS)}")

    bot = CheckupChatbot(checkup, SAMPLE_DOCTORS)
    print(f"Hello {checkup.name}! I have read your checkup results.")
    print(
        f"You can ask up to {bot.max_questions} health questions before meeting "
        "the doctor. Type 'done' when you have no more questions.\n"
    )

    while not bot.is_finished:
        question = input("You: ").strip()
        if question.lower() in ("done", "exit", "quit"):
            bot.finish()
            break
        reply = bot.ask(question)
        print(f"Assistant: {reply.answer}")
        if not bot.is_finished:
            print(f"({reply.questions_left} question(s) left)\n")

    print("\n" + bot.summary.to_text())


if __name__ == "__main__":
    main()
