# Simple NLU

A small local Natural Language Understanding and dialogue project for learning Python and traditional machine learning. It runs on a MacBook in VS Code, with no LLM, paid AI API, external inference service, or downloaded pretrained language model. Package installation needs internet access; training and inference run locally.

**NLU** turns a sentence into structured meaning. **Intent classification** identifies what someone wants to do (for example, book or cancel a table). **Entity extraction** finds details such as a date, time, or number of guests. This project recognizes eight restaurant intents and returns `unknown` when the highest class probability is below a configurable threshold.

## Start on your MacBook

The project is already created here. Open Terminal and run:

```bash
cd "/Users/*your username*/Desktop/Simple NLU System/language-nlu"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.train
python -m src.nlu
```

A virtual environment keeps this project's packages separate from other Python projects. One is already installed in this workspace; activate it to use it. In a cloned checkout, run `git clone https://github.com/Shigen-dmg/Simple-NLU-System.git` followed by `cd Simple-NLU-System` instead of the absolute `cd` above.

The tested interpreter is Python 3.9.6 on Apple Silicon macOS. Dependencies are bounded to compatible versions. `requirements-lock.txt` records all exact versions tested; use `python -m pip install -r requirements-lock.txt` to reproduce this environment. On a different Python version, use `requirements.txt`, retrain, and rerun tests. Scikit-learn serialized models should be loaded using the same scikit-learn version that trained them. Only load trusted joblib files: deserialization can execute code.

### VS Code

1. Open the `language-nlu` folder with File → Open Folder.
2. Install Microsoft's Python extension if needed.
3. Press **Cmd+Shift+P**, choose **Python: Select Interpreter**, and select `.venv/bin/python`. If absent, choose **Enter interpreter path** and browse to it.
4. Open Terminal → New Terminal. Run `source .venv/bin/activate` if it is not already active.
5. Run all commands from `language-nlu`, where `src`, `api`, and `tests` are directly visible.

## How machine learning works here

The CSV provides labeled examples: a sentence is the input and its intent is the answer to learn. There are 192 rows, 24 per intent, with varied wording. Training removes two capitalization/punctuation duplicates, leaving 190 distinct examples.

**TF-IDF** converts text into a sparse numerical vector. Words common in a particular sentence but less common across the dataset receive more weight. The vectorizer lowercases and tokenizes text; it learns both individual words and two-word phrases (`ngram_range=(1, 2)`). There is no hand-written intent keyword list.

**Logistic Regression** learns a set of weights for each intent. It combines feature values with these weights to estimate probabilities for the eight classes. `C=10` controls regularization (larger values allow less constrained weights). This is a fixed teaching baseline, not a parameter optimized using the test set. `max_iter=1000` allows enough optimizer iterations; `random_state=42` fixes the data split and estimator seed.

The scikit-learn `Pipeline` stores the learned vocabulary and classifier together. At prediction time, the very same vectorizer converts the sentence, then the classifier computes `predict_proba()`. The largest probability is the confidence. A 0.89 probability is a model estimate, not proof of an 89% real-world success rate. This small model is not probability-calibrated.

```text
Training CSV → stratified train/test split
                      ↓
            fit TF-IDF + classifier on train
                      ↓
            evaluate on unseen test sentences
                      ↓
            refit on all examples → save pipeline

User sentence
      ├─────────────────────────────┐
      ↓                             ↓
Text preprocessing             Entity extractor
      ↓                        regex + dateparser
TF-IDF                              ↓
      ↓                        Date / Time / Party size
Intent classifier                   │
      ↓                             │
Intent + confidence                 │
      └──────────────┬──────────────┘
                     ↓
           Structured NLU result
```

Entity extraction receives the original sentence, preserving date/time details. It stays separate from classification, so entities can still be returned when intent is `unknown`.

## Files and responsibilities

