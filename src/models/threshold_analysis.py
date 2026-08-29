from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


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
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)


# --------------------------------------------------
# Train
# --------------------------------------------------

pipeline.fit(
    X_train,
    y_train,
)

probabilities = pipeline.predict_proba(
    X_validation
)[:, 1]


# --------------------------------------------------
# Revenue-aware analysis
# --------------------------------------------------

amounts = validation_df["amount"].values
actual_outcomes = y_validation.values

results = []

for threshold in np.arange(
    0.10,
    0.91,
    0.05,
):

    predictions = (
        probabilities >= threshold
    ).astype(int)

    intervention_mask = predictions == 1

    # Revenue that was actually recovered
    # among cases we chose to intervene on.
    recovered_revenue = (
        amounts[
            intervention_mask
            & (actual_outcomes == 1)
        ].sum()
    )

    revenue_at_risk = amounts.sum()

    recovery_rate = (
        recovered_revenue
        / revenue_at_risk
    )

    interventions = intervention_mask.sum()

    successful_interventions = (
        intervention_mask
        & (actual_outcomes == 1)
    ).sum()

    intervention_success_rate = (
        successful_interventions
        / interventions
        if interventions > 0
        else 0
    )

    results.append({
        "threshold": round(threshold, 2),
        "precision": precision_score(
            actual_outcomes,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            actual_outcomes,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            actual_outcomes,
            predictions,
            zero_division=0,
        ),
        "interventions": interventions,
        "successful_interventions":
            successful_interventions,
        "recovered_revenue":
            recovered_revenue,
        "recovery_rate":
            recovery_rate,
        "intervention_success_rate":
            intervention_success_rate,
    })


results_df = pd.DataFrame(results)


# --------------------------------------------------
# Output
# --------------------------------------------------

print("=" * 90)
print("RECLAIM — REVENUE-AWARE THRESHOLD ANALYSIS")
print("=" * 90)

print("\nValidation results:\n")

print(
    results_df.to_string(
        index=False,
        formatters={
            "precision":
                "{:.3f}".format,
            "recall":
                "{:.3f}".format,
            "f1":
                "{:.3f}".format,
            "recovered_revenue":
                "₹{:,.2f}".format,
            "recovery_rate":
                "{:.2%}".format,
            "intervention_success_rate":
                "{:.2%}".format,
        },
    )
)


# --------------------------------------------------
# Best thresholds
# --------------------------------------------------

best_f1 = results_df.loc[
    results_df["f1"].idxmax()
]

best_revenue = results_df.loc[
    results_df["recovered_revenue"].idxmax()
]

best_precision = results_df.loc[
    results_df["precision"].idxmax()
]


print("\n" + "-" * 90)

print(
    "\nBest F1 threshold:"
)

print(
    best_f1.to_string()
)

print(
    "\nBest recovered-revenue threshold:"
)

print(
    best_revenue.to_string()
)

print(
    "\nBest precision threshold:"
)

print(
    best_precision.to_string()
)

print("\n" + "=" * 90)