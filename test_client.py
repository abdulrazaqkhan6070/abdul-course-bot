import asyncio
import json

from websockets.asyncio.client import connect

QUESTIONS = [
    "How many credit hours can I take in one semester, and what if I want more than the limit?",
    "When is the last date to register for Spring 2027 courses?",
    "Does the university offer free hostel accommodation for all students?",
]


def show_tool_result(msg):
    result = msg["result"]
    if msg["name"] == "search_faq" and result.get("found"):
        top = result["results"][0]
        print(f"[Tool result] search_faq found {len(result['results'])} entries")
        print(f"              best match: \"{top['question']}\" (distance {top['distance']})")
    else:
        print(f"[Tool result] {result}")


async def main():
    async with connect("ws://127.0.0.1:8000/ws/chat") as ws:
        for turn, question in enumerate(QUESTIONS, 1):
            print(f"\n--- Turn {turn} ---")
            print(f"Student: {question}")
            await ws.send(question)

            advisor_started = False
            while True:
                msg = json.loads(await ws.recv())

                if msg["type"] == "tool_call":
                    print(f"[Tool call]   {msg['name']}({msg['args']})")
                elif msg["type"] == "tool_result":
                    show_tool_result(msg)
                elif msg["type"] == "chunk":
                    if not advisor_started:
                        print("Advisor: ", end="", flush=True)
                        advisor_started = True
                    print(msg["text"], end="", flush=True)
                elif msg["type"] == "done":
                    print()
                    break
                elif msg["type"] == "error":
                    print(f"\n[error] {msg['text']}")
                    break


asyncio.run(main())