import pytest

from tools import COURSES, TOOLS, check_prerequisites


def test_known_course_returns_details():
    result = check_prerequisites("CS301")
    assert result["found"] is True
    assert result["code"] == "CS301"
    assert result["title"] == "Algorithms"
    assert result["credits"] == 3


def test_course_with_no_prerequisites():
    result = check_prerequisites("CS101")
    assert result["found"] is True
    assert result["prerequisites"] == []


def test_course_with_multiple_prerequisites():
    result = check_prerequisites("CS401")
    assert result["prerequisites"] == ["CS301", "MATH202"]


@pytest.mark.parametrize("code", ["CS301", "cs301", " cs 301 ", "Cs301"])
def test_code_is_case_and_space_insensitive(code):
    result = check_prerequisites(code)
    assert result["found"] is True
    assert result["code"] == "CS301"


def test_unknown_course_is_not_found():
    result = check_prerequisites("CS999")
    assert result["found"] is False
    assert "CS999" in result["message"]


@pytest.mark.parametrize("bad_input", ["", "   ", None, 301, []])
def test_bad_input_does_not_crash(bad_input):
    result = check_prerequisites(bad_input)
    assert result["found"] is False
    assert "message" in result


def test_every_prerequisite_exists_in_catalog():
    for code, course in COURSES.items():
        for prereq in course["prerequisites"]:
            assert prereq in COURSES, f"{code} lists unknown prerequisite {prereq}"


def test_tool_schema_matches_function():
    declaration = TOOLS[0]["function_declarations"][0]
    assert declaration["name"] == "check_prerequisites"
    assert declaration["parameters"]["required"] == ["code"]