```text
language-nlu/
├── README.md                 Concepts, setup, usage, and limitations
├── DEVELOPMENT.md            Stage-by-stage guide with full source listings
├── requirements.txt          Compatible direct dependency ranges
├── requirements-lock.txt     Exact tested dependency versions
├── pytest.ini                Test discovery and import path
├── .gitignore                Python environments and caches
├── data/training_data.csv    Labeled intent examples
├── data/restaurant_info.json Local menu, hours, and address for replies
├── models/intent_model.pkl   Trained TF-IDF/classifier pipeline (kept available)
├── src/
│   ├── __init__.py            Marks the Python package
│   ├── train.py               Data validation, training, evaluation, serialization
│   ├── predict.py             Cached model loading and confidence rejection
│   ├── entities.py            Independent date, time, and party-size extraction
│   ├── nlu.py                 Combined understand() function and interactive CLI
│   └── dialogue.py            Replies and conversation memory
├── api/
│   ├── __init__.py            Marks the API package
│   └── main.py                FastAPI app and Pydantic input validation
└── tests/
    ├── __init__.py            Marks the tests package
    ├── test_nlu.py            Intent, entity, dataset, CLI, and API checks
    └── test_dialogue.py       Conversation, corrections, reset, and chat API checks
```

The complete implementation is in these files. The dialogue layer uses the existing trained model; no retraining is needed just to enable replies. [DEVELOPMENT.md](DEVELOPMENT.md) presents their full contents in build order, explains important code, and gives commands and expected output for each stage.

## Stage 1: inspect the dataset

```bash
python -c "import pandas as pd; d=pd.read_csv('data/training_data.csv'); print(d.groupby('intent').size())"
```

Expect 24 examples each for `restaurant_booking`, `cancel_booking`, `modify_booking`, `opening_hours`, `view_menu`, `restaurant_location`, `greeting`, and `goodbye`. The CSV is generated with proper quoting for sentences containing commas.

## Stage 2: train

```bash
python -m src.train
```

Training reserves 25% of the deduplicated examples for testing, stratified so all intents are represented. TF-IDF is fitted only on training text during evaluation, preventing vocabulary leakage. It prints accuracy, macro precision, macro recall, macro F1, and a per-intent classification report.

- Accuracy: fraction of correctly classified holdout sentences.
- Precision: among predictions for an intent, how many are correct.
- Recall: among actual examples of an intent, how many are detected.
- F1: balances precision and recall.
- Macro: gives each intent equal weight.

Observed baseline output:

```text
Examples: 190 (142 train / 48 test)
Accuracy: 0.833
Precision (macro): 0.852
Recall (macro): 0.833
F1 (macro): 0.832
...classification report...
Saved model trained on all 190 examples: .../models/intent_model.pkl
```

The report evaluates the highest-probability class before applying the rejection threshold. After evaluation the pipeline is refitted on all examples and saved. The report describes the held-out evaluation model, not an independent test of the final refit model. Unit tests cover expected behavior; many test phrases are also training examples and do not replace holdout evaluation. Metrics can change after editing data or package versions.

## Stages 3–5: use Python functions

```bash
python -c "from src.predict import predict_intent; print(predict_intent('Can you reserve a table for me?'))"
python -c "from src.entities import extract_entities; print(extract_entities('tomorrow at 7:30 pm table for two'))"
python -c "from src.nlu import understand; print(understand('Book a table tomorrow at 7pm for 4 people'))"
```

The first returns intent and confidence; the second returns entities without loading the ML model; the third combines them and includes the original text. For a reproducible date example:

```python
from datetime import datetime
from src.nlu import understand

result = understand(
    "Book a table tomorrow at 7pm for 4 people",
    reference_time=datetime(2026, 10, 2, 12),
)
print(result)
```

Expected result, with confidence rounded for display:

```json
{
  "text": "Book a table tomorrow at 7pm for 4 people",
  "intent": "restaurant_booking",
  "confidence": 0.8941,
  "entities": {
    "date": "2026-10-03",
    "time": "19:00",
    "party_size": 4
  }
}
```

### Confidence threshold

The default is 0.50. Set it for the process:

```bash
export NLU_CONFIDENCE_THRESHOLD=0.60
python -m src.nlu
```

Or pass `predict_intent(text, threshold=0.60)` or `understand(text, threshold=0.60)`. Use `unset NLU_CONFIDENCE_THRESHOLD` to return to the default. Raising the threshold rejects more sentences, including some valid requests. The unrounded probability determines rejection. Unknown results retain the highest class probability, rather than a probability of an independently learned unknown class.

The tested input `My computer graphics card is broken` returns `unknown` at approximately 0.378 confidence. Thresholding cannot reliably detect every unrelated sentence: an unfamiliar input can share familiar words and receive a confident wrong answer. A larger independent validation set and dedicated out-of-domain examples would help assess rejection behavior.

### Entity rules

