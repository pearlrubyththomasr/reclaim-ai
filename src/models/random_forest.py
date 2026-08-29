from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRAIN_PATH = Path("data/processed/train.csv")
VALIDATION_PATH = Path("data/processed/validation.csv")

TARGET = "recovered"

NUMERIC_FEATURES = [
    "amount",
    "attempt_number",
    "previous_transactions",
    "previous_successes",
    "previous_failures",
    "previous_recovery_successes",
    "customer_failure_rate",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
]

CATEGORICAL_FEATURES = [
    "payment_method",
    "merchant_category",
    "subscription_status",
    "failure_category",
    "failure_code",
]


# --------------------------------------------------
# Load data
# --------------------------------------------------

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)

X_train = train_df[
    NUMERIC_FEATURES + CATEGORICAL_FEATURES
]

y_train = train_df[TARGET]

X_validation = validation_df[
    NUMERIC_FEATURES + CATEGORICAL_FEATURES
]

y_validation = validation_df[TARGET]


# --------------------------------------------------
# Preprocessing
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES,
        ),
        (
            "numeric",
            "passthrough",
            NUMERIC_FEATURES,
        ),
    ]
)


# --------------------------------------------------
# Random Forest
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,
    min_samples_leaf=5,
    max_features="sqrt",
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)


# --------------------------------------------------
# Pipeline
# --------------------------------------------------

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# --------------------------------------------------
# Train
# --------------------------------------------------

print("=" * 60)
print("RECLAIM — RANDOM FOREST")
print("=" * 60)

print("\nTraining model...")

pipeline.fit(
    X_train,
    y_train,
)

print("✓ Training complete")


# --------------------------------------------------
# Predictions
# --------------------------------------------------

predictions = pipeline.predict(
    X_validation
)

probabilities = pipeline.predict_proba(
    X_validation
)[:, 1]


# --------------------------------------------------
# Metrics
# --------------------------------------------------

accuracy = accuracy_score(
    y_validation,
    predictions,
)

precision = precision_score(
    y_validation,
    predictions,
    zero_division=0,
)

recall = recall_score(
    y_validation,
    predictions,
    zero_division=0,
)

f1 = f1_score(
    y_validation,
    predictions,
    zero_division=0,
)

roc_auc = roc_auc_score(
    y_validation,
    probabilities,
)

pr_auc = average_precision_score(
    y_validation,
    probabilities,
)

brier = brier_score_loss(
    y_validation,
    probabilities,
)

logloss = log_loss(
    y_validation,
    probabilities,
)

confusion = confusion_matrix(
    y_validation,
    predictions,
)


# --------------------------------------------------
# Output
# --------------------------------------------------

print("\nValidation Metrics")
print("-" * 60)

print(f"Accuracy:          {accuracy:.4f}")
print(f"Precision:         {precision:.4f}")
print(f"Recall:            {recall:.4f}")
print(f"F1:                {f1:.4f}")
print(f"ROC-AUC:           {roc_auc:.4f}")
print(f"PR-AUC:            {pr_auc:.4f}")
print(f"Brier Score:       {brier:.4f}")
print(f"Log Loss:          {logloss:.4f}")

print("\nConfusion Matrix")
print(confusion)

print("\nClassification Report")

print(
    classification_report(
        y_validation,
        predictions,
        target_names=[
            "Not Recovered",
            "Recovered",
        ],
        zero_division=0,
    )
)

print("=" * 60)