from pathlib import Path
import sys

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------------
# Allow importing decision policy
# --------------------------------------------------

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from decision.policy import decide_recovery_action


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRAIN_PATH = Path(
    "data/processed/train.csv"
)

VALIDATION_PATH = Path(
    "data/processed/validation.csv"
)


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

TARGET = "recovered"


# --------------------------------------------------
# Load training data
# --------------------------------------------------

train_df = pd.read_csv(
    TRAIN_PATH
)

X_train = train_df[FEATURES]
y_train = train_df[TARGET]


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
print("RECLAIM — END-TO-END PREDICTION")
print("=" * 70)

print("\nTraining model...")

pipeline.fit(
    X_train,
    y_train,
)

print("✓ Model trained")


# --------------------------------------------------
# Load sample failed payments
# --------------------------------------------------

validation_df = pd.read_csv(
    VALIDATION_PATH
)

samples = validation_df.sample(
    n=5,
    random_state=42,
)


# --------------------------------------------------
# Generate predictions
# --------------------------------------------------

probabilities = pipeline.predict_proba(
    samples[FEATURES]
)[:, 1]


# --------------------------------------------------
# Decision engine
# --------------------------------------------------

for (_, row), probability in zip(
    samples.iterrows(),
    probabilities,
):

    decision = decide_recovery_action(
        recovery_probability=float(
            probability
        ),
        amount=float(
            row["amount"]
        ),
        failure_category=row[
            "failure_category"
        ],
        attempt_number=int(
            row["attempt_number"]
        ),
        customer_failure_rate=float(
            row["customer_failure_rate"]
        ),
    )

    print("\n" + "=" * 70)

    print(
        f"Transaction amount: "
        f"₹{row['amount']:,.2f}"
    )

    print(
        f"Payment method: "
        f"{row['payment_method']}"
    )

    print(
        f"Failure category: "
        f"{row['failure_category']}"
    )

    print(
        f"Failure code: "
        f"{row['failure_code']}"
    )

    print(
        f"Attempt number: "
        f"{row['attempt_number']}"
    )

    print(
        f"Customer failure rate: "
        f"{row['customer_failure_rate']:.2%}"
    )

    print("\nMODEL")

    print(
        f"Recovery probability: "
        f"{decision.recovery_probability:.2%}"
    )

    print(
        f"Expected recovery value: "
        f"₹{decision.expected_revenue:,.2f}"
    )

    print("\nDECISION")

    print(
        f"Confidence: "
        f"{decision.confidence}"
    )

    print(
        f"Recommended action: "
        f"{decision.recommended_action}"
    )

    print("\nReasons:")

    for reason in decision.reason:
        print(f"  • {reason}")


print("\n" + "=" * 70)
print("✅ END-TO-END INFERENCE COMPLETE")
print("=" * 70)