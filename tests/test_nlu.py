"""Regression checks for learned intents, date rules, CLI, and API behavior."""
from datetime import datetime, timezone
import subprocess
import sys

from fastapi.testclient import TestClient
import pandas as pd
import pytest

from api.main import app
from src.entities import extract_entities
from src.nlu import understand
from src.predict import load_model, predict_intent
from src.train import DATA_PATH, PROJECT_ROOT, train

BASE = datetime(2026, 10, 2, 12, 0)


@pytest.fixture(scope="session", autouse=True)
def ensure_model():
    """Tests work on a clean checkout, even if the saved model was removed."""
    from src.predict import MODEL_PATH
    if not MODEL_PATH.exists():
        train()
    load_model.cache_clear()


@pytest.mark.parametrize("text,intent", [
    ("Book a table tomorrow", "restaurant_booking"),
    ("Cancel my booking", "cancel_booking"),
    ("Change my reservation to tomorrow", "modify_booking"),
    ("Show me the menu", "view_menu"),
    ("What time do you open?", "opening_hours"),
    ("Where are you located?", "restaurant_location"),
    ("Hello!", "greeting"),
    ("Bye", "goodbye"),
    ("Could we reserve a table for our dinner?", "restaurant_booking"),
])
def test_intents(text, intent):
    result = understand(text)
    assert result["intent"] == intent
    assert 0 <= result["confidence"] <= 1
    assert result["text"] == text


@pytest.mark.parametrize("text", [
    "My computer graphics card is broken",
    "Quantum physics describes electrons",
    "zxqvplm",
])
def test_unknown(text):
    result = predict_intent(text)
    assert result["intent"] == "unknown"
    assert result["confidence"] < 0.5


def test_threshold(monkeypatch):
    assert predict_intent("Hello!", threshold=1)["intent"] == "unknown"
    monkeypatch.setenv("NLU_CONFIDENCE_THRESHOLD", "1")
    assert predict_intent("Hello!")["intent"] == "unknown"
    with pytest.raises(ValueError):
        predict_intent("hello", threshold=1.1)


@pytest.mark.parametrize("text,expected", [
    ("Book a table tomorrow at 7pm for 4 people",
     {"date": "2026-10-03", "time": "19:00", "party_size": 4}),
    ("next Friday at 7:30 pm table for two",
     {"date": "2026-10-09", "time": "19:30", "party_size": 2}),
    ("tonight at 19:00 party of 6",
     {"date": "2026-10-02", "time": "19:00", "party_size": 6}),
    ("today at noon for three guests",
     {"date": "2026-10-02", "time": "12:00", "party_size": 3}),
    ("day after tomorrow at midnight", {"date": "2026-10-04", "time": "00:00"}),
    ("on Friday", {"date": "2026-10-02"}),
    ("on Monday", {"date": "2026-10-05"}),
    ("next Monday", {"date": "2026-10-05"}),
    ("next Sunday", {"date": "2026-10-11"}),
    ("on 2026-12-25", {"date": "2026-12-25"}),
    ("on October 10, 2026", {"date": "2026-10-10"}),
    ("on 10 October 2026", {"date": "2026-10-10"}),
    ("for 0 people", {}),
    ("at 25:00", {}),
    ("at 19:99", {}),
    ("Hello!", {}),
])
def test_entities(text, expected):
    assert extract_entities(text, reference_time=BASE) == expected


def test_timezone_boundary():
    utc_time = datetime(2026, 10, 2, 18, tzinfo=timezone.utc)
    assert extract_entities("tomorrow", reference_time=utc_time)["date"] == "2026-10-04"


@pytest.mark.parametrize("text", ["", "   ", None, "a" * 2001])
def test_invalid_text(text):
    with pytest.raises(ValueError):
        understand(text)


def test_dataset():
    data = pd.read_csv(DATA_PATH)
    assert set(data.columns) == {"text", "intent"}
    assert data.intent.nunique() == 8
    assert data.intent.value_counts().min() >= 20


def test_model_is_learned_pipeline():
    model = load_model()
    assert list(model.named_steps) == ["tfidf", "classifier"]
    assert len(model.named_steps["tfidf"].vocabulary_) > 100
    assert len(model.classes_) == 8


def test_api():
    with TestClient(app) as client:
        assert client.get("/").json() == {"name": "Simple NLU API", "status": "running"}
        response = client.post("/understand", json={"text": "Book a table at 7pm for 4 people"})
        assert response.status_code == 200
        result = response.json()
        assert set(result) == {"intent", "confidence", "entities"}
        assert result["intent"] == "restaurant_booking"
        assert result["entities"] == {"time": "19:00", "party_size": 4}
        assert client.post("/understand", json={"text": "My computer graphics card is broken"}).json()["intent"] == "unknown"
        for payload in [{}, {"text": ""}, {"text": "   "}, {"text": "a" * 2001}, {"text": 42}]:
            assert client.post("/understand", json=payload).status_code == 422


def test_api_missing_model(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("Intent model missing. Run: python -m src.train")
    monkeypatch.setattr("api.main.understand", missing)
    with TestClient(app) as client:
        response = client.post("/understand", json={"text": "hello"})
        assert response.status_code == 503
        assert "python -m src.train" in response.json()["detail"]


def test_cli():
    process = subprocess.run(
        [sys.executable, "-m", "src.nlu"], input="Hello!\nexit\n", text=True,
        capture_output=True, cwd=PROJECT_ROOT, timeout=30,
    )
    assert process.returncode == 0
    assert "Simple NLU" in process.stdout
    assert "Intent: greeting" in process.stdout
