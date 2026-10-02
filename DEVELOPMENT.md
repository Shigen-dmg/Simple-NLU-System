# Development stages and full source

Run these commands from `language-nlu` with `.venv` activated. Train before prediction, CLI, or API use. README explains setup, architecture, metrics, confidence, and limitations. Actual source files remain the editable implementation.

## Stage 1: Dataset

Labeled examples teach the model how wording relates to intents. CSV quoting preserves commas.

### `data/training_data.csv`

Full contents:

```csv
text,intent
Book a table for tomorrow,restaurant_booking
Reserve dinner tonight,restaurant_booking
Can I get a table for four,restaurant_booking
I'd like to make a reservation,restaurant_booking
Please book dinner for two people,restaurant_booking
We need a table on Friday evening,restaurant_booking
Could you reserve a table for me,restaurant_booking
Book a table tomorrow at 7pm for 4 people,restaurant_booking
Arrange a lunch reservation for six,restaurant_booking
I'd like to reserve seating for our group,restaurant_booking
Can we book dinner this weekend,restaurant_booking
Is it possible to make a table booking,restaurant_booking
Please reserve a spot for lunch,restaurant_booking
Book dinner tomorrow at 8pm for 3 people,restaurant_booking
I need a reservation for Saturday night,restaurant_booking
We'd like a table for our anniversary,restaurant_booking
Make a dinner booking for five guests,restaurant_booking
Reserve a table near the window,restaurant_booking
May I book a table at noon,restaurant_booking
Can you arrange a reservation for tonight,restaurant_booking
I want to book lunch next Monday,restaurant_booking
Please get us a table for two,restaurant_booking
I'd like to dine here tomorrow with friends,restaurant_booking
Can you reserve a table for me?,restaurant_booking
Cancel my reservation,cancel_booking
I want to cancel my booking,cancel_booking
Please cancel the table I reserved,cancel_booking
We cannot attend so cancel our dinner reservation,cancel_booking
I'd like to call off my lunch booking,cancel_booking
Remove my reservation for Friday,cancel_booking
Cancel the dinner reservation for two,cancel_booking
I no longer need my booked table,cancel_booking
Please delete my table booking,cancel_booking
Could you cancel our reservation tonight,cancel_booking
We need to cancel Saturday's booking,cancel_booking
I want to withdraw my dinner reservation,cancel_booking
Call off the table reservation please,cancel_booking
Cancel my booking for tomorrow,cancel_booking
Please revoke my lunch reservation,cancel_booking
We won't be coming so cancel our table,cancel_booking
Can you cancel the reservation under my name,cancel_booking
I'd like my existing booking cancelled,cancel_booking
Delete the dinner booking I made earlier,cancel_booking
Our plans changed please cancel the reservation,cancel_booking
I need to cancel the table for six,cancel_booking
Cancel the booking at seven,cancel_booking
Remove our dinner reservation from the schedule,cancel_booking
Please cancel my reservation entirely,cancel_booking
Change my reservation to tomorrow,modify_booking
I want to modify my booking,modify_booking
Move my table reservation to Friday,modify_booking
Please change my booking time to 8pm,modify_booking
Update our reservation to six people,modify_booking
Can I reschedule my dinner booking,modify_booking
Change the party size on my reservation,modify_booking
Shift our lunch booking to next week,modify_booking
I'd like to adjust my existing reservation,modify_booking
Move our table booking an hour later,modify_booking
Please amend the reservation under my name,modify_booking
Change my table for two to a table for four,modify_booking
Can you update my booking date,modify_booking
Reschedule my reservation for Saturday evening,modify_booking
Make my existing reservation earlier,modify_booking
I'd like to add two guests to my booking,modify_booking
Reduce the number of people on our reservation,modify_booking
Can we move our reserved dinner to Sunday,modify_booking
Modify my table booking to 7:30 pm,modify_booking
Please change the reservation from lunch to dinner,modify_booking
Update the time of my reservation,modify_booking
Keep my booking but change the date,modify_booking
Can I alter our dinner reservation,modify_booking
I need to postpone my existing booking,modify_booking
What time do you open,opening_hours
When do you close,opening_hours
What are your opening hours,opening_hours
Are you open on Sundays,opening_hours
Tell me your business hours,opening_hours
How late is the restaurant open,opening_hours
When does dinner service start,opening_hours
What time do you shut tonight,opening_hours
Are you open for lunch today,opening_hours
What's your closing time on Friday,opening_hours
When can customers start dining,opening_hours
Do you open early on weekends,opening_hours
Which hours are you open during the week,opening_hours
Can you tell me when the restaurant opens,opening_hours
Is the restaurant open on holidays,opening_hours
When is your last seating,opening_hours
What time does lunch service finish,opening_hours
Are you still open at midnight,opening_hours
What are your operating times,opening_hours
Does the restaurant close in the afternoon,opening_hours
How early do you open tomorrow,opening_hours
Until what time can we eat here,opening_hours
What is your Sunday opening schedule,opening_hours
What time do you open?,opening_hours
Show me the menu,view_menu
What food do you serve,view_menu
Can I see your dinner menu,view_menu
I'd like to browse the dishes,view_menu
Do you have vegetarian meals,view_menu
What's on the lunch menu,view_menu
Tell me about your desserts,view_menu
Which dishes are available,view_menu
Please send me your food menu,view_menu
What are your specials today,view_menu
Can I look at the drinks list,view_menu
Do you serve seafood,view_menu
What meals can I order,view_menu
Show your vegan options please,view_menu
I want to see the breakfast menu,view_menu
What kind of cuisine do you offer,view_menu
List your main courses,view_menu
Are there gluten free options on the menu,view_menu
Let me browse the restaurant menu,view_menu
Do you offer a children's menu,view_menu
Which appetizers do you serve,view_menu
Can you show me your beverage menu,view_menu
Tell me what dishes you cook,view_menu
I'd like to check the menu before booking,view_menu
Where is the restaurant,restaurant_location
Where are you located,restaurant_location
What is your address,restaurant_location
How do I get to your restaurant,restaurant_location
Can you give me directions,restaurant_location
Which street are you on,restaurant_location
Tell me your restaurant location,restaurant_location
Where can I find you,restaurant_location
Send me the address please,restaurant_location
Are you near the train station,restaurant_location
What's the nearest landmark to your restaurant,restaurant_location
Show me where the restaurant is,restaurant_location
I need directions to your building,restaurant_location
Which neighborhood is the restaurant in,restaurant_location
How can I reach your location,restaurant_location
Where is your entrance,restaurant_location
Can you share your street address,restaurant_location
Is your restaurant downtown,restaurant_location
What road is the restaurant on,restaurant_location
Please help me find the restaurant,restaurant_location
Where exactly are you situated,restaurant_location
Give me the restaurant's postcode,restaurant_location
Can you point me to your location,restaurant_location
Where are you located?,restaurant_location
Hello,greeting
Hi there,greeting
Hey,greeting
Good morning,greeting
Good evening,greeting
Hello there,greeting
Hi how are you,greeting
Hey folks,greeting
Greetings,greeting
Good afternoon,greeting
Hi everyone,greeting
Hello restaurant team,greeting
Nice to meet you,greeting
Hey there how's it going,greeting
Hi can you help me,greeting
Hello good morning,greeting
Howdy,greeting
Hello again,greeting
Hey good to see you,greeting
Hi restaurant staff,greeting
Greetings to your team,greeting
Hi there folks,greeting
Hello how are things,greeting
Hey can we chat,greeting
Bye,goodbye
Goodbye,goodbye
See you later,goodbye
Have a nice day,goodbye
That's all thanks bye,goodbye
Good night,goodbye
See you soon,goodbye
Farewell,goodbye
I'm leaving now goodbye,goodbye
Thanks for your help see you,goodbye
Talk to you later,goodbye
Bye for now,goodbye
Catch you later,goodbye
Have a great evening,goodbye
Until next time,goodbye
Take care goodbye,goodbye
All done thanks bye,goodbye
See you next time,goodbye
I have to go now,goodbye
Thanks goodbye,goodbye
Have a good night,goodbye
Cheers see you around,goodbye
Bye bye,goodbye
That's everything goodbye,goodbye
```

