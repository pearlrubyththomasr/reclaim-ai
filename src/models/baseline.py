from pathlib import Path

import pandas as pd

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


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRAIN_PATH = Path("data/processed/train.csv")
VALIDATION_PATH = Path("data/processed/validation.csv")

TARGET = "recovered"


# --------------------------------------------------
# Load data
# --------------------------------------------------

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)

y_train = train_df[TARGET]
y_validation = validation_df[TARGET]


# --------------------------------------------------
# Majority-class baseline
# --------------------------------------------------

majority_class = y_train.mode()[0]

predictions = [majority_class] * len(y_validation)

# Probability of the positive class.
# Since the model always predicts the majority class,
# probability of recovery is 0 for every sample.
probabilities = [0.0] * len(y_validation)


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

# ROC-AUC cannot be meaningfully computed when
# every prediction has exactly the same score.
roc_auc = None

average_precision = average_precision_score(
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
    labels=[0, 1],
)

confusion = confusion_matrix(
    y_validation,
    predictions,
)


# --------------------------------------------------
# Output
# --------------------------------------------------

print("=" * 60)
print("RECLAIM — MAJORITY CLASS BASELINE")
print("=" * 60)

print(f"\nTraining recovery rate: {y_train.mean():.2%}")

print(
    f"Majority class: "
    f"{majority_class}"
)

print("\nValidation metrics")
print("-" * 60)

print(f"Accuracy:          {accuracy:.4f}")
print(f"Precision:         {precision:.4f}")
print(f"Recall:            {recall:.4f}")
print(f"F1:                {f1:.4f}")
print(f"PR-AUC:            {average_precision:.4f}")
print(f"Brier Score:       {brier:.4f}")
print(f"Log Loss:          {logloss:.4f}")

print(
    f"ROC-AUC:           "
    f"{'N/A' if roc_auc is None else f'{roc_auc:.4f}'}"
)

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