from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.calibration import (
    calibration_curve,
)
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRAIN_PATH = Path(
    "data/processed/train.csv"
)

VALIDATION_PATH = Path(
    "data/processed/validation.csv"
)

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

FEATURES = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

train_df = pd.read_csv(
    TRAIN_PATH
)

validation_df = pd.read_csv(
    VALIDATION_PATH
)

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_validation = validation_df[FEATURES]
y_validation = validation_df[TARGET]


# --------------------------------------------------
# Build model
# --------------------------------------------------

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

model = LogisticRegression(
    max_iter=1000,
    random_state=42,
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


# --------------------------------------------------
# Train
# --------------------------------------------------

print("=" * 70)
print("RECLAIM — PROBABILITY CALIBRATION")
print("=" * 70)

print("\nTraining model...")

pipeline.fit(
    X_train,
    y_train,
)

print("✓ Model trained")


# --------------------------------------------------
# Generate probabilities
# --------------------------------------------------

probabilities = pipeline.predict_proba(
    X_validation
)[:, 1]


# --------------------------------------------------
# Calibration metrics
# --------------------------------------------------

brier = brier_score_loss(
    y_validation,
    probabilities,
)

logloss = log_loss(
    y_validation,
    probabilities,
)


print("\nCalibration Metrics")
print("-" * 70)

print(
    f"Brier Score: {brier:.4f}"
)

print(
    f"Log Loss:    {logloss:.4f}"
)


# --------------------------------------------------
# Reliability curve
# --------------------------------------------------

fraction_positive, mean_predicted = (
    calibration_curve(
        y_validation,
        probabilities,
        n_bins=10,
        strategy="uniform",
    )
)


print("\nReliability Table")
print("-" * 70)

print(
    f"{'Predicted':>12}"
    f"{'Actual':>12}"
)

for predicted, actual in zip(
    mean_predicted,
    fraction_positive,
):

    print(
        f"{predicted:>11.3f}"
        f"{actual:>12.3f}"
    )


# --------------------------------------------------
# Plot
# --------------------------------------------------

plt.figure(
    figsize=(7, 7)
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Perfect calibration",
)

plt.plot(
    mean_predicted,
    fraction_positive,
    marker="o",
    label="Logistic Regression",
)

plt.xlabel(
    "Mean predicted probability"
)

plt.ylabel(
    "Fraction of positives"
)

plt.title(
    "RECLAIM Probability Calibration"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.show()


print("\n" + "=" * 70)
print("✅ CALIBRATION ANALYSIS COMPLETE")
print("=" * 70)