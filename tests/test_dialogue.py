"""Conversation checks for memory, corrections, truthful replies, and isolation."""
from datetime import datetime
import subprocess
import sys

from fastapi.testclient import TestClient
import pytest

from api.main import app
from src.dialogue import DialogueManager
from src.train import PROJECT_ROOT

BASE = datetime(2026, 10, 2, 12)


def turn(bot, text):
    return bot.respond(text, reference_time=BASE)


def test_booking_across_turns():
    bot = DialogueManager()
    first = turn(bot, "Book a table tomorrow")
    assert first["state"]["date"] == "2026-10-03"
    assert "What time" in first["reply"]
    second = turn(bot, "7pm")
    assert second["state"]["time"] == "19:00"
    assert "How many" in second["reply"]
    third = turn(bot, "Four")
    assert third["state"]["party_size"] == 4
    assert third["state"]["awaiting_confirmation"]
    last = turn(bot, "yes")
    assert last["booking_draft"] == {"date": "2026-10-03", "time": "19:00", "party_size": 4}
    assert "No real reservation has been saved" in last["reply"]
    assert not last["state"]["active"]


def test_out_of_order_details():
    bot = DialogueManager()
    assert "What date" in turn(bot, "I'd like to make a reservation")["reply"]
    result = turn(bot, "party of 6")
    assert result["state"]["party_size"] == 6
    assert "What date" in result["reply"]
    result = turn(bot, "tomorrow at 7:30 pm")
    assert result["state"]["awaiting_confirmation"]
    assert result["state"]["time"] == "19:30"


def test_correction():
    bot = DialogueManager()
    turn(bot, "Book a table tomorrow at 7pm for 4 people")
    changed = turn(bot, "8pm")
    assert changed["state"]["time"] == "20:00"
    assert changed["state"]["date"] == "2026-10-03"
    assert turn(bot, "yes")["booking_draft"]["time"] == "20:00"


@pytest.mark.parametrize("text", ["reset", "cancel", "never mind", "no"])
def test_discard(text):
    bot = DialogueManager()
    turn(bot, "Book a table tomorrow at 7pm for 4 people")
    result = turn(bot, text)
    assert not result["state"]["active"]
    assert result["state"]["date"] is None
    assert "booking_draft" not in result


def test_information_interrupt():
    bot = DialogueManager(restaurant_info={"menu": ["Pasta", "Salad"]})
    turn(bot, "Book a table tomorrow")
    result = turn(bot, "Show me the menu")
    assert "Pasta; Salad" in result["reply"]
    assert "What time" in result["reply"]
    assert result["state"]["date"] == "2026-10-03"
    assert turn(bot, "7pm")["state"]["time"] == "19:00"


def test_unknown_does_not_confirm():
    bot = DialogueManager()
    turn(bot, "Book a table tomorrow at 7pm for 4 people")
    result = turn(bot, "My computer graphics card is broken")
    assert result["handled_as"] == "clarification"
    assert result["state"]["awaiting_confirmation"]
    assert "booking_draft" not in result


def test_number_only_when_asked():
    bot = DialogueManager()
    assert turn(bot, "four")["state"]["party_size"] is None
    turn(bot, "Book a table tomorrow")
    assert turn(bot, "four")["state"]["party_size"] is None
    turn(bot, "7pm")
    assert turn(bot, "0")["state"]["party_size"] is None
    assert turn(bot, "4")["state"]["party_size"] == 4


@pytest.mark.parametrize("text,info,expected", [
    ("What time do you open?", {"opening_hours": "Daily 12:00–22:00"}, "Daily 12:00–22:00"),
    ("Where are you located?", {"address": "123 Example Street"}, "123 Example Street"),
    ("Show me the menu", {"menu": ["Soup", "Rice"]}, "Soup; Rice"),
    ("Show me the menu", {}, "hasn't been configured"),
    ("Where are you located?", {}, "hasn't been configured"),
    ("What time do you open?", {}, "haven't been configured"),
])
def test_information(text, info, expected):
    assert expected in turn(DialogueManager(restaurant_info=info), text)["reply"]


def test_existing_reservation_replies():
    bot = DialogueManager()
    assert "can't cancel" in turn(bot, "Cancel my booking")["reply"]
    assert "can't change" in turn(bot, "Change my reservation to tomorrow")["reply"]


def test_goodbye_clears_memory():
    bot = DialogueManager()
    turn(bot, "Book a table tomorrow")
    assert not turn(bot, "Bye")["state"]["active"]
    assert turn(bot, "Book a table for two")["state"]["date"] is None


def test_independent_managers():
    first, second = DialogueManager(), DialogueManager()
    turn(first, "Book a table tomorrow")
    assert not turn(second, "Hello!")["state"]["active"]


def test_chat_api():
    with TestClient(app) as client:
        response = client.post("/chat", json={"text": "Book a table tomorrow"})
        assert response.status_code == 200
        state = response.json()["state"]
        state = client.post("/chat", json={"text": "7pm", "state": state}).json()["state"]
        assert state["time"] == "19:00"
        state = client.post("/chat", json={"text": "four", "state": state}).json()["state"]
        assert state["awaiting_confirmation"]
        confirmed = client.post("/chat", json={"text": "yes", "state": state}).json()
        assert confirmed["booking_draft"]["party_size"] == 4
        assert not confirmed["state"]["active"]
        assert not client.post("/chat", json={"text": "hello"}).json()["state"]["active"]


@pytest.mark.parametrize("payload", [
    {"text": " "},
    {"text": "yes", "state": {"awaiting_confirmation": True}},
    {"text": "yes", "state": {"active": True, "awaiting_confirmation": True}},
    {"text": "hello", "state": {"date": "2026-02-30"}},
    {"text": "hello", "state": {"time": "25:00"}},
    {"text": "hello", "state": {"party_size": 0}},
])
def test_invalid_chat(payload):
    with TestClient(app) as client:
        assert client.post("/chat", json=payload).status_code == 422


def test_chat_cli():
    process = subprocess.run(
        [sys.executable, "-m", "src.nlu"],
        input="Book a table tomorrow\n7pm\nfour\nyes\nexit\n", text=True,
        capture_output=True, cwd=PROJECT_ROOT, timeout=30,
    )
    assert process.returncode == 0
    assert "Bot: What time" in process.stdout
    assert "Bot: How many people" in process.stdout
    assert "Demo booking draft confirmed" in process.stdout
