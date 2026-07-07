"""Runtime wrapper around the trained risk-profiling model used by the API."""
import os
import joblib
import pandas as pd

HERE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(HERE, "artifacts", "risk_model.joblib")

_bundle = None


class ModelNotTrainedError(RuntimeError):
    pass


def _load():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise ModelNotTrainedError(
                "Risk model not found. Run: python -m app.ml.generate_dataset "
                "&& python -m app.ml.train_risk_model"
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def predict_risk_profile(features: dict) -> dict:
    """features must contain all keys in bundle['features']. Returns label + class probabilities."""
    bundle = _load()
    row = pd.DataFrame([{k: features[k] for k in bundle["features"]}])
    pipeline = bundle["pipeline"]
    label_encoder = bundle["label_encoder"]

    pred_idx = pipeline.predict(row)[0]
    proba = pipeline.predict_proba(row)[0]
    label = label_encoder.inverse_transform([pred_idx])[0]
    proba_map = {cls: round(float(p), 4) for cls, p in zip(label_encoder.classes_, proba)}

    return {
        "risk_label": label,
        "confidence": proba_map[label],
        "class_probabilities": proba_map,
    }


def is_ready() -> bool:
    return os.path.exists(MODEL_PATH)
