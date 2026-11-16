import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load GEMINI_API_KEY from the .env file
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# The system persona: tells the model who it is and how to behave
SYSTEM_PROMPT = """You are Abdul's University Course Advisor, a friendly and accurate
assistant for university students. You help with course prerequisites, credit hours,
admissions questions, and deadlines. Keep answers short and clear. If you are not sure
about a university-specific rule, say so and suggest the student check with the
registrar or department office. Never invent course codes or dates."""


def ask_advisor(question: str) -> str:
    """Send one question to Gemini with the advisor persona and return the reply."""
    response = client.models.generate_content(
            model="gemini-3.8-flash",
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
        ),
    )
    return response.text


if __name__ == "__main__":
    question = "How many credit hours should a student usually take in one semester?"
    print(f"Student: {question}\n")
    print(f"Advisor: {ask_advisor(question)}")