Supported date spans include `today`, `tomorrow`, `day after tomorrow`, `tonight`, weekdays, `next Friday`, ISO dates (`2026-10-03`), and dates such as `October 10, 2026` or `10 October 2026`. Recognized spans are parsed with `dateparser`; output is `YYYY-MM-DD`.

Relative dates default to **Asia/Singapore** regardless of your Mac's timezone. `extract_entities(text, timezone='America/New_York')` lets a Python caller change it. An aware `reference_time` is converted to that timezone; a naive one is treated as local wall-clock time. `tonight` means today's date and does not invent a time. An unqualified weekday means its next occurrence, including today. `next Friday` means Friday of the next Monday–Sunday calendar week. These policies avoid ambiguity and are covered by deterministic tests.

Times include `7pm`, `7:30 pm`, `19:00`, `noon`, and `midnight`, returned in 24-hour `HH:MM` format. Party sizes include `for 4 people`, `for three guests`, `table for two`, and `party of 6`. Written numbers one through twelve and positive digit counts are supported.

Missing or invalid entities are omitted. The first recognized span for each entity is used. Bare times such as `at 7`, bare counts such as `for four`, numeric slash dates, date ranges, timezone phrases, and complex corrections such as “not Friday, Saturday instead” are outside the initial rules. The extractor does not resolve conflicting entities or validate restaurant availability.

## Stage 6: interactive CLI

```bash
python -m src.nlu
```

```text
Simple NLU
Type "exit" to quit, or "reset" to clear the conversation.

You: Book a table tomorrow at 7pm for 4 people
Bot: A table for 4 on 2026-10-03 at 19:00. Confirm this demo draft? Say yes or no, or give corrected details. This does not reserve a real table.

Intent: restaurant_booking
Confidence: 89%

Entities:
Date: 2026-10-03
Time: 19:00
Party size: 4
```

The date above assumes October 2, 2026 in Singapore; actual relative dates follow the current clock. Continue typing sentences, then type `exit`. Ctrl+C and end-of-input also exit. If the model is missing, the CLI tells you to run training. The model is cached once per process, so restart the CLI/API after retraining.

## Stage 7: local API

```bash
uvicorn api.main:app --reload
```