Run:

```bash
python -c "import pandas as pd; print(pd.read_csv('data/training_data.csv').groupby('intent').size())"
```

Expected output: 24 examples for each of eight intents.

## Stage 2: Training

The initializer marks a package. train.py validates data, removes duplicates, and splits with stratification. The Pipeline fits TF-IDF only on training text before evaluation, preventing vocabulary leakage. Macro metrics weight each intent equally. After evaluation, it refits on all examples and saves the full pipeline.

### `src/__init__.py`

Full contents:

```python
# Empty package initializer; no executable code.
```

### `src/train.py`

Full contents:

```python
"""Train and evaluate a TF-IDF + Logistic Regression intent classifier."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "training_data.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "intent_model.pkl"


def train(data_path: Path = DATA_PATH, model_path: Path = MODEL_PATH) -> Pipeline:
    """Report held-out performance, then fit all examples and save the pipeline."""
    data = pd.read_csv(data_path)
    if not {"text", "intent"}.issubset(data.columns):
        raise ValueError("CSV must contain text and intent columns.")
    if data[["text", "intent"]].isna().any().any():
        raise ValueError("Training text and intent labels must not be missing.")
    if any(not isinstance(value, str) or not value.strip()
           for value in data[["text", "intent"]].to_numpy().ravel()):
        raise ValueError("Training text and labels must be nonempty strings.")
    # Ignore capitalization/punctuation duplicates so they cannot cross the split.
    data["normalized"] = data.text.str.lower().str.replace(r"[^\w\s]", "", regex=True).str.strip()
    if (data.groupby("normalized").intent.nunique() > 1).any():
        raise ValueError("The same sentence has conflicting intent labels.")
    data = data.drop_duplicates("normalized")
    if data.intent.nunique() < 2 or data.intent.value_counts().min() < 5:
        raise ValueError("Provide at least two intents and five distinct examples per intent.")
    train_text, test_text, train_labels, test_labels = train_test_split(
        data.text, data.intent, test_size=0.25, stratify=data.intent, random_state=42
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("classifier", LogisticRegression(C=10.0, max_iter=1000, random_state=42)),
    ])
    # Fit vocabulary on training data only; test examples remain unseen.
    model.fit(train_text, train_labels)
    predicted = model.predict(test_text)
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_labels, predicted, average="macro", zero_division=0
    )
    print(f"Examples: {len(data)} ({len(train_text)} train / {len(test_text)} test)")
    print(f"Accuracy: {accuracy_score(test_labels, predicted):.3f}")
    print(f"Precision (macro): {precision:.3f}")
    print(f"Recall (macro): {recall:.3f}")
    print(f"F1 (macro): {f1:.3f}")
    print(classification_report(test_labels, predicted, zero_division=0))
    # The saved educational model uses all data AFTER holdout evaluation.
    model.fit(data.text, data.intent)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Saved model trained on all {len(data)} examples: {model_path}")
    return model


if __name__ == "__main__":
    train()
```

