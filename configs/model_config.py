# ==================================================
# RECLAIM MODEL CONFIGURATION
# ==================================================

MODEL_NAME = "logistic_regression"

MODEL_VERSION = "1.0.0"

RANDOM_STATE = 42

MAX_ITER = 1000

DECISION_THRESHOLD = 0.35


# ==================================================
# NUMERIC FEATURES
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


# ==================================================
# CATEGORICAL FEATURES
# ==================================================

CATEGORICAL_FEATURES = [
    "payment_method",
    "merchant_category",
    "subscription_status",
    "failure_category",
    "failure_code",
]


# ==================================================
# ALL FEATURES
# ==================================================

FEATURES = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)


TARGET = "recovered"