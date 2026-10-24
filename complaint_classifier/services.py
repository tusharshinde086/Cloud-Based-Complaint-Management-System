import os
import re
from functools import lru_cache
from pathlib import Path

import joblib
from django.conf import settings


MODEL_PATH = Path(getattr(settings, "BASE_DIR", Path.cwd())) / "ml_models" / "complaint_classifier.joblib"


def clean_text(value):
    text = str(value or "").lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def _load_model():
    if not MODEL_PATH.exists():
        return None
    try:
        return joblib.load(MODEL_PATH)
    except (OSError, ValueError, EOFError, ImportError):
        return None


def classify_complaint(title, description):
    text = clean_text(f"{title or ''} {description or ''}")
    model = _load_model()
    if model is not None:
        try:
            prediction = model.predict([text])[0]
            confidence = None
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba([text])[0]
                confidence = round(float(max(probabilities)) * 100, 2)
            return {
                "category": str(prediction),
                "method": "trained_model",
                "confidence": confidence,
            }
        except (ValueError, TypeError, AttributeError):
            pass

    # Deterministic fallback when no trained model is installed.
    keyword_groups = {
        "Technical": ["internet", "network", "server", "website", "software", "computer", "login", "app", "system", "error"],
        "Billing": ["bill", "billing", "payment", "refund", "invoice", "charge", "fee", "transaction"],
        "Facilities": ["electricity", "water", "cleaning", "toilet", "chair", "room", "building", "fan", "light"],
        "Service": ["staff", "service", "delay", "response", "support", "behaviour", "behavior", "help"],
    }
    scores = {
        category: sum(1 for keyword in keywords if re.search(rf"\b{re.escape(keyword)}\b", text))
        for category, keywords in keyword_groups.items()
    }
    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        best_category = "General"
    return {
        "category": best_category,
        "method": "keyword_fallback",
        "confidence": None,
    }


def train_classifier(csv_path, model_path=None, text_column="text", label_column="category"):
    """Train and save a text classifier from a CSV containing text and category columns."""
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    frame = pd.read_csv(csv_path)
    if text_column not in frame.columns or label_column not in frame.columns:
        raise ValueError(
            f"CSV must contain columns named '{text_column}' and '{label_column}'."
        )
    frame = frame[[text_column, label_column]].dropna()
    frame[text_column] = frame[text_column].map(clean_text)
    frame[label_column] = frame[label_column].astype(str).str.strip()
    frame = frame[(frame[text_column] != "") & (frame[label_column] != "")]
    if frame[label_column].nunique() < 2:
        raise ValueError("Training data must contain at least two different categories.")
    if len(frame) < 10:
        raise ValueError("Provide at least 10 labelled examples to train the initial model.")

    X_train, X_test, y_train, y_test = train_test_split(
        frame[text_column], frame[label_column], test_size=0.2,
        random_state=42, stratify=frame[label_column]
        if frame[label_column].value_counts().min() >= 2 else None,
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=15000, sublinear_tf=True)),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "report": classification_report(y_test, predictions, zero_division=0, output_dict=True),
        "samples": int(len(frame)),
    }
    output_path = Path(model_path) if model_path else MODEL_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    _load_model.cache_clear()
    return metrics