Run:

```bash
python -m src.train
```

Expected output: Accuracy 0.833; macro precision 0.852, recall 0.833, F1 0.832; a classification report and saved model path.

## Stage 3: Prediction

load_model caches the pipeline. predict_proba returns probabilities in model.classes_ order. argmax selects the best index. A configurable threshold rejects uncertain predictions; there are no hard-coded intent keywords.

### `src/predict.py`

Full contents:

```python
"""Predict learned intents with a configurable rejection threshold."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
from sklearn.pipeline import Pipeline

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "intent_model.pkl"


@lru_cache(maxsize=1)
def load_model() -> Pipeline:
    """Load once per process. Restart the CLI/API after retraining."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError("Intent model missing. Run: python -m src.train")
    return joblib.load(MODEL_PATH)


def validate_text(text: str) -> None:
    """Reject invalid text consistently in Python, CLI, and API callers."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a nonempty string.")
    if len(text) > 2000:
        raise ValueError("Text must contain at most 2000 characters.")


def predict_intent(text: str, threshold: Optional[float] = None) -> Dict[str, Any]:
    """Return the most likely intent, or unknown below the threshold."""
    validate_text(text)
    if threshold is None:
        threshold = float(os.getenv("NLU_CONFIDENCE_THRESHOLD", "0.50"))
    if not 0 <= threshold <= 1:
        raise ValueError("Confidence threshold must be between 0 and 1.")
    model = load_model()
    probabilities = model.predict_proba([text])[0]
    best_index = int(probabilities.argmax())
    confidence = float(probabilities[best_index])
    intent = str(model.classes_[best_index]) if confidence >= threshold else "unknown"
    return {"intent": intent, "confidence": confidence}
```

Run:

