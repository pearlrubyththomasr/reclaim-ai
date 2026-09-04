from dataclasses import dataclass


# ==================================================
# RETRAINING DECISION
# ==================================================

@dataclass
class RetrainingDecision:

    retrain: bool

    severity: str

    reasons: list


# ==================================================
# EVALUATE
# ==================================================

def evaluate_retraining_need(
    drift_results,
    production_rows,
    minimum_production_rows=100,
):

    reasons = []

    # --------------------------------------------------
    # Not enough data
    # --------------------------------------------------

    if production_rows < minimum_production_rows:

        return RetrainingDecision(

            retrain=False,

            severity="INSUFFICIENT_DATA",

            reasons=[
                (
                    "Not enough production "
                    "predictions for reliable retraining."
                )
            ],
        )

    # --------------------------------------------------
    # Check drift
    # --------------------------------------------------

    significant_drift = []

    for group_name in (
        "numeric",
        "categorical",
    ):

        group = drift_results.get(
            group_name,
            {},
        )

        for column, psi in group.items():

            if psi > 0.25:

                significant_drift.append(
                    column
                )

    if significant_drift:

        reasons.append(
            "Significant feature drift detected: "
            +
            ", ".join(
                significant_drift
            )
        )

    # --------------------------------------------------
    # Final decision
    # --------------------------------------------------

    if significant_drift:

        return RetrainingDecision(

            retrain=True,

            severity="HIGH",

            reasons=reasons,
        )

    return RetrainingDecision(

        retrain=False,

        severity="STABLE",

        reasons=[
            "No significant drift detected."
        ],
    )