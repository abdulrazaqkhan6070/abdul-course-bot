import chromadb

from ingest import COLLECTION_NAME, DB_PATH, embed_texts
# Mock course catalog. These are made-up courses used for the demo.
COURSES = {
    "CS101": {"title": "Introduction to Programming", "credits": 3, "prerequisites": []},
    "CS102": {"title": "Object-Oriented Programming", "credits": 3, "prerequisites": ["CS101"]},
    "CS201": {"title": "Data Structures", "credits": 3, "prerequisites": ["CS102"]},
    "CS202": {"title": "Database Systems", "credits": 3, "prerequisites": ["CS102"]},
    "CS301": {"title": "Algorithms", "credits": 3, "prerequisites": ["CS201", "MATH201"]},
    "CS401": {"title": "Machine Learning", "credits": 3, "prerequisites": ["CS301", "MATH202"]},
    "MATH101": {"title": "Calculus I", "credits": 3, "prerequisites": []},
    "MATH201": {"title": "Discrete Mathematics", "credits": 3, "prerequisites": ["MATH101"]},
    "MATH202": {"title": "Linear Algebra", "credits": 3, "prerequisites": ["MATH101"]},
}


def check_prerequisites(code) -> dict:
    """Return the title, credits and prerequisites for a course code.
    Never raises: bad input returns a clear 'found: False' result."""
    if not isinstance(code, str) or not code.strip():
        return {
            "found": False,
            "code": str(code),
            "message": "A course code is required, for example CS301.",
        }

    code = code.strip().upper().replace(" ", "")
    course = COURSES.get(code)

    if course is None:
        return {
            "found": False,
            "code": code,
            "message": f"No course with code {code} exists in the catalog.",
        }

    return {
        "found": True,
        "code": code,
        "title": course["title"],
        "credits": course["credits"],
        "prerequisites": course["prerequisites"],
    }

def search_faq(query, n_results: int = 3) -> dict:
    """Search the FAQ knowledge base and return the closest matching entries."""
    if not isinstance(query, str) or not query.strip():
        return {"found": False, "message": "A search query is required."}

    n_results = n_results if isinstance(n_results, int) and 1 <= n_results <= 5 else 3

    try:
        db = chromadb.PersistentClient(path=DB_PATH)
        collection = db.get_collection(COLLECTION_NAME)
    except Exception:
        return {"found": False, "message": "The FAQ database is not ready. Run ingest.py first."}

    # Questions use a different embedding setting than the stored documents
    vector = embed_texts([query.strip()], task_type="RETRIEVAL_QUERY")[0]
    hits = collection.query(query_embeddings=[vector], n_results=n_results)

    results = []
    for meta, distance in zip(hits["metadatas"][0], hits["distances"][0]):
        results.append(
            {
                "category": meta["category"],
                "question": meta["question"],
                "answer": meta["answer"],
                "distance": round(distance, 3),  # lower means a closer match
            }
        )

    if not results:
        return {"found": False, "message": "No FAQ entries matched."}
    return {"found": True, "results": results}

# JSON schema that tells Gemini this tool exists and how to call it
TOOLS = [
    {
        "function_declarations": [
            {
                "name": "check_prerequisites",
                "description": (
                    "Look up a university course by its code (for example CS301) "
                    "and return its title, credit hours, and the list of "
                    "prerequisite course codes. Use this whenever a student asks "
                    "what they need to take before a course."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The course code, for example CS301 or MATH201.",
                        }
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "search_faq",
                "description": (
                    "Search the university FAQ knowledge base about admissions, "
                    "credit hours, fees, and deadlines. Use this for any policy, "
                    "requirement, date, or fee question. Answer only from the "
                    "returned entries; if none of them answers the question, say "
                    "you do not have that information."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The student's question, in plain words.",
                        }
                    },
                    "required": ["query"],
                },
            },
        ]
    }
]

if __name__ == "__main__":
    print(check_prerequisites("CS301"))
    print(check_prerequisites("cs 101"))
    print(check_prerequisites("CS999"))