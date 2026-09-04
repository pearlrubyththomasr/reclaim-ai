from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ==================================================
# PROJECT PATHS
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

SRC_DIR = ROOT_DIR / "src"

sys.path.append(
    str(ROOT_DIR)
)

sys.path.append(
    str(SRC_DIR)
)


# ==================================================
# DATA PATHS
# ==================================================

REFERENCE_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "validation.csv"
)

PREDICTION_LOG_PATH = (
    ROOT_DIR
    / "logs"
    / "predictions.csv"
)


# ==================================================
# MONITORING CONFIGURATION
# ==================================================

PSI_WARNING = 0.10
PSI_CRITICAL = 0.25

MIN_MONITORING_ROWS = 100


# ==================================================
# PSI — NUMERIC
# ==================================================

def calculate_numeric_psi(
    reference,
    current,
    bins=10,
):

    reference = np.asarray(
        reference,
        dtype=float,
    )

    current = np.asarray(
        current,
        dtype=float,
    )

    reference = reference[
        np.isfinite(reference)
    ]

    current = current[
        np.isfinite(current)
    ]

    if len(reference) == 0 or len(current) == 0:
        return np.nan

    breakpoints = np.quantile(
        reference,
        np.linspace(
            0,
            1,
            bins + 1,
        ),
    )

    breakpoints = np.unique(
        breakpoints
    )

    if len(breakpoints) < 3:
        return 0.0

    reference_counts, _ = np.histogram(
        reference,
        bins=breakpoints,
    )

    current_counts, _ = np.histogram(
        current,
        bins=breakpoints,
    )

    reference_pct = (
        reference_counts
        / len(reference)
    )

    current_pct = (
        current_counts
        / len(current)
    )

    epsilon = 1e-6

    reference_pct = np.clip(
        reference_pct,
        epsilon,
        None,
    )

    current_pct = np.clip(
        current_pct,
        epsilon,
        None,
    )

    psi = np.sum(
        (
            current_pct
            - reference_pct
        )
        * np.log(
            current_pct
            / reference_pct
        )
    )

    return float(psi)


# ==================================================
# PSI — CATEGORICAL
# ==================================================

def calculate_categorical_psi(
    reference,
    current,
):

    reference = (
        pd.Series(reference)
        .fillna("UNKNOWN")
        .astype(str)
    )

    current = (
        pd.Series(current)
        .fillna("UNKNOWN")
        .astype(str)
    )

    categories = set(
        reference.unique()
    ).union(
        set(current.unique())
    )

    epsilon = 1e-6

    psi = 0.0

    for category in categories:

        reference_pct = (
            (reference == category).mean()
        )

        current_pct = (
            (current == category).mean()
        )

        reference_pct = max(
            reference_pct,
            epsilon,
        )

        current_pct = max(
            current_pct,
            epsilon,
        )

        psi += (
            current_pct
            - reference_pct
        ) * np.log(
            current_pct
            / reference_pct
        )

    return float(psi)


# ==================================================
# PSI INTERPRETATION
# ==================================================

def interpret_psi(psi):

    if np.isnan(psi):

        return "N/A"

    if psi >= PSI_CRITICAL:

        return "CRITICAL"

    if psi >= PSI_WARNING:

        return "WARNING"

    return "STABLE"


# ==================================================
# LOAD DATA
# ==================================================

print("=" * 70)
print("RECLAIM — MODEL MONITORING")
print("=" * 70)


if not PREDICTION_LOG_PATH.exists():

    print(
        "\n❌ Prediction log not found."
    )

    sys.exit(1)


reference_df = pd.read_csv(
    REFERENCE_PATH
)

current_df = pd.read_csv(
    PREDICTION_LOG_PATH
)


print("\nMonitoring Dataset")
print("-" * 70)

print(
    f"Reference rows: "
    f"{len(reference_df)}"
)

print(
    f"Production predictions: "
    f"{len(current_df)}"
)


