import json
import sys

import chromadb
from google.genai import errors, types

from bot import client

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIMENSIONS = 768
FAQ_FILE = "faqs.json"
DB_PATH = "chroma_db"
COLLECTION_NAME = "faqs"


def load_faqs(path: str = FAQ_FILE) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def embed_texts(texts: list[str], task_type: str) -> list[list[float]]:
    """Turn a list of texts into a list of embedding vectors."""
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBED_DIMENSIONS,
        ),
    )
    return [e.values for e in response.embeddings]


def build_index() -> int:
    """Embed every FAQ and store it in a fresh ChromaDB collection."""
    faqs = load_faqs()
    # Embed question and answer together so either one can match a search
    texts = [f"{faq['question']}\n{faq['answer']}" for faq in faqs]
    vectors = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")

    db = chromadb.PersistentClient(path=DB_PATH)
    try:
        db.delete_collection(COLLECTION_NAME)  # start clean so re-running never duplicates
    except Exception:
        pass
    collection = db.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # compare by meaning, not length
    )
    collection.add(
        ids=[faq["id"] for faq in faqs],
        embeddings=vectors,
        documents=texts,
        metadatas=[
            {
                "category": faq["category"],
                "question": faq["question"],
                "answer": faq["answer"],
            }
            for faq in faqs
        ],
    )
    return collection.count()


if __name__ == "__main__":
    try:
        count = build_index()
    except errors.APIError as e:
        print(f"Could not embed the FAQs: {e}")
        sys.exit(1)
    print(f"Stored {count} FAQs in ChromaDB ({DB_PATH}/)")