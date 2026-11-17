import asyncio
import json

from websockets.asyncio.client import connect

QUESTIONS = [
    "Hi, my name is Abdul and I study Computer Science.",
    "How many credit hours do I usually need per semester?",
    "What is my name and what do I study?",
]


async def main():
    async with connect("ws://127.0.0.1:8000/ws/chat") as ws:
        for turn, question in enumerate(QUESTIONS, 1):
            print(f"\n--- Turn {turn} ---")
            print(f"Student: {question}")
            print("Advisor: ", end="", flush=True)
            await ws.send(question)

            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "chunk":
                    print(msg["text"], end="", flush=True)
                elif msg["type"] == "done":
                    print()
                    break
                elif msg["type"] == "error":
                    print(f"\n[error] {msg['text']}")
                    break


asyncio.run(main())