# ==================================================
# SAMPLE SIZE CHECK
# ==================================================

if len(current_df) < MIN_MONITORING_ROWS:

    print("\n⚠️ Monitoring sample is small.")

    print(
        f"At least {MIN_MONITORING_ROWS} "
        f"production predictions are recommended "
        f"for reliable drift estimates."
    )


# ==================================================
# PREDICTION MONITORING
# ==================================================

print("\nPrediction Statistics")
print("-" * 70)

if "recovery_probability" in current_df:

    probability_mean = (
        current_df[
            "recovery_probability"
        ].mean()
    )

    probability_std = (
        current_df[
            "recovery_probability"
        ].std()
    )

    print(
        f"Average recovery probability: "
        f"{probability_mean:.4f}"
    )

    print(
        f"Probability standard deviation: "
        f"{probability_std:.4f}"
    )


# ==================================================
# INTERVENTION RATE
# ==================================================

if "recommended_action" in current_df:

    intervention_actions = {
        "RETRY",
        "PAYMENT_LINK",
        "PAYMENT_METHOD_UPDATE",
    }

    intervention_mask = (
        current_df[
            "recommended_action"
        ].isin(intervention_actions)
    )

    intervention_rate = (
        intervention_mask.mean()
    )

    print(
        f"Intervention rate: "
        f"{intervention_rate:.2%}"
    )


# ==================================================
# ACTION DISTRIBUTION
# ==================================================

if "recommended_action" in current_df:

    print("\nAction Distribution")
    print("-" * 70)

    action_distribution = (
        current_df[
            "recommended_action"
        ]
        .value_counts(
            normalize=True
        )
    )

    for action, percentage in (
        action_distribution.items()
    ):

        print(
            f"{action:<25}"
            f"{percentage:.2%}"
        )


# ==================================================
# NUMERIC DRIFT
# ==================================================

numeric_features = [
    "amount",
    "attempt_number",
    "customer_failure_rate",
]


print("\nNumeric Data Drift")
print("-" * 70)

for feature in numeric_features:

    if (
        feature not in reference_df.columns
        or feature not in current_df.columns
    ):
        continue

    psi = calculate_numeric_psi(
        reference_df[feature],
        current_df[feature],
    )

    status = interpret_psi(
        psi
    )

    print(
        f"{feature:<30}"
        f"PSI: {psi:.4f}   "
        f"{status}"
    )


# ==================================================
# CATEGORICAL DRIFT
# ==================================================

categorical_features = [
    "failure_category",
    "failure_code",
]


print("\nCategorical Data Drift")
print("-" * 70)

for feature in categorical_features:

    if (
        feature not in reference_df.columns
        or feature not in current_df.columns
    ):
        continue

    psi = calculate_categorical_psi(
        reference_df[feature],
        current_df[feature],
    )

    status = interpret_psi(
        psi
    )

    print(
        f"{feature:<30}"
        f"PSI: {psi:.4f}   "
        f"{status}"
    )


# ==================================================
# MODEL PROBABILITY DRIFT
# ==================================================

if "recovery_probability" in current_df:

    # Reference probabilities require a model
    # prediction column. Since the reference
    # dataset does not contain predictions,
    # we explicitly report this limitation.

    print("\nPrediction Drift")
    print("-" * 70)

    print(
        "Reference prediction distribution:"
    )

    print(
        "Not available yet."
    )

    print(
        "Next monitoring phase will store "
        "reference model predictions for "
        "probability-distribution comparison."
    )


# ==================================================
# FINAL STATUS
# ==================================================

print("\n" + "=" * 70)
print("MONITORING COMPLETE")
print("=" * 70)

print(
    "\nPSI interpretation:"
)

print(
    "  < 0.10   → STABLE"
)

print(
    "  0.10–0.25 → WARNING"
)

print(
    "  >= 0.25  → CRITICAL"
)

print("\n" + "=" * 70)