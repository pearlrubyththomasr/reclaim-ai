import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATA_PATH = Path("data/raw/transactions_raw.csv")

REQUIRED_COLUMNS = [
    "transaction_id",
    "customer_id",
    "timestamp",
    "amount",
    "currency",
    "payment_method",
    "merchant_category",
    "subscription_status",
    "payment_status",
    "failure_category",
    "failure_code",
    "attempt_number",
    "previous_transactions",
    "previous_successes",
    "previous_failures",
    "previous_recovery_successes",
    "customer_failure_rate",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "recovery_probability",
    "recovered",
]

VALID_PAYMENT_METHODS = {
    "upi",
    "credit_card",
    "debit_card",
    "netbanking",
    "wallet",
}

VALID_PAYMENT_STATUSES = {
    "failed",
    "successful",
}

VALID_FAILURE_CATEGORIES = {
    "none",
    "transient",
    "insufficient_funds",
    "expired_payment_method",
    "authentication_failure",
    "network_failure",
    "merchant_error",
    "unknown",
}


# --------------------------------------------------
# Validation helpers
# --------------------------------------------------

errors = []


def check(condition, message):
    """Add an error if a validation condition fails."""
    if not condition:
        errors.append(message)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

if not DATA_PATH.exists():
    print(f"❌ Dataset not found: {DATA_PATH}")
    sys.exit(1)

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("RECLAIM DATA VALIDATION")
print("=" * 60)

print(f"\nDataset: {DATA_PATH}")
print(f"Rows:    {len(df):,}")
print(f"Columns: {len(df.columns)}")


# --------------------------------------------------
# Schema validation
# --------------------------------------------------

missing_columns = [
    col for col in REQUIRED_COLUMNS
    if col not in df.columns
]

unexpected_columns = [
    col for col in df.columns
    if col not in REQUIRED_COLUMNS
]

check(
    len(missing_columns) == 0,
    f"Missing required columns: {missing_columns}"
)

if unexpected_columns:
    print(f"⚠️ Unexpected columns: {unexpected_columns}")


# Stop here if schema is fundamentally broken
if missing_columns:
    print("\n❌ Schema validation failed.")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)


# --------------------------------------------------
# Missing values
# --------------------------------------------------

missing_values = df[REQUIRED_COLUMNS].isnull().sum()

missing_total = missing_values.sum()

check(
    missing_total == 0,
    f"Missing values detected: {missing_total}"
)


# --------------------------------------------------
# Duplicate IDs
# --------------------------------------------------

duplicate_transactions = (
    df["transaction_id"].duplicated().sum()
)

duplicate_customers = (
    df["customer_id"].duplicated().sum()
)

check(
    duplicate_transactions == 0,
    f"Duplicate transaction IDs: {duplicate_transactions}"
)

# Customer IDs SHOULD repeat, so we don't flag those.


# --------------------------------------------------
# Amount validation
# --------------------------------------------------

invalid_amounts = (
    (df["amount"] <= 0) |
    (~df["amount"].apply(lambda x: isinstance(x, (int, float))))
).sum()

check(
    invalid_amounts == 0,
    f"Invalid transaction amounts: {invalid_amounts}"
)


# --------------------------------------------------
# Categorical validation
# --------------------------------------------------

invalid_payment_methods = (
    ~df["payment_method"].isin(VALID_PAYMENT_METHODS)
).sum()

check(
    invalid_payment_methods == 0,
    f"Invalid payment methods: {invalid_payment_methods}"
)


invalid_statuses = (
    ~df["payment_status"].isin(VALID_PAYMENT_STATUSES)
).sum()

check(
    invalid_statuses == 0,
    f"Invalid payment statuses: {invalid_statuses}"
)


invalid_failure_categories = (
    ~df["failure_category"].isin(VALID_FAILURE_CATEGORIES)
).sum()

check(
    invalid_failure_categories == 0,
    f"Invalid failure categories: {invalid_failure_categories}"
)


# --------------------------------------------------
# Attempt number validation
# --------------------------------------------------

