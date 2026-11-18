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


def check_prerequisites(code: str) -> dict:
    """Return the title, credits and prerequisites for a course code."""
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
            }
        ]
    }
]

if __name__ == "__main__":
    print(check_prerequisites("CS301"))
    print(check_prerequisites("cs 101"))
    print(check_prerequisites("CS999"))