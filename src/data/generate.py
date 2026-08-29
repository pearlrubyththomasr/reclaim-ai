import os
import numpy as np
import pandas as pd
from faker import Faker

# -----------------------------
# Configuration
# -----------------------------

SEED = 42
N_TRANSACTIONS = 50_000

np.random.seed(SEED)
fake = Faker()
fake.seed_instance(SEED)

OUTPUT_PATH = "data/raw/transactions_raw.csv"


# -----------------------------
# Reference categories
# -----------------------------

PAYMENT_METHODS = [
    "upi",
    "credit_card",
    "debit_card",
    "netbanking",
    "wallet",
]

FAILURE_TYPES = [
    "transient",
    "insufficient_funds",
    "expired_payment_method",
    "authentication_failure",
    "network_failure",
    "merchant_error",
    "unknown",
]

FAILURE_CODES = {
    "transient": [
        "GATEWAY_TIMEOUT",
        "PROCESSING_TIMEOUT",
    ],
    "insufficient_funds": [
        "INSUFFICIENT_FUNDS",
        "BALANCE_LOW",
    ],
    "expired_payment_method": [
        "CARD_EXPIRED",
        "PAYMENT_METHOD_EXPIRED",
    ],
    "authentication_failure": [
        "AUTH_FAILED",
        "OTP_FAILED",
    ],
    "network_failure": [
        "NETWORK_ERROR",
        "CONNECTION_FAILED",
    ],
    "merchant_error": [
        "MERCHANT_CONFIGURATION_ERROR",
        "INVALID_REQUEST",
    ],
    "unknown": [
        "UNKNOWN_ERROR",
    ],
}

MERCHANT_CATEGORIES = [
    "ecommerce",
    "saas",
    "education",
    "travel",
    "food",
    "healthcare",
]

SUBSCRIPTION_STATUSES = [
    "none",
    "active",
    "past_due",
]


# -----------------------------
# Generate customers
# -----------------------------

N_CUSTOMERS = 10_000

customer_ids = [
    f"CUST_{i:05d}"
    for i in range(1, N_CUSTOMERS + 1)
]

customer_profiles = pd.DataFrame({
    "customer_id": customer_ids,
    "previous_transactions": np.random.randint(1, 30, N_CUSTOMERS),
    "previous_failures": np.random.randint(0, 8, N_CUSTOMERS),
    "previous_recovery_successes": np.random.randint(0, 6, N_CUSTOMERS),
})

customer_profiles["previous_successes"] = (
    customer_profiles["previous_transactions"]
    - customer_profiles["previous_failures"]
)

customer_profiles["previous_successes"] = (
    customer_profiles["previous_successes"].clip(lower=0)
)

customer_profiles["customer_failure_rate"] = (
    customer_profiles["previous_failures"]
    / customer_profiles["previous_transactions"]
)


# -----------------------------
# Generate transactions
# -----------------------------

transaction_ids = [
    f"TXN_{i:06d}"
    for i in range(1, N_TRANSACTIONS + 1)
]

transactions = pd.DataFrame({
    "transaction_id": transaction_ids,
    "customer_id": np.random.choice(
        customer_ids,
        N_TRANSACTIONS
    ),
    "amount": np.round(
        np.random.lognormal(
            mean=np.log(1800),
            sigma=0.9,
            size=N_TRANSACTIONS
        ),
        2
    ),
    "currency": "INR",
    "payment_method": np.random.choice(
        PAYMENT_METHODS,
        N_TRANSACTIONS,
        p=[0.45, 0.20, 0.15, 0.12, 0.08],
    ),
    "merchant_category": np.random.choice(
        MERCHANT_CATEGORIES,
        N_TRANSACTIONS,
    ),
    "subscription_status": np.random.choice(
        SUBSCRIPTION_STATUSES,
        N_TRANSACTIONS,
        p=[0.55, 0.35, 0.10],
    ),
    "timestamp": pd.date_range(
        start="2026-01-01",
        periods=N_TRANSACTIONS,
        freq="15min",
    ),
})


# -----------------------------
# Attach customer history
# -----------------------------

transactions = transactions.merge(
    customer_profiles,
    on="customer_id",
    how="left",
)


# -----------------------------
# Generate payment failures
# -----------------------------

