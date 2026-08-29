from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRAIN_PATH = Path("data/processed/train.csv")

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

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "recovered"


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(TRAIN_PATH)

X = df[FEATURES]
y = df[TARGET]


# --------------------------------------------------
# Preprocessing
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
                handle_unknown="ignore",
            ),
            CATEGORICAL_FEATURES,
        ),
    ]
)


# --------------------------------------------------
# Model
# --------------------------------------------------

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

print("=" * 70)
print("RECLAIM — MODEL EXPLAINABILITY")
print("=" * 70)

print("\nTraining model...")

pipeline.fit(X, y)

print("✓ Model trained")


# --------------------------------------------------
# Extract feature names
# --------------------------------------------------

fitted_preprocessor = pipeline.named_steps[
    "preprocessor"
]

fitted_model = pipeline.named_steps[
    "model"
]

feature_names = (
    fitted_preprocessor
    .get_feature_names_out()
)

coefficients = fitted_model.coef_[0]


# --------------------------------------------------
# Build coefficient table
# --------------------------------------------------

importance = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients,
})

importance["absolute_coefficient"] = (
    importance["coefficient"].abs()
)

importance = importance.sort_values(
    "absolute_coefficient",
    ascending=False,
)


# --------------------------------------------------
# Output top features
# --------------------------------------------------

print("\nTop 20 features influencing recovery")
print("-" * 70)

print(
    importance[
        [
            "feature",
            "coefficient",
        ]
    ]
    .head(20)
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)


# --------------------------------------------------
# Positive / negative features
# --------------------------------------------------

positive = (
    importance[
        importance["coefficient"] > 0
    ]
    .sort_values(
        "coefficient",
        ascending=False,
    )
    .head(10)
)

negative = (
    importance[
        importance["coefficient"] < 0
    ]
    .sort_values(
        "coefficient",
        ascending=True,
    )
    .head(10)
)


print("\n")
print("Features increasing recovery probability")
print("-" * 70)

print(
    positive[
        [
            "feature",
            "coefficient",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)


print("\n")
print("Features decreasing recovery probability")
print("-" * 70)

print(
    negative[
        [
            "feature",
            "coefficient",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)


# --------------------------------------------------
# Example prediction
# --------------------------------------------------

sample = X.iloc[[0]]

sample_probability = pipeline.predict_proba(
    sample
)[0, 1]

print("\n")
print("=" * 70)
print("EXAMPLE TRANSACTION")
print("=" * 70)

print(
    sample.to_string(index=False)
)

print(
    f"\nPredicted recovery probability: "
    f"{sample_probability:.2%}"
)

print("=" * 70)