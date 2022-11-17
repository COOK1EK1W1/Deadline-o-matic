from src.deadlines import read_deadlines_to_json
import validators
import datetime

DEADLINE_KEYS = ["name", "subject", "start-datetime", "due-datetime", "mark", "room", "url", "info"]

def test_opening_file() -> None:
    assert type(read_deadlines_to_json()) == list

def test_all_keys() -> None:
    data = read_deadlines_to_json()
    for deadline in data:
        for key in DEADLINE_KEYS:
            assert key in deadline

def test_required() -> None:
    data = read_deadlines_to_json()
    for deadline in data:
        assert deadline["name"] != ""
        assert deadline["subject"] != ""

def test_dates_correct_form() -> None:
    data = read_deadlines_to_json()
    for deadline in data:
        if deadline["start-datetime"] != "":
            datetime.datetime.strptime(deadline["start-datetime"], "%Y-%m-%d %H:%M")
        if deadline["due-datetime"] != "":
            datetime.datetime.strptime(deadline["due-datetime"], "%Y-%m-%d  %H:%M")

def test_mark() -> None:
    data = read_deadlines_to_json()
    for deadline in data:
        assert 0 <= deadline["mark"] <= 1


def test_urls() -> None:
    data = read_deadlines_to_json()
    for deadline in data:
        if deadline["url"] != "":
            assert validators.url(deadline["url"])

def test_duplicates() -> None:
    data = read_deadlines_to_json()
    for i, deadline in enumerate(data):
        for y in range(i+1, len(data)):
            assert not ((deadline["name"] == data[y]["name"]) and (deadline["subject"] == data[y]["subject"]))