```bash
python -c "from src.predict import predict_intent; print(predict_intent('Can you reserve a table for me?'))"
```

Expected output: restaurant_booking with a probability between zero and one.

## Stage 4: Entities

Regular expressions locate supported date/time spans and dateparser parses them. Positive digits and number words supply party size. Weekday policies are explicit; an injectable reference clock makes tests repeatable. No classifier is loaded here.

### `src/entities.py`

Full contents:

```python
"""Extract a small, explicit set of restaurant entities without an AI service."""
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

import dateparser

NUMBER_WORDS = dict(zip(
    "one two three four five six seven eight nine ten eleven twelve".split(), range(1, 13)
))
NUMBER = r"(?:\d+|" + "|".join(NUMBER_WORDS) + r")"
PARTY_PATTERN = re.compile(
    rf"\b(?:party\s+of\s+(?P<party>{NUMBER})\b|"
    rf"table\s+for\s+(?P<table>{NUMBER})\b|"
    rf"for\s+(?P<people>{NUMBER})\s+(?:people|persons|guests|diners)\b)", re.I
)
TIME_PATTERN = re.compile(
    r"\b(?:(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s*[ap]m\b|"
    r"(?:[01]?\d|2[0-3]):[0-5]\d\b|noon\b|midnight\b)", re.I
)
WEEKDAY = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
MONTH = (r"january|february|march|april|may|june|july|august|september|"
         r"october|november|december")
DATE_PATTERN = re.compile(
    rf"\b(?:day after tomorrow|tomorrow|tonight|today|"
    rf"(?:next\s+)?(?:{WEEKDAY})|\d{{4}}-\d{{2}}-\d{{2}}|"
    rf"(?:{MONTH})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?|"
    rf"\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTH})(?:\s+\d{{4}})?)\b", re.I
)


def extract_entities(text: str, reference_time: Optional[datetime] = None,
                     timezone: str = "Asia/Singapore") -> Dict[str, Any]:
    """Return recognized entities; use an injectable local clock for testing.

    'next Friday' means Friday in the next calendar week (Monday–Sunday).
    An unqualified weekday means its next occurrence, including today.
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    zone = ZoneInfo(timezone)
    base = reference_time or datetime.now(zone)
    if base.tzinfo is not None:
        base = base.astimezone(zone)
    base = base.replace(tzinfo=None)
    settings = {"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"}
    entities: Dict[str, Any] = {}
    match = DATE_PATTERN.search(text)
    if match:
        phrase = match.group().lower()
        if phrase == "tonight":
            phrase = "today"
        # dateparser does not reliably support 'next Friday'; anchor the weekday.
        if re.fullmatch(rf"next\s+(?:{WEEKDAY})", phrase):
            next_monday = base + timedelta(days=7 - base.weekday())
            weekday_index = WEEKDAY.split("|").index(phrase.split()[-1])
            candidate = next_monday + timedelta(days=weekday_index)
            parsed = dateparser.parse(candidate.date().isoformat(), languages=["en"], settings=settings)
        elif re.fullmatch(WEEKDAY, phrase):
            # Parsing weekdays as future can skip today; make our policy explicit.
            weekdays = WEEKDAY.split("|")
            candidate = base + timedelta(days=(weekdays.index(phrase) - base.weekday()) % 7)
            parsed = dateparser.parse(candidate.date().isoformat(), languages=["en"], settings=settings)
        else:
            parsed = dateparser.parse(phrase, languages=["en"], settings=settings)
        if parsed is not None:
            entities["date"] = parsed.date().isoformat()
    match = TIME_PATTERN.search(text)
    if match:
        phrase = match.group().lower()
        phrase = {"noon": "12:00", "midnight": "00:00"}.get(phrase, phrase)
        parsed = dateparser.parse(phrase, languages=["en"], settings=settings)
        if parsed is not None:
            entities["time"] = parsed.strftime("%H:%M")
    match = PARTY_PATTERN.search(text)
    if match:
        raw = next(value for value in match.groupdict().values() if value).lower()
        size = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
        if size > 0:
            entities["party_size"] = size
    return entities
```

Run:

```bash
python -c "from src.entities import extract_entities; print(extract_entities('tomorrow at 7:30 pm table for two'))"
```

Expected output: Tomorrow's Singapore date, time 19:30, and party_size 2.

## Stage 5 and 6: NLU and CLI

