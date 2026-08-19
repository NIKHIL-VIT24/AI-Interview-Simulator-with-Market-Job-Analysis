"""
Hiring Probability Model — XGBoost
Combines technical, behavioral, and resume scores
to predict hiring probability.

Final formula from architecture doc:
  P(Hire=1|X) = sigmoid(β1 + β2*B + β3*R + β4*MaxD + β5*EC + β6*SR)

XGBoost is trained on structured features and used for prediction.
Until we have real training data, we use a logistic regression approximation.
"""
import numpy as np
import os
import pickle
try:
    from sklearn.linear_model import LogisticRegression
except Exception:
    LogisticRegression = None

# Path to save/load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "hiring_model.pkl")


# ── Model Training (run once to create model) ────────────────────────────────

def train_hiring_model():
    """
    Train a Logistic Regression model on synthetic data.
    In production: replace with real labelled hiring data.
    XGBoost can be swapped in once you have 100+ samples.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    np.random.seed(42)
    n = 500

    # Synthetic training features: [technical, behavioral, resume, max_difficulty, eye_contact, speech_rate]
    X = np.column_stack([
        np.random.uniform(30, 100, n),   # technical score
        np.random.uniform(0.2, 1.0, n),  # behavioral score
        np.random.uniform(0.1, 1.0, n),  # resume score
        np.random.randint(1, 5, n),      # max difficulty reached
        np.random.uniform(0.3, 1.0, n),  # eye contact
        np.random.uniform(0.4, 1.0, n),  # speech rate
    ])

    # Label: hire if overall quality is high
    y = (
        (X[:, 0] > 60) &                # good technical score
        (X[:, 1] > 0.5) &               # good behavioral
        (X[:, 2] > 0.4)                 # decent resume
    ).astype(int)

    if LogisticRegression is None:
        print("[Hiring Model] scikit-learn unavailable. Using heuristic fallback model.")
        return None

    model = LogisticRegression(random_state=42, max_iter=500)
    model.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"[Hiring Model] Trained and saved to {MODEL_PATH}")
    return model


def load_hiring_model():
    """Load the trained model, or train if not found."""
    if LogisticRegression is None:
        print("[Hiring Model] scikit-learn not installed. Falling back to heuristic scoring.")
        return None

    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    else:
        print("[Hiring Model] No saved model found. Training new model...")
        return train_hiring_model()


# Load once at module import
_model = load_hiring_model()


def _heuristic_probability(
    technical_score: float,
    behavioral_score: float,
    resume_score: float,
    max_difficulty: int,
    eye_contact_pct: float,
    speech_rate_norm: float,
) -> float:
    """Fallback probability when ML libs are unavailable."""
    technical_norm = max(0.0, min(1.0, technical_score / 100.0))
    difficulty_norm = max(0.0, min(1.0, max_difficulty / 4.0))
    raw = (
        0.38 * technical_norm
        + 0.20 * behavioral_score
        + 0.18 * resume_score
        + 0.12 * difficulty_norm
        + 0.07 * eye_contact_pct
        + 0.05 * speech_rate_norm
    )
    return max(0.0, min(1.0, raw))


# ── Prediction ───────────────────────────────────────────────────────────────

def predict_hiring_probability(
    technical_score: float,    # 0–100
    behavioral_score: float,   # 0.0–1.0
    resume_score: float,       # 0.0–1.0
    max_difficulty: int,       # 1–4
    eye_contact_pct: float,    # 0.0–1.0
    speech_rate_norm: float    # 0.0–1.0 (normalized)
) -> dict:
    """
    Predict hiring probability using the trained model.
    Returns probability (0-1) and a recommendation.
    """
    features = np.array([[
        technical_score,
        behavioral_score,
        resume_score,
        float(max_difficulty),
        eye_contact_pct,
        speech_rate_norm
    ]])

    if _model is not None and hasattr(_model, "predict_proba"):
        prob = float(_model.predict_proba(features)[0][1])
    else:
        prob = _heuristic_probability(
            technical_score=technical_score,
            behavioral_score=behavioral_score,
            resume_score=resume_score,
            max_difficulty=max_difficulty,
            eye_contact_pct=eye_contact_pct,
            speech_rate_norm=speech_rate_norm,
        )

    # Recommendation thresholds
    if prob >= 0.70:
        recommendation = "Hire"
    elif prob >= 0.45:
        recommendation = "Maybe"
    else:
        recommendation = "Reject"

    return {
        "hiring_probability": round(prob, 4),
        "recommendation": recommendation,
        "score_breakdown": {
            "technical_score": technical_score,
            "behavioral_score": behavioral_score,
            "resume_score": resume_score,
            "max_difficulty_reached": max_difficulty,
            "eye_contact": eye_contact_pct,
            "speech_rate": speech_rate_norm
        }
    }


def retrain_with_real_data(training_data: list):
    """
    Retrain the model with real labeled hiring data.

    training_data: list of dicts with keys:
        technical_score, behavioral_score, resume_score,
        max_difficulty, eye_contact_pct, speech_rate_norm, hired (0/1)
    """
    global _model

    if LogisticRegression is None:
        raise RuntimeError("scikit-learn is required for retraining.")

    X = np.array([
        [d["technical_score"], d["behavioral_score"], d["resume_score"],
         d["max_difficulty"], d["eye_contact_pct"], d["speech_rate_norm"]]
        for d in training_data
    ])
    y = np.array([d["hired"] for d in training_data])

    # Switch to XGBoost for production
    try:
        from xgboost import XGBClassifier
        _model = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="logloss"
        )
    except ImportError:
        _model = LogisticRegression(max_iter=500)

    _model.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(_model, f)

    print("[Hiring Model] Retrained with real data and saved.")