Expect a startup message indicating Uvicorn is running at `http://127.0.0.1:8000`. Leave this terminal running; press Ctrl+C to stop. Open [the root endpoint](http://127.0.0.1:8000) in a browser for:

```json
{"name": "Simple NLU API", "status": "running"}
```

Open [Swagger documentation](http://127.0.0.1:8000/docs), expand `POST /understand`, click **Try it out**, enter a JSON request, and click **Execute**. Alternatively, in a second terminal:

```bash
curl -X POST http://127.0.0.1:8000/understand \
  -H 'Content-Type: application/json' \
  -d '{"text":"Book a table tomorrow at 7pm for 4 people"}'
```

The response contains `intent`, `confidence`, and `entities`; the Python function additionally includes `text`. Pydantic rejects missing, empty, whitespace-only, non-string, or over-2000-character text with HTTP 422. A missing trained model returns HTTP 503 with a training command. GET `/` indicates the API process is running, not that a model has been loaded. These endpoints analyze sentences; they do not create real reservations.

## Stage 8: tests

```bash
pytest
```

Tests cover all intents, an additional booking paraphrase, unrelated text, configurable thresholds, all requested entity formats, explicit/relative dates, timezone boundaries, invalid input, learned model structure, dataset counts, CLI exit, API responses, and the missing-model response. They fix the clock for relative-date checks so they do not fail tomorrow. If the model is absent, the session fixture trains it first.

## Extend it

Add labeled sentences to the CSV, retrain, restart the CLI/API, and rerun tests. Preserve varied phrasing and balanced classes. Keep new evaluation examples distinct from training examples; the holdout here is small (six examples per intent) and its metrics are only a rough baseline.

To replace TF-IDF with another classifier later, change training and the `predict_intent()` implementation while preserving its `{intent, confidence}` return contract. `understand()`, entity extraction, CLI, and API can keep using that interface. Transformer models would require different dependencies, training, and evaluation; none are included now.

## Conversation replies and memory

Run the same CLI command after restarting it:

```bash
python -m src.nlu
```

Try:

```text
You: Book a table tomorrow
Bot: What time would you like? For example, 7pm or 19:30.
You: 7pm
Bot: How many people? You can say four or for 4 people.
You: Four
Bot: A table for 4 on 2026-10-03 at 19:00. Confirm this demo draft? ...
You: yes
Bot: Demo booking draft confirmed: 4 people on 2026-10-03 at 19:00. No real reservation has been saved; please contact the restaurant to book.
```

Dates follow the actual clock; the example assumes October 2, 2026. The CLI still displays raw intent, confidence, and entities below each reply, so you can see the NLU process. A short answer can have raw intent `unknown` while the dialogue manager correctly handles it as an answer to the pending question. It does not replace that confidence with an invented score.

`src/dialogue.py` adds a **dialogue manager**: it remembers an active booking draft, asks for the first missing slot, and chooses response templates. The **state** consists of `active`, `date`, `time`, `party_size`, and `awaiting_confirmation`. Ordinary requests use the learned classifier. Exact dialogue controls such as yes/no/reset and number-only answers use small deterministic rules in their conversation context.

- Supply details across turns or in one message. Supported entities may arrive in any order.
- When asked for party size, use `four`, `4`, or `4 people`. Standalone counts are accepted only when party size is the next missing detail. For a correction after the summary, use `for six people`.
- Correct a time with `8pm` or a date with `next Friday`; the bot shows an updated confirmation summary.
- Ask `Show me the menu` during a booking. It replies and resumes its pending question.
- Say `reset`, `start over`, `cancel`, or `never mind` to discard the current draft. Say `no` at confirmation to discard it.
- Say `yes` at confirmation to acknowledge the demo draft. `booking_draft` is returned on that turn; the active state is cleared. No reservation is saved or availability checked.
- Requests to cancel or modify an existing reservation explain that you must contact the restaurant. The bot can correct details of its current unsaved draft.
- Unrecognized replies prompt clarification while retaining the current draft. Goodbye clears memory; `exit` quits the CLI.

This is a small restaurant assistant with templates and one pending booking task. It does not generate unrestricted conversation or interpret arbitrary negations/corrections. Memory lasts only while the CLI process is running. It does not store customer data or confirmed drafts on disk.

### Configure real restaurant replies

Edit `data/restaurant_info.json` with your own information:

```json
{
  "name": "Your restaurant",
  "opening_hours": "Your actual opening hours",
  "address": "Your actual restaurant address",
  "menu": ["Your first dish", "Your second dish"]
}
```

The shipped hours/address are `null` and the menu is empty. Missing values produce a clear “hasn't been configured” reply. `opening_hours` and `address` should be strings or null, and `menu` should be a list of strings. Save valid JSON and restart the CLI to load updates. The API loads the file for each chat request. Editing these facts needs no model retraining.

### Python conversation interface

```python
from src.dialogue import DialogueManager

bot = DialogueManager()
print(bot.respond("Book a table tomorrow")["reply"])
print(bot.respond("7pm")["reply"])
print(bot.respond("four")["reply"])
```

Each manager owns independent state. `respond()` returns the original NLU fields plus `reply`, `handled_as`, and `state`; confirmation additionally returns `booking_draft`. `handled_as` tells you whether dialogue rules handled the message as booking details, confirmation, control, or clarification. `reference_time` remains available for deterministic examples/tests.

### Chat API

Start `uvicorn api.main:app --reload` and use `POST /chat` in Swagger at `http://127.0.0.1:8000/docs`. First request:

```json
{"text": "Book a table tomorrow"}
```

The response includes the bot's `reply` and `state`. Copy the **complete returned state** into your next request:

```json
{
  "text": "7pm",
  "state": {
    "active": true,
    "date": "2026-10-03",
    "time": null,
    "party_size": null,
    "awaiting_confirmation": false
  }
}
```

Use the actual date from your response. Continue with `four`, then `yes`, always sending the latest returned state. Omitting state starts a fresh conversation. This client-carried design avoids a global shared session and keeps conversations independent; nothing persists on the server. State is a draft controlled by the client, never proof of a real booking. Malformed dates/times, nonpositive party sizes, and incomplete confirmation states return HTTP 422. `/understand` retains its existing request/response contract.

Run `pytest` to check both NLU and conversation behavior. The verified suite has 66 passing tests, including the CLI's full booking conversation and independent API state.

## Reference documentation

The implementation follows the official [scikit-learn Pipeline documentation](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html), [Logistic Regression documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), and [dateparser settings documentation](https://dateparser.readthedocs.io/en/latest/settings.html). Consult documentation matching the installed version when comparing newer APIs.