invalid_attempts = (
    (df["attempt_number"] < 1) |
    (df["attempt_number"] > 10)
).sum()

check(
    invalid_attempts == 0,
    f"Invalid attempt numbers: {invalid_attempts}"
)


# --------------------------------------------------
# Customer-history consistency
# --------------------------------------------------

invalid_history = (
    df["previous_failures"]
    > df["previous_transactions"]
).sum()

check(
    invalid_history == 0,
    f"Customers with more failures than transactions: {invalid_history}"
)


invalid_successes = (
    df["previous_successes"]
    != (
        df["previous_transactions"]
        - df["previous_failures"]
    )
).sum()

check(
    invalid_successes == 0,
    f"Inconsistent previous_successes values: {invalid_successes}"
)


# --------------------------------------------------
# Probability validation
# --------------------------------------------------

invalid_probabilities = (
    (df["recovery_probability"] < 0) |
    (df["recovery_probability"] > 1)
).sum()

check(
    invalid_probabilities == 0,
    f"Invalid recovery probabilities: {invalid_probabilities}"
)


# --------------------------------------------------
# Target validation
# --------------------------------------------------

invalid_recovered_values = (
    ~df["recovered"].isin([0, 1])
).sum()

check(
    invalid_recovered_values == 0,
    f"Invalid recovered values: {invalid_recovered_values}"
)


# Successful original payments should not be marked
# as recovered.

invalid_successful_recovery = (
    (df["payment_status"] == "successful") &
    (df["recovered"] == 1)
).sum()

check(
    invalid_successful_recovery == 0,
    (
        "Successful original payments marked as recovered: "
        f"{invalid_successful_recovery}"
    )
)


# Successful payments should have no failure category.

invalid_successful_failure_category = (
    (df["payment_status"] == "successful") &
    (df["failure_category"] != "none")
).sum()

check(
    invalid_successful_failure_category == 0,
    (
        "Successful payments have a failure category: "
        f"{invalid_successful_failure_category}"
    )
)


# Failed payments should have a failure category.

invalid_failed_failure_category = (
    (df["payment_status"] == "failed") &
    (df["failure_category"] == "none")
).sum()

check(
    invalid_failed_failure_category == 0,
    (
        "Failed payments have no failure category: "
        f"{invalid_failed_failure_category}"
    )
)


# --------------------------------------------------
# Timestamp validation
# --------------------------------------------------

timestamps = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

invalid_timestamps = timestamps.isna().sum()

check(
    invalid_timestamps == 0,
    f"Invalid timestamps: {invalid_timestamps}"
)


# --------------------------------------------------
# Print summary
# --------------------------------------------------

print("\n" + "-" * 60)
print("VALIDATION SUMMARY")
print("-" * 60)

checks = {
    "Required columns": len(missing_columns) == 0,
    "Missing values": missing_total == 0,
    "Duplicate transaction IDs": duplicate_transactions == 0,
    "Valid amounts": invalid_amounts == 0,
    "Valid payment methods": invalid_payment_methods == 0,
    "Valid payment statuses": invalid_statuses == 0,
    "Valid failure categories": invalid_failure_categories == 0,
    "Valid attempt numbers": invalid_attempts == 0,
    "Consistent customer history": (
        invalid_history == 0
        and invalid_successes == 0
    ),
    "Valid probabilities": invalid_probabilities == 0,
    "Valid target": invalid_recovered_values == 0,
    "Valid timestamps": invalid_timestamps == 0,
    "Recovery consistency": (
        invalid_successful_recovery == 0
        and invalid_successful_failure_category == 0
        and invalid_failed_failure_category == 0
    ),
}

for name, passed in checks.items():
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {name}")


# --------------------------------------------------
# Final result
# --------------------------------------------------

print("\n" + "=" * 60)

if errors:
    print("❌ DATASET VALIDATION FAILED")
    print("=" * 60)

    for error in errors:
        print(f"  • {error}")

    sys.exit(1)

else:
    print("✅ DATASET VALIDATION PASSED")
    print("=" * 60)

    print("\nDataset is safe to proceed to preprocessing.")