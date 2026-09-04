import sys
from pathlib import Path

import pandas as pd


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))


# ==================================================
# IMPORTS
# ==================================================

from mlops.model_monitor import monitor_model

from agent.retraining_decision import (
    evaluate_retraining_need,
)


# ==================================================
# RETRAINING PIPELINE
# ==================================================

def run_retraining_check():

    # --------------------------------------------------
    # YOUR ACTUAL VALIDATION DATASET
    # --------------------------------------------------

    reference_file = (
        ROOT_DIR
        / "data"
        / "processed"
        / "validation.csv"
    )

    # --------------------------------------------------
    # PRODUCTION PREDICTION LOG
    # --------------------------------------------------

    production_file = (
        ROOT_DIR
        / "logs"
        / "predictions.csv"
    )

    print("\n")
    print("=" * 70)
    print("RECLAIM — RETRAINING CHECK")
    print("=" * 70)

    # --------------------------------------------------
    # FILE VALIDATION
    # --------------------------------------------------

    if not reference_file.exists():

        print(
            "\n❌ Validation dataset not found:"
        )

        print(reference_file)

        return None

    if not production_file.exists():

        print(
            "\n❌ Production prediction log not found:"
        )

        print(production_file)

        return None

    # --------------------------------------------------
    # LOAD PRODUCTION DATA
    # --------------------------------------------------

    production_df = pd.read_csv(
        production_file
    )

    print(
        f"\nProduction predictions: "
        f"{len(production_df)}"
    )

    # --------------------------------------------------
    # MONITOR
    # --------------------------------------------------

    drift_results = monitor_model(

        reference_file,

        production_file,
    )

    # --------------------------------------------------
    # RETRAINING DECISION
    # --------------------------------------------------

    decision = evaluate_retraining_need(

        drift_results=drift_results,

        production_rows=len(
            production_df
        ),
    )

    # --------------------------------------------------
    # DISPLAY DECISION
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("RETRAINING DECISION")
    print("=" * 70)

    print(
        f"\nRetrain required: "
        f"{decision.retrain}"
    )

    print(
        f"Severity: "
        f"{decision.severity}"
    )

    print("\nReasons:")

    for reason in decision.reasons:

        print(
            f"  • {reason}"
        )

    # --------------------------------------------------
    # NEXT STEP
    # --------------------------------------------------

    print("\nRECOMMENDED ACTION")
    print("-" * 70)

    if decision.retrain:

        print(
            "⚠ Model retraining should be initiated."
        )

        print(
            "A candidate model must be trained "
            "and evaluated before promotion."
        )

    elif decision.severity == "INSUFFICIENT_DATA":

        print(
            "⏳ Continue collecting production "
            "predictions before making a retraining decision."
        )

    else:

        print(
            "✅ Current model can remain in production."
        )

    print("\n" + "=" * 70)

    print(
        "RETRAINING CHECK COMPLETE"
    )

    print("=" * 70)

    return decision


# ==================================================
# CLI
# ==================================================

if __name__ == "__main__":

    run_retraining_check()