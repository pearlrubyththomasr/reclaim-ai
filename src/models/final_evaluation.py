from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
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
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ==================================================
# RECLAIM — FINAL MODEL CONFIGURATION
# ==================================================

TRAIN_PATH = Path(
    "data/processed/train.csv"
)

TEST_PATH = Path(
    "data/processed/test.csv"
)

TARGET = "recovered"

DECISION_THRESHOLD = 0.35

RANDOM_STATE = 42


# ==================================================
# FEATURES
# ==================================================

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

FEATURES = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)


# ==================================================
# LOAD DATA
# ==================================================

train_df = pd.read_csv(
    TRAIN_PATH
)

test_df = pd.read_csv(
    TEST_PATH
)

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ==================================================
# PREPROCESSING
# ==================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            NUMERIC_FEATURES,
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES,
        ),
    ]
)


# ==================================================
# MODEL
# ==================================================

model = LogisticRegression(
    max_iter=1000,
    random_state=RANDOM_STATE,
)


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


# ==================================================
# TRAIN
# ==================================================

print("=" * 70)
print("RECLAIM — FINAL TEST EVALUATION")
print("=" * 70)

print("\n🔒 FINAL MODEL CONFIGURATION")
print("-" * 70)

print("Model:              Logistic Regression")
print(f"Decision threshold: {DECISION_THRESHOLD}")
print(f"Random state:       {RANDOM_STATE}")

print("\nTraining on training set...")

pipeline.fit(
    X_train,
    y_train,
)

print("✓ Training complete")


# ==================================================
# PREDICTIONS
# ==================================================

probabilities = pipeline.predict_proba(
    X_test
)[:, 1]

predictions = (
    probabilities >= DECISION_THRESHOLD
).astype(int)


# ==================================================
# METRICS
# ==================================================

accuracy = accuracy_score(
    y_test,
    predictions,
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0,
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0,
)

roc_auc = roc_auc_score(
    y_test,
    probabilities,
)

pr_auc = average_precision_score(
    y_test,
    probabilities,
)

brier = brier_score_loss(
    y_test,
    probabilities,
)

logloss = log_loss(
    y_test,
    probabilities,
)

confusion = confusion_matrix(
    y_test,
    predictions,
)


# ==================================================
# TEST SET SUMMARY
# ==================================================

print("\n")
print("=" * 70)
print("FINAL TEST RESULTS")
print("=" * 70)

print("\nClassification Metrics")
print("-" * 70)

print(
    f"Accuracy:          {accuracy:.4f}"
)

print(
    f"Precision:         {precision:.4f}"
)

print(
    f"Recall:            {recall:.4f}"
)

print(
    f"F1:                {f1:.4f}"
)

print(
    f"ROC-AUC:           {roc_auc:.4f}"
)

print(
    f"PR-AUC:            {pr_auc:.4f}"
)

print(
    f"Brier Score:       {brier:.4f}"
)

print(
    f"Log Loss:           {logloss:.4f}"
)


# ==================================================
# CONFUSION MATRIX
# ==================================================

print("\nConfusion Matrix")
print("-" * 70)

print(confusion)


# ==================================================
# CLASSIFICATION REPORT
# ==================================================

print("\nClassification Report")
print("-" * 70)

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Not Recovered",
            "Recovered",
        ],
        zero_division=0,
    )
)


# ==================================================
# TEST SET DISTRIBUTION
# ==================================================

print("\nTest Set Information")
print("-" * 70)

print(
    f"Test rows:          {len(test_df)}"
)

print(
    f"Actual recoveries:  {y_test.sum()}"
)

print(
    f"Actual recovery rate: "
    f"{y_test.mean():.2%}"
)

print(
    f"Predicted recoveries: "
    f"{predictions.sum()}"
)

print(
    f"Predicted intervention rate: "
    f"{predictions.mean():.2%}"
)


# ==================================================
# TEST SET DATE RANGE
# ==================================================

print("\nTest Date Range")
print("-" * 70)

print(
    "Date range: available in preprocessing report"
)

print(
    "Test set contains only processed model features."
)

# ==================================================
# FINAL STATUS
# ==================================================

print("\n")
print("=" * 70)
print("🔒 TEST SET EVALUATION COMPLETE")
print("=" * 70)

print(
    "\nThe test set has now been evaluated "
    "using the frozen model configuration."
)

print(
    "\nDo NOT tune the model using these results."
)

print("=" * 70)