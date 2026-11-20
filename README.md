# University Course Advisor (abdul-course-bot)

A chatbot for university students (prerequisites, credit hours, admissions, deadlines). It uses FastAPI WebSockets, Google Gemini with streaming, function calling, a small RAG knowledge base in ChromaDB, and a simple chat page.

## Features

- **Streaming chat:** replies appear word by word over a WebSocket (`/ws/chat`).
- **Memory:** each chat keeps its own history, so the bot remembers earlier turns.
- **Tool calling:** `check_prerequisites(code)` looks up a course in a mock catalog.
- **FAQ search (RAG):** `search_faq(query)` finds the closest of 15 FAQs in ChromaDB, and the bot answers only from them.

## Setup

Requires Python 3.10+ and a free Gemini API key from https://aistudio.google.com/apikey

```bash
git clone https://github.com/abdulrazaqkhan6070/abdul-course-bot.git
cd abdul-course-bot
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

On Mac/Linux, activate with `source .venv/bin/activate`.

1. Copy `.env.example` to `.env` and put your key in it: `GEMINI_API_KEY=your_key`
2. Build the knowledge base (once, and again if `faqs.json` changes): `python ingest.py`

## Run

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 for the chat page. Optional: `python test_client.py` runs a 3-question test in the terminal, and `python -m pytest -v` runs the unit tests.

## Try it

- `What are the prerequisites for CS301?` (tool call)
- `How many credit hours can I take in one semester?` (FAQ search)
- `What was my first question?` (memory)
- `Does the university offer free hostel accommodation?` (not in the FAQs, so the bot says it does not know)

## Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app: serves the page, `/ws/chat`, streaming, and the tool call loop |
| `index.html` | The chat page |
| `tools.py` | `check_prerequisites`, `search_faq`, and their JSON schemas |
| `ingest.py` | Embeds `faqs.json` into ChromaDB |
| `faqs.json` | 15 example FAQs (made-up policies and dates) |
| `bot.py` | Gemini client and system prompt |
| `test_client.py`, `test_tools.py` | Terminal demo client and unit tests |

Screenshots for each day are in `screenshots/`. Never commit `.env`.