understand combines the components and preserves the original text. main accepts repeated input, displays percentages, and exits on exit, EOF, or Ctrl+C. Missing models and invalid text produce useful instructions.

### `src/nlu.py`

Full contents:

```python
"""Combine intent prediction and independent entity extraction; run the CLI."""
from datetime import datetime
from typing import Any, Dict, Optional

from src.entities import extract_entities
from src.predict import predict_intent


def understand(text: str, threshold: Optional[float] = None,
               reference_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Convert a sentence into an intent, confidence, and recognized entities."""
    prediction = predict_intent(text, threshold=threshold)
    return {"text": text, **prediction,
            "entities": extract_entities(text, reference_time=reference_time)}


def main() -> None:
    """Read sentences until exit, EOF, or Ctrl+C."""
    print('Simple NLU\nType "exit" to quit.\n')
    while True:
        try:
            text = input("You: ")
            if text.strip().lower() == "exit":
                break
            result = understand(text)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except FileNotFoundError as error:
            print(error)
            break
        except ValueError as error:
            print(error)
            continue
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.0%}\n")
        print("Entities:")
        for name, value in result["entities"].items():
            print(f"{name.replace('_', ' ').capitalize()}: {value}")
        if not result["entities"]:
            print("None found")
        print()


if __name__ == "__main__":
    main()
```

Run:

```bash
python -m src.nlu
```

Expected output: Simple NLU, an exit instruction, and a You: prompt. Enter a sentence for intent, confidence, and entities.

## Stage 7: API

The initializer marks a package. Pydantic validates input text before passing it to understand. POST returns the three requested output fields. A missing model returns HTTP 503 with the training command. GET reports API process status.

### `api/__init__.py`

Full contents:

```python
# Empty package initializer; no executable code.
```

### `api/main.py`

Full contents:

```python
"""Local FastAPI endpoints for the NLU pipeline."""
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.nlu import understand

app = FastAPI(title="Simple NLU API")


class UnderstandRequest(BaseModel):
    """A nonempty sentence, limited to 2000 characters."""
    text: str = Field(min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def reject_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank.")
        return value


@app.get("/")
def root() -> Dict[str, str]:
    return {"name": "Simple NLU API", "status": "running"}


@app.post("/understand")
def understand_sentence(request: UnderstandRequest) -> Dict[str, Any]:
    try:
        result = understand(request.text)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {key: result[key] for key in ("intent", "confidence", "entities")}
```

Run:

```bash
uvicorn api.main:app --reload
```

Expected output: Uvicorn starts at http://127.0.0.1:8000. Visit /docs to try POST /understand. README supplies a curl request.

## Stage 8: Tests

Parametrized cases check all eight intents, rejection, entities, and date/time policies. TestClient checks HTTP behavior. A subprocess checks CLI behavior. Tests train only if a model is absent. Unit tests complement holdout evaluation; they do not measure generalization.

### `tests/__init__.py`

Full contents:

```python
# Empty package initializer; no executable code.
```

### `tests/test_nlu.py`

Full contents:

```python
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
```

### `pytest.ini`

Full contents:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

Run:

```bash
pytest
```

Expected output: 39 passing tests in the tested environment.

## Stage 9 and 10: Environment

Dependency ranges support the installed Mac Python. httpx supports API tests. The ignore file excludes environments and caches while keeping data and the trained model. requirements-lock.txt records the exact tested dependency set.

### `requirements.txt`

Full contents:

```text
pandas>=2.2,<2.3
scikit-learn>=1.6,<1.7
joblib>=1.4,<1.6
dateparser>=1.2,<1.3
fastapi>=0.115,<0.117
uvicorn>=0.34,<0.35
pytest>=8.3,<8.5
httpx>=0.27,<0.29
```

### `.gitignore`

Full contents:

```text
.venv/
__pycache__/
.pytest_cache/
.DS_Store
*.py[cod]
*.egg-info/
.coverage
htmlcov/
.env
```

Run:

```bash
python -m pip install -r requirements.txt
```

Expected output: Packages install in the active virtual environment, or report Requirement already satisfied.

## Stage 11: README

README.md explains NLU, TF-IDF, Logistic Regression, the architecture, all files, exact macOS and VS Code setup, usage, and limitations. Open it in VS Code and press Cmd+Shift+V for Markdown Preview. Expected output: formatted project documentation.
