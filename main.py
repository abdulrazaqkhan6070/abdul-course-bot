import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.genai import errors, types

from bot import client, SYSTEM_PROMPT

MODEL = "gemini-3.8-flash"

app = FastAPI(title="University Course Advisor")


async def stream_reply(websocket: WebSocket, messages, attempts=4) -> str:
    """Stream Gemini's reply to the client chunk by chunk and return the full text.
    On a 503, retry only if nothing has been sent yet."""
    for attempt in range(attempts):
        full_text = ""
        try:
            stream = await client.aio.models.generate_content_stream(
                model=MODEL,
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                ),
            )
            async for chunk in stream:
                if chunk.text:
                    full_text += chunk.text
                    await websocket.send_json({"type": "chunk", "text": chunk.text})
            return full_text
        except errors.ServerError:
            if full_text or attempt == attempts - 1:
                raise
            wait = 2 ** (attempt + 1)
            print(f"Gemini busy, retrying in {wait}s...")
            await asyncio.sleep(wait)


@app.get("/")
def root():
    return {"status": "ok", "service": "abdul-course-bot"}


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    messages = []  # in-memory history for this chat only

    try:
        while True:
            user_text = await websocket.receive_text()
            messages.append(
                types.Content(role="user", parts=[types.Part(text=user_text)])
            )

            try:
                reply = await stream_reply(websocket, messages)
            except WebSocketDisconnect:
                raise
            except Exception as e:
                messages.pop()  # drop the failed question so history stays clean
                await websocket.send_json({"type": "error", "text": str(e)})
                continue

            messages.append(
                types.Content(role="model", parts=[types.Part(text=reply)])
            )
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        print("Client disconnected")