transactions["payment_status"] = np.random.choice(
    ["failed", "successful"],
    N_TRANSACTIONS,
    p=[0.28, 0.72],
)

failed_mask = transactions["payment_status"] == "failed"

transactions["failure_category"] = "none"

transactions.loc[failed_mask, "failure_category"] = np.random.choice(
    FAILURE_TYPES,
    failed_mask.sum(),
    p=[
        0.25,  # transient
        0.25,  # insufficient funds
        0.12,  # expired payment method
        0.12,  # authentication
        0.12,  # network
        0.08,  # merchant error
        0.06,  # unknown
    ],
)

transactions["failure_code"] = "NONE"

for failure_type, codes in FAILURE_CODES.items():

    mask = transactions["failure_category"] == failure_type

    if mask.any():
        transactions.loc[mask, "failure_code"] = np.random.choice(
            codes,
            mask.sum(),
        )


# -----------------------------
# Attempt number
# -----------------------------

transactions["attempt_number"] = np.where(
    failed_mask,
    np.random.choice(
        [1, 2, 3],
        N_TRANSACTIONS,
        p=[0.60, 0.28, 0.12],
    ),
    1,
)


# -----------------------------
# Temporal features
# -----------------------------

transactions["hour_of_day"] = (
    transactions["timestamp"].dt.hour
)

transactions["day_of_week"] = (
    transactions["timestamp"].dt.dayofweek
)

transactions["is_weekend"] = (
    transactions["day_of_week"] >= 5
).astype(int)


# -----------------------------
# Recovery probability
# -----------------------------

# Start with a base probability
recovery_probability = np.full(
    N_TRANSACTIONS,
    0.55
)


# Failure-specific effects

recovery_probability += np.where(
    transactions["failure_category"] == "transient",
    0.22,
    0,
)

recovery_probability += np.where(
    transactions["failure_category"] == "network_failure",
    0.15,
    0,
)

recovery_probability -= np.where(
    transactions["failure_category"] == "insufficient_funds",
    0.18,
    0,
)

recovery_probability -= np.where(
    transactions["failure_category"] == "expired_payment_method",
    0.12,
    0,
)

recovery_probability -= np.where(
    transactions["failure_category"] == "merchant_error",
    0.25,
    0,
)


# Customer-history effects

recovery_probability -= (
    transactions["customer_failure_rate"] * 0.30
)

recovery_probability += np.minimum(
    transactions["previous_recovery_successes"] * 0.025,
    0.10,
)


# Attempt effects

recovery_probability -= (
    transactions["attempt_number"] - 1
) * 0.12


# Large transactions slightly harder to recover

recovery_probability -= np.clip(
    (transactions["amount"] - 5000) / 50_000,
    0,
    0.10,
)


# Add noise

recovery_probability += np.random.normal(
    0,
    0.08,
    N_TRANSACTIONS,
)


# Keep probability valid

recovery_probability = np.clip(
    recovery_probability,
    0.02,
    0.95,
)


transactions["recovery_probability"] = np.round(
    recovery_probability,
    4,
)


# -----------------------------
# Recovery outcome
# -----------------------------

transactions["recovered"] = 0

recovery_mask = failed_mask

transactions.loc[recovery_mask, "recovered"] = (
    np.random.random(recovery_mask.sum())
    < transactions.loc[
        recovery_mask,
        "recovery_probability"
    ]
).astype(int)


# Successful original payments are not recovery events

transactions.loc[
    transactions["payment_status"] == "successful",
    "recovered"
] = 0


# -----------------------------
# Clean column ordering
# -----------------------------

columns = [
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

transactions = transactions[columns]


# -----------------------------
# Save
# -----------------------------

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True,
)

transactions.to_csv(
    OUTPUT_PATH,
    index=False,
)

print("Dataset generated successfully.")
print(f"Rows: {len(transactions):,}")
print(f"Columns: {len(transactions.columns)}")
print(f"Saved to: {OUTPUT_PATH}")

print("\nPayment status:")
print(
    transactions["payment_status"]
    .value_counts(normalize=True)
    .round(3)
)

print("\nFailure categories:")
print(
    transactions.loc[
        failed_mask,
        "failure_category"
    ]
    .value_counts(normalize=True)
    .round(3)
)

print("\nRecovery rate among failed payments:")
print(
    transactions.loc[
        failed_mask,
        "recovered"
    ].mean().round(3)
)