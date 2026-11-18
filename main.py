import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.genai import errors, types

from bot import client, SYSTEM_PROMPT
from tools import TOOLS, check_prerequisites

MODEL = "gemini-3.8-flash"
MAX_TOOL_ROUNDS = 5  # safety limit so the loop can never run forever

# Maps the tool name Gemini uses to the real Python function
TOOL_FUNCTIONS = {"check_prerequisites": check_prerequisites}

app = FastAPI(title="University Course Advisor")


async def stream_one_round(websocket: WebSocket, messages, attempts=6):
    """One Gemini call. Streams text to the client as it arrives.
    Returns (all_parts, tool_calls). Retries on 503 if no text was sent yet."""
    for attempt in range(attempts):
        parts = []
        sent_text = False
        try:
            stream = await client.aio.models.generate_content_stream(
                model=MODEL,
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                    tools=TOOLS,
                ),
            )
            async for chunk in stream:
                if not chunk.candidates or not chunk.candidates[0].content:
                    continue
                for part in chunk.candidates[0].content.parts or []:
                    parts.append(part)
                    if part.text:
                        sent_text = True
                        await websocket.send_json({"type": "chunk", "text": part.text})
            tool_calls = [p.function_call for p in parts if p.function_call]
            return parts, tool_calls
        except errors.ServerError:
            if sent_text or attempt == attempts - 1:
                raise
            wait = 2 ** (attempt + 1)
            print(f"Gemini busy, retrying in {wait}s...")
            await asyncio.sleep(wait)


async def stream_reply(websocket: WebSocket, messages):
    """Run the tool call loop. Adds every model turn and tool result to messages."""
    for _ in range(MAX_TOOL_ROUNDS):
        parts, tool_calls = await stream_one_round(websocket, messages)
        if not parts:
            raise RuntimeError("Empty reply from the model")
        messages.append(types.Content(role="model", parts=parts))

        if not tool_calls:
            return  # plain text answer, we are done

        response_parts = []
        for call in tool_calls:
            args = dict(call.args or {})
            print(f"Tool call: {call.name}({args})")
            await websocket.send_json(
                {"type": "tool_call", "name": call.name, "args": args}
            )

            func = TOOL_FUNCTIONS.get(call.name)
            result = func(**args) if func else {"error": f"Unknown tool {call.name}"}

            await websocket.send_json(
                {"type": "tool_result", "name": call.name, "result": result}
            )
            response_parts.append(
                types.Part.from_function_response(
                    name=call.name, response={"result": result}
                )
            )

        # Hand the tool results back to Gemini, then loop for its next answer
        messages.append(types.Content(role="user", parts=response_parts))

    raise RuntimeError("Too many tool calls in a row")


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
            start = len(messages)
            messages.append(
                types.Content(role="user", parts=[types.Part(text=user_text)])
            )

            try:
                await stream_reply(websocket, messages)
            except WebSocketDisconnect:
                raise
            except Exception as e:
                del messages[start:]  # roll back this whole turn so history stays clean
                await websocket.send_json({"type": "error", "text": str(e)})
                continue

            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        print("Client disconnected")