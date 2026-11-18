import asyncio
import json

from websockets.asyncio.client import connect

QUESTIONS = [
    "What are the prerequisites for CS301?",
    "And what about CS401?",
    "Is there a course called CS999?",
]


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
                    print(f"[Tool result] {msg['result']}")
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