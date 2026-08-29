from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RAW_PATH = Path("data/raw/transactions_raw.csv")
PROCESSED_DIR = Path("data/processed")

TRAIN_PATH = PROCESSED_DIR / "train.csv"
VALIDATION_PATH = PROCESSED_DIR / "validation.csv"
TEST_PATH = PROCESSED_DIR / "test.csv"


# --------------------------------------------------
# Feature definitions
# --------------------------------------------------

FEATURE_COLUMNS = [
    "amount",
    "payment_method",
    "merchant_category",
    "subscription_status",
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
]

TARGET_COLUMN = "recovered"

IDENTIFIER_COLUMNS = [
    "transaction_id",
    "customer_id",
]

EXCLUDED_COLUMNS = [
    "timestamp",
    "currency",
    "payment_status",
    "recovery_probability",
]


# --------------------------------------------------
# Load data
# --------------------------------------------------

if not RAW_PATH.exists():
    raise FileNotFoundError(
        f"Raw dataset not found: {RAW_PATH}"
    )

df = pd.read_csv(RAW_PATH)

print("=" * 60)
print("RECLAIM DATA PREPROCESSING")
print("=" * 60)

print(f"\nRaw dataset:")
print(f"Rows:    {len(df):,}")
print(f"Columns: {len(df.columns)}")


# --------------------------------------------------
# Parse timestamp
# --------------------------------------------------

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="raise",
)

# Always sort before a temporal split.
df = df.sort_values(
    "timestamp"
).reset_index(drop=True)


# --------------------------------------------------
# Keep only failed payments
# --------------------------------------------------

failed_df = df[
    df["payment_status"] == "failed"
].copy()

print("\nFailed payment events:")
print(f"Rows: {len(failed_df):,}")


# --------------------------------------------------
# Additional temporal features
# --------------------------------------------------

failed_df["hour_of_day"] = (
    failed_df["timestamp"].dt.hour
)

failed_df["day_of_week"] = (
    failed_df["timestamp"].dt.dayofweek
)

failed_df["is_weekend"] = (
    failed_df["day_of_week"] >= 5
).astype(int)


# --------------------------------------------------
# Select ML dataset
# --------------------------------------------------

ml_df = failed_df[
    FEATURE_COLUMNS + [TARGET_COLUMN]
].copy()


# --------------------------------------------------
# Verify target
# --------------------------------------------------

if not ml_df[TARGET_COLUMN].isin([0, 1]).all():
    raise ValueError(
        "Target column contains values other than 0/1."
    )


# --------------------------------------------------
# Temporal split
# --------------------------------------------------

n = len(ml_df)

train_end = int(n * 0.80)
validation_end = int(n * 0.90)

train_df = ml_df.iloc[
    :train_end
].copy()

validation_df = ml_df.iloc[
    train_end:validation_end
].copy()

test_df = ml_df.iloc[
    validation_end:
].copy()


# --------------------------------------------------
# Create output directory
# --------------------------------------------------

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# Save datasets
# --------------------------------------------------

train_df.to_csv(
    TRAIN_PATH,
    index=False,
)

validation_df.to_csv(
    VALIDATION_PATH,
    index=False,
)

test_df.to_csv(
    TEST_PATH,
    index=False,
)


# --------------------------------------------------
# Print split information
# --------------------------------------------------

print("\n" + "-" * 60)
print("TEMPORAL SPLIT")
print("-" * 60)

print(
    f"\nTrain:      {len(train_df):,} rows"
)

print(
    f"Validation: {len(validation_df):,} rows"
)

print(
    f"Test:       {len(test_df):,} rows"
)


print("\nDate ranges:")

print(
    f"Train:      "
    f"{failed_df.iloc[0]['timestamp']} → "
    f"{failed_df.iloc[train_end - 1]['timestamp']}"
)

print(
    f"Validation: "
    f"{failed_df.iloc[train_end]['timestamp']} → "
    f"{failed_df.iloc[validation_end - 1]['timestamp']}"
)

print(
    f"Test:       "
    f"{failed_df.iloc[validation_end]['timestamp']} → "
    f"{failed_df.iloc[-1]['timestamp']}"
)


# --------------------------------------------------
# Target distribution
# --------------------------------------------------

print("\n" + "-" * 60)
print("TARGET DISTRIBUTION")
print("-" * 60)

for name, dataset in [
    ("Train", train_df),
    ("Validation", validation_df),
    ("Test", test_df),
]:

    recovery_rate = dataset[
        TARGET_COLUMN
    ].mean()

    print(
        f"{name:<12}"
        f"Recovery rate: "
        f"{recovery_rate:.2%}"
    )


# --------------------------------------------------
# Leakage checks
# --------------------------------------------------

print("\n" + "-" * 60)
print("LEAKAGE CHECK")
print("-" * 60)

for column in EXCLUDED_COLUMNS:
    if column in ml_df.columns:
        raise ValueError(
            f"Leakage column found in ML dataset: {column}"
        )

print("✓ No known leakage columns included")


# --------------------------------------------------
# Final verification
# --------------------------------------------------

assert len(train_df) > 0
assert len(validation_df) > 0
assert len(test_df) > 0

assert (
    train_df.index.max()
    if len(train_df)
    else 0
) >= 0

print("\n" + "=" * 60)
print("✅ PREPROCESSING COMPLETE")
print("=" * 60)

print("\nGenerated:")
print(f"  {TRAIN_PATH}")
print(f"  {VALIDATION_PATH}")
print(f"  {TEST_PATH}")