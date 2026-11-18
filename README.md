# University Course Advisor (abdul-course-bot)

An AI chatbot that helps university students with course prerequisites, credit hours, admissions questions, and deadlines. It uses Google Gemini with a custom "course advisor" system persona, served over a FastAPI WebSocket with streaming replies and function calling.

## Status

- **Day 1:** repo setup and a basic script (`bot.py`) that sends one question to the LLM and prints the reply.
- **Day 2:** FastAPI WebSocket endpoint `/ws/chat` with in-memory conversation history and chunk-by-chunk streaming.
- **Day 3:** function calling with one custom tool, `check_prerequisites(code)`, backed by a mock course catalog.

Planned next: 15 FAQs on admissions, credits and deadlines.

## Tech Stack

- Python 3.10+
- FastAPI and Uvicorn
- WebSockets
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

**Day 1: single question script**

```bash
python bot.py
```

**Day 2 and 3: streaming chat server with tool calling**

1. Start the server in one terminal:

```bash
uvicorn main:app --reload
```

2. In a second terminal (with the venv activated), run the test client:

```bash
python test_client.py
```

The test client opens one WebSocket connection and sends 3 questions about course prerequisites (CS301, CS401, and a course that does not exist, CS999). For each turn it prints the tool call, the data the tool returned, and the streamed answer.

## Function Calling (Day 3)

The bot has one tool, `check_prerequisites(code)`, defined in `tools.py`. It looks a course code up in a mock catalog (a Python dictionary of made-up courses) and returns the title, credit hours, and prerequisite codes. If the code does not exist, it returns a "not found" result so the bot can say so instead of inventing details.

How the tool call loop works in `main.py`:

1. The conversation is sent to Gemini together with the tool's JSON schema.
2. If Gemini asks for the tool, the server runs the matching Python function and sends the result back to the model.
3. Gemini writes the final answer from the tool result, and the text is streamed to the client.
4. If the model needs more lookups, the loop repeats, up to a safety limit of 5 rounds.

Mock catalog (for testing): CS101, CS102, CS201, CS202, CS301, CS401, MATH101, MATH201, MATH202.

## WebSocket API

Endpoint: `ws://127.0.0.1:8000/ws/chat`

The client sends plain text messages. The server replies with JSON messages:

| Message | Meaning |
|---|---|
| `{"type": "tool_call", "name": "...", "args": {...}}` | The model asked to run a tool |
| `{"type": "tool_result", "name": "...", "result": {...}}` | The data the tool returned |
| `{"type": "chunk", "text": "..."}` | A piece of the reply, sent as soon as it is generated |
| `{"type": "done"}` | The reply is finished |
| `{"type": "error", "text": "..."}` | Something went wrong (for example, the model is busy) |

Each connection keeps its own in-memory `messages` list, so the bot remembers previous turns within the same chat. The history is lost when the connection closes. If Gemini returns a 503 (high demand), the server retries automatically before giving up.

## Project Structure

```
abdul-course-bot/
├── bot.py             # Gemini client and advisor system persona (Day 1 script)
├── main.py            # FastAPI app: /ws/chat streaming endpoint and tool call loop
├── tools.py           # Mock course catalog, check_prerequisites, and the tool schema
├── test_client.py     # 3-turn streaming test client that shows tool calls
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── .gitignore         # Files Git should not track
├── screenshots/       # Terminal screenshots for each day
└── README.md
```

## Notes

Never commit your real `.env` file. It is listed in `.gitignore`.