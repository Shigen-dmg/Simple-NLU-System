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
