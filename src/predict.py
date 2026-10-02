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
