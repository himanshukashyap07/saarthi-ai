"""
Trains a RandomForest classifier that infers a customer's behavioural risk
profile (conservative / moderate / aggressive) from spending + investment
behaviour features, instead of relying on a one-time static questionnaire.

Run: python -m app.ml.train_risk_model
Requires app/ml/data/synthetic_customers.csv (run generate_dataset.py first).
"""
import os
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

HERE = os.path.dirname(__file__)
DATA_PATH = os.path.join(HERE, "data", "synthetic_customers.csv")
ARTIFACT_DIR = os.path.join(HERE, "artifacts")
MODEL_PATH = os.path.join(ARTIFACT_DIR, "risk_model.joblib")
METRICS_PATH = os.path.join(ARTIFACT_DIR, "metrics.json")

NUMERIC_FEATURES = [
    "age", "dependents", "monthly_income", "monthly_expense", "monthly_savings",
    "savings_rate", "existing_investment_value", "equity_pct_current", "debt_pct_current",
    "sip_active", "sip_amount", "sip_missed_last_6m", "txn_volatility",
    "credit_card_utilization_pct", "goal_horizon_years",
]
CATEGORICAL_FEATURES = ["occupation"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "risk_label"


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} not found — run generate_dataset.py first")

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET]

    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    preprocessor = ColumnTransformer(transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ], remainder="passthrough")

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=10, min_samples_leaf=5,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    print("Confusion matrix (rows=actual, cols=predicted):", label_encoder.classes_.tolist())
    for row in cm:
        print(row)

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    joblib.dump({
        "pipeline": pipeline,
        "label_encoder": label_encoder,
        "features": FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
    }, MODEL_PATH)

    with open(METRICS_PATH, "w") as f:
        json.dump({"accuracy": acc, "report": report, "confusion_matrix": cm,
                    "classes": label_encoder.classes_.tolist()}, f, indent=2)

    print(f"\nSaved model -> {MODEL_PATH}")
    print(f"Saved metrics -> {METRICS_PATH}")


if __name__ == "__main__":
    main()
