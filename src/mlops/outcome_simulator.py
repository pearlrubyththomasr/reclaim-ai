from pathlib import Path
import random

import pandas as pd


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

LOG_FILE = (
    ROOT_DIR
    / "logs"
    / "predictions.csv"
)


# ==================================================
# CONFIGURATION
# ==================================================

RANDOM_STATE = 42

random.seed(
    RANDOM_STATE
)


# ==================================================
# LOAD PREDICTIONS
# ==================================================

if not LOG_FILE.exists():

    raise FileNotFoundError(
        "Prediction log not found."
    )


df = pd.read_csv(
    LOG_FILE
)


# ==================================================
# CHECK REQUIRED COLUMNS
# ==================================================

required_columns = {
    "amount",
    "recovery_probability",
    "recommended_action",
    "outcome_status",
    "recovered_amount",
}


missing = (
    required_columns
    - set(df.columns)
)


if missing:

    raise ValueError(
        f"Missing columns: {missing}"
    )


# ==================================================
# SIMULATE OUTCOMES
# ==================================================

updated = 0


for index, row in df.iterrows():

    if row["outcome_status"] != "PENDING":
        continue


    probability = float(
        row["recovery_probability"]
    )

    action = row[
        "recommended_action"
    ]

    amount = float(
        row["amount"]
    )


    # ----------------------------------------------
    # No-action transactions
    # ----------------------------------------------

    if action == "NO_ACTION":

        recovered = False


    else:

        recovered = (
            random.random()
            < probability
        )


    # ----------------------------------------------
    # Store outcome
    # ----------------------------------------------

    if recovered:

        df.at[
            index,
            "outcome_status"
        ] = "RECOVERED"

        df.at[
            index,
            "recovered_amount"
        ] = amount

    else:

        df.at[
            index,
            "outcome_status"
        ] = "NOT_RECOVERED"

        df.at[
            index,
            "recovered_amount"
        ] = 0.0


    updated += 1


# ==================================================
# SAVE
# ==================================================

df.to_csv(
    LOG_FILE,
    index=False,
)


# ==================================================
# SUMMARY
# ==================================================

recovered_mask = (
    df["outcome_status"]
    == "RECOVERED"
)

recovered_count = (
    recovered_mask.sum()
)

recovered_revenue = (
    df.loc[
        recovered_mask,
        "recovered_amount"
    ].sum()
)

total_amount = (
    df["amount"].sum()
)

recovery_rate = (
    recovered_count / len(df)
    if len(df) > 0
    else 0
)


# ==================================================
# OUTPUT
# ==================================================

print("=" * 70)
print("RECLAIM — OUTCOME SIMULATION")
print("=" * 70)

print(
    f"\nPredictions processed: "
    f"{updated}"
)

print(
    f"Recovered transactions: "
    f"{recovered_count}"
)

print(
    f"Recovery rate: "
    f"{recovery_rate:.2%}"
)

print(
    f"Recovered revenue: "
    f"₹{recovered_revenue:,.2f}"
)

print(
    f"Total payment value: "
    f"₹{total_amount:,.2f}"
)

print("\n" + "=" * 70)
print("✅ OUTCOME SIMULATION COMPLETE")
print("=" * 70)