# University Course Advisor (abdul-course-bot)

An AI chatbot that helps university students with course prerequisites, credit hours, admissions questions, and deadlines. It uses Google Gemini with a custom "course advisor" system persona, served over a FastAPI WebSocket with streaming replies, function calling, and a small RAG knowledge base (ChromaDB).

## Status

- **Day 1:** repo setup and a basic script (`bot.py`) that sends one question to the LLM and prints the reply.
- **Day 2:** FastAPI WebSocket endpoint `/ws/chat` with in-memory conversation history and chunk-by-chunk streaming.
- **Day 3:** function calling with one custom tool, `check_prerequisites(code)`, backed by a mock course catalog, plus input validation and unit tests.
- **Day 4:** mini knowledge base (RAG): 15 FAQs in `faqs.json`, embedded with Gemini and stored in a local ChromaDB, searched by a new `search_faq` tool.

## Tech Stack

- Python 3.10+
- FastAPI and Uvicorn
- WebSockets
- Google Gemini via the `google-genai` SDK (chat and embeddings)
- ChromaDB (local vector store)
- python-dotenv for loading the API key
- pytest for unit tests

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

5. Build the knowledge base (needed once, and again whenever `faqs.json` changes):

```bash
python ingest.py
```

## Usage

**Day 1: single question script**

```bash
python bot.py
```

**Streaming chat server with tools and RAG**

1. Start the server in one terminal:

```bash
uvicorn main:app --reload
```

2. In a second terminal (with the venv activated), run the test client:

```bash
python test_client.py
```

The test client opens one WebSocket connection and sends 3 policy questions. For each turn it prints the tool call, a summary of the search result, and the streamed answer. The third question is about something that is not in the FAQs, to show that the bot says it does not know instead of inventing an answer.

## Tools

The bot has two tools, both declared with a JSON schema in `tools.py`:

| Tool | What it does |
|---|---|
| `check_prerequisites(code)` | Looks a course code up in a mock catalog and returns its title, credit hours, and prerequisites. Unknown or invalid codes return a "not found" result. |
| `search_faq(query)` | Searches the FAQ knowledge base by meaning and returns the closest entries. |

How the tool call loop works in `main.py`:

1. The conversation is sent to Gemini together with the tool schemas.
2. If Gemini asks for a tool, the server runs the matching Python function (in a worker thread, so the server is not blocked) and sends the result back to the model.
3. Gemini writes the final answer from the tool result, and the text is streamed to the client.
4. If the model needs more lookups, the loop repeats, up to a safety limit of 5 rounds.

Tool calls run through a safe helper (`run_tool`), so malformed or unexpected arguments return an error result instead of crashing the chat.

## Knowledge Base (RAG)

- `faqs.json` holds 15 short question and answer pairs about admissions, credits, and deadlines. The policies, fees, and dates in it are made-up examples for the demo.
- `ingest.py` embeds each FAQ with the Gemini embedding model (`gemini-embedding-001`, 768 dimensions) and stores it in a local ChromaDB collection (the `chroma_db/` folder, not committed to Git).
- `search_faq` embeds the student's question, asks ChromaDB for the closest FAQs (cosine distance, lower means a closer match), and returns them to the model.
- The system prompt tells the bot to answer policy questions only from the returned entries, and to say it does not have the information when nothing matches.

## Testing

Unit tests for the tool function live in `test_tools.py`. They do not need the server or an API call:

```bash
python -m pytest -v
```

`pytest.ini` limits pytest to `test_tools.py`. The file `test_client.py` is a live demo client, not a unit test.

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
├── bot.py             # Gemini client and advisor system prompt
├── main.py            # FastAPI app: /ws/chat streaming endpoint and tool call loop
├── tools.py           # check_prerequisites, search_faq, and the tool schemas
├── faqs.json          # 15 FAQ pairs (the knowledge base source)
├── ingest.py          # Embeds the FAQs and stores them in ChromaDB
├── test_tools.py      # Unit tests for the tools
├── pytest.ini         # Limits pytest to test_tools.py
├── test_client.py     # 3-turn streaming test client that shows tool calls
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── .gitignore         # Files Git should not track
├── screenshots/       # Terminal screenshots for each day
└── README.md
```

## Notes

Never commit your real `.env` file. It is listed in `.gitignore`, along with the generated `chroma_db/` folder.