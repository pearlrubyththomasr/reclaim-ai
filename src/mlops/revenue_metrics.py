from pathlib import Path

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
# LOAD DATA
# ==================================================

df = pd.read_csv(
    LOG_FILE
)


# ==================================================
# BASIC METRICS
# ==================================================

total_transactions = len(df)

intervention_actions = {
    "RETRY",
    "PAYMENT_LINK",
    "PAYMENT_METHOD_UPDATE",
}

intervention_mask = (
    df["recommended_action"]
    .isin(intervention_actions)
)

interventions = (
    intervention_mask.sum()
)

recovered_mask = (
    df["outcome_status"]
    == "RECOVERED"
)

recovered_transactions = (
    recovered_mask.sum()
)

recovered_revenue = (
    df.loc[
        recovered_mask,
        "recovered_amount"
    ].sum()
)

expected_revenue = (
    df["expected_revenue"].sum()
)

total_payment_value = (
    df["amount"].sum()
)


# ==================================================
# RATES
# ==================================================

intervention_rate = (
    interventions
    / total_transactions
    if total_transactions
    else 0
)

recovery_rate = (
    recovered_transactions
    / total_transactions
    if total_transactions
    else 0
)

intervention_recovery_rate = (
    recovered_transactions
    / interventions
    if interventions
    else 0
)


# ==================================================
# OUTPUT
# ==================================================

print("=" * 70)
print("RECLAIM — REVENUE RECOVERY METRICS")
print("=" * 70)

print("\nTransaction Metrics")
print("-" * 70)

print(
    f"Total failed payments: "
    f"{total_transactions}"
)

print(
    f"Interventions: "
    f"{interventions}"
)

print(
    f"Intervention rate: "
    f"{intervention_rate:.2%}"
)

print("\nRecovery Metrics")
print("-" * 70)

print(
    f"Recovered transactions: "
    f"{recovered_transactions}"
)

print(
    f"Overall recovery rate: "
    f"{recovery_rate:.2%}"
)

print(
    f"Intervention success rate: "
    f"{intervention_recovery_rate:.2%}"
)

print("\nRevenue Metrics")
print("-" * 70)

print(
    f"Total payment value: "
    f"₹{total_payment_value:,.2f}"
)

print(
    f"Expected recovery: "
    f"₹{expected_revenue:,.2f}"
)

print(
    f"Actual recovered revenue: "
    f"₹{recovered_revenue:,.2f}"
)

print("\n" + "=" * 70)
print("✅ REVENUE METRICS COMPLETE")
print("=" * 70)