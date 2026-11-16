# University Course Advisor (abdul-course-bot)

An AI chatbot that helps university students with course prerequisites, credit hours, admissions questions, and deadlines. It uses Google Gemini with a custom "course advisor" system persona.

## Status

Day 1: repo setup and a basic script that sends one question to the LLM and prints the reply.

Planned next: a `check_prerequisites(code)` function and 15 FAQs on admissions, credits and deadlines.

## Tech Stack

- Python 3.10+
- FastAPI and Uvicorn (for the API, coming in later days)
- Google Gemini via the `google-genai` SDK
- python-dotenv for loading the API key

## Setup

1. Clone the repo:

```bash
git clone https://github.com/abdulrazaqkhan6070/abdul-course-bot.git
cd abdul-course-bot
```

2. Create and activate a virtual environment (Windows):

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

On Mac/Linux, use `source .venv/bin/activate` instead.

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create your `.env` file by copying `.env.example`, then add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

You can get a free key at https://aistudio.google.com/apikey

## Usage

```bash
python bot.py
```

The script sends a sample question to the advisor bot and prints the reply.

## Project Structure

```
abdul-course-bot/
├── bot.py             # Basic LLM script with the advisor persona
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── .gitignore         # Files Git should not track
└── README.md
```

## Notes

Never commit your real `.env` file. It is listed in `.gitignore`.