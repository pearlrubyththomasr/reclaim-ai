from pathlib import Path
import sys

import pandas as pd


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))


# ==================================================
# IMPORT DRIFT FUNCTIONS
# ==================================================

from mlops.drift_detector import (
    numeric_drift,
    categorical_drift,
    classify_drift,
)


# ==================================================
# MONITOR MODEL
# ==================================================

def monitor_model(
    reference_file,
    production_file,
):

    # --------------------------------------------------
    # Check files
    # --------------------------------------------------

    if not reference_file.exists():

        raise FileNotFoundError(
            f"Reference dataset not found:\n"
            f"{reference_file}"
        )

    if not production_file.exists():

        raise FileNotFoundError(
            f"Production prediction log not found:\n"
            f"{production_file}"
        )

    # --------------------------------------------------
    # Load data
    # --------------------------------------------------

    reference_df = pd.read_csv(
        reference_file
    )

    production_df = pd.read_csv(
        production_file
    )

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("RECLAIM — MODEL MONITOR")
    print("=" * 70)

    print(
        f"\nReference rows:  "
        f"{len(reference_df)}"
    )

    print(
        f"Production rows: "
        f"{len(production_df)}"
    )

    # --------------------------------------------------
    # Production data warning
    # --------------------------------------------------

    if len(production_df) < 100:

        print("\n⚠ WARNING")

        print(
            "Production sample contains fewer "
            "than 100 predictions."
        )

        print(
            "Drift estimates may be unreliable."
        )

    # ==================================================
    # NUMERIC DRIFT
    # ==================================================

    numeric_columns = [

        "amount",

        "attempt_number",

        "customer_failure_rate",
    ]

    numeric_results = numeric_drift(

        reference_df,

        production_df,

        numeric_columns,
    )

    print("\nNUMERIC DRIFT")
    print("-" * 70)

    if numeric_results:

        for column, psi in (
            numeric_results.items()
        ):

            print(
                f"{column:30s}"
                f"PSI={psi:.4f}"
                f" [{classify_drift(psi)}]"
            )

    else:

        print(
            "No matching numeric columns found."
        )

    # ==================================================
    # CATEGORICAL DRIFT
    # ==================================================

    categorical_columns = [

        "failure_category",

        "failure_code",
    ]

    categorical_results = (
        categorical_drift(

            reference_df,

            production_df,

            categorical_columns,
        )
    )

    print("\nCATEGORICAL DRIFT")
    print("-" * 70)

    if categorical_results:

        for column, psi in (
            categorical_results.items()
        ):

            print(
                f"{column:30s}"
                f"PSI={psi:.4f}"
                f" [{classify_drift(psi)}]"
            )

    else:

        print(
            "No matching categorical columns found."
        )

    # ==================================================
    # ACTION DISTRIBUTION
    # ==================================================

    if "recommended_action" in production_df:

        print("\nACTION DISTRIBUTION")
        print("-" * 70)

        action_distribution = (
            production_df[
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
                f"{action:30s}"
                f"{percentage:.2%}"
            )

    # ==================================================
    # PREDICTION STATISTICS
    # ==================================================

    if "recovery_probability" in production_df:

        probabilities = pd.to_numeric(
            production_df[
                "recovery_probability"
            ],
            errors="coerce",
        ).dropna()

        if len(probabilities) > 0:

            print("\nPREDICTION STATISTICS")
            print("-" * 70)

            print(
                f"Mean probability: "
                f"{probabilities.mean():.2%}"
            )

            print(
                f"Minimum probability: "
                f"{probabilities.min():.2%}"
            )

            print(
                f"Maximum probability: "
                f"{probabilities.max():.2%}"
            )

            print(
                f"Median probability: "
                f"{probabilities.median():.2%}"
            )

    # ==================================================
    # INTERVENTION RATE
    # ==================================================

    if "recommended_action" in production_df:

        interventions = (
            production_df[
                "recommended_action"
            ]
            != "NO_ACTION"
        ).sum()

        intervention_rate = (
            interventions /
            len(production_df)
        )

        print("\nINTERVENTION METRICS")
        print("-" * 70)

        print(
            f"Interventions: "
            f"{interventions}"
        )

        print(
            f"Intervention rate: "
            f"{intervention_rate:.2%}"
        )

    # ==================================================
    # OUTCOME METRICS
    # ==================================================

    if "outcome_status" in production_df:

        print("\nOUTCOME STATUS")
        print("-" * 70)

        print(
            production_df[
                "outcome_status"
            ]
            .value_counts()
            .to_string()
        )

    if "recovered_amount" in production_df:

        recovered_amount = pd.to_numeric(
            production_df[
                "recovered_amount"
            ],
            errors="coerce",
        ).fillna(0)

        print(
            f"\nRecovered revenue: "
            f"₹{recovered_amount.sum():,.2f}"
        )

    # ==================================================
    # FINAL STATUS
    # ==================================================

    all_psi = list(
        numeric_results.values()
    ) + list(
        categorical_results.values()
    )

    if any(
        psi > 0.25
        for psi in all_psi
    ):

        overall_status = "SIGNIFICANT DRIFT"

    elif any(
        psi >= 0.10
        for psi in all_psi
    ):

        overall_status = "MODERATE DRIFT"

    else:

        overall_status = "STABLE"

    print("\nOVERALL MODEL STATUS")
    print("-" * 70)

    print(
        f"Status: {overall_status}"
    )

    print("\n" + "=" * 70)

    print(
        "MODEL MONITORING COMPLETE"
    )

    print("=" * 70)

    return {

        "numeric": numeric_results,

        "categorical": categorical_results,

        "overall_status":
            overall_status,
    }


# ==================================================
# CLI
# ==================================================

if __name__ == "__main__":

    # Your actual validation dataset
    reference_file = (
        ROOT_DIR
        / "data"
        / "processed"
        / "validation.csv"
    )

    # Production prediction log
    production_file = (
        ROOT_DIR
        / "logs"
        / "predictions.csv"
    )

    monitor_model(
        reference_file,
        production_file,
    )