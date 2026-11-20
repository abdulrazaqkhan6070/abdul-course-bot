# University Course Advisor (abdul-course-bot)

A chatbot for university students (prerequisites, credits, admissions, deadlines), built with FastAPI WebSockets, Google Gemini, function calling, and a small RAG knowledge base in ChromaDB.

## Progress

- **Day 1:** repo setup and a basic LLM script (`bot.py`).
- **Day 2:** WebSocket endpoint `/ws/chat` with in-memory history and streaming.
- **Day 3:** function calling with `check_prerequisites(code)` on a mock catalog, plus unit tests.
- **Day 4:** RAG: 15 FAQs in `faqs.json`, embedded with Gemini into ChromaDB, searched by a `search_faq` tool.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`. Then build the knowledge base once:

```bash
python ingest.py
```

## Run

```bash
uvicorn main:app --reload
python test_client.py
```

`test_client.py` sends 3 questions over the WebSocket and prints each tool call and the streamed answer. Unit tests: `python -m pytest -v`.

## How it works

- `main.py`: `/ws/chat` keeps the chat history, streams replies, and runs the tool call loop (max 5 rounds) through a safe helper `run_tool`.
- `tools.py`: `check_prerequisites` and `search_faq`, with their JSON schemas.
- `ingest.py`: embeds `faqs.json` and stores it in ChromaDB (`chroma_db/`, not committed).
- `search_faq` finds the closest FAQs by meaning; the bot answers only from them, or says it does not know.

Server messages are JSON: `tool_call`, `tool_result`, `chunk`, `done`, `error`.

Screenshots for each day are in `screenshots/`. Never commit `.env`.