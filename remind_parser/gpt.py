from g4f.Provider import Aichatos
from g4f.client import Client

client = Client(provider=Aichatos)

promt = '''
Provide answer IN RUSSIAN
In this text transcription of a voice message, highlight all the events that need to be reminded about.
Each reminder should be on a new line.
For each event, form a reminder in the format "напомни [reminder time] [reminder text]". Only this text.
If the transcription is inaccurate, correct the reminder text to make it logical and grammatically correct.
If there is no informative reminder in the text, return "Error".
Reminders should not be repeated.
FOLLOW the restrictions below.

RESTRICTIONS for setting the time:
- Use specific time instead of words in the format "hh:mm".
- When mentioning the time of day, use exact time.
- Invent the time if it is not specified exactly, minimize words.

Examples:

Original text: "Go to dinner in the evening"
Expected output:
remind at 18:00 go to dinner

Original text: "Today at 18:00 meeting with a friend. Tomorrow morning need to submit documents to the tax office. In two days, a trip to the office is scheduled at 14:00."
Expected output:
remind today at 18:00 meeting with a friend
remind in two days at 14:00 trip to the office

Original text: "Don't forget to have breakfast tomorrow at 8 am. Also, tomorrow evening, at 7:00 pm, we have dinner with colleagues. In three days, you need to pay for utilities."
Expected output:
remind tomorrow at 08:00 have breakfast
remind tomorrow at 19:00 dinner with colleagues
remind in three days pay for utilities

Original text: "Just wanted to remind you that you are the best!"
Expected output:
Error


Text for analysis:

{text}
'''


def remind_summary(text: str) -> str:
    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": promt.format(text=text)}]
    )

    summary = chat_completion.choices[0].message.content or ""
    return summary


if __name__ == "__main__":
    while True:
        content = input("Типа расшифровка: ")
        print(remind_summary(content))

