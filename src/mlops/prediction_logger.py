from pathlib import Path
from datetime import datetime, timezone
import csv


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

LOG_DIR = ROOT_DIR / "logs"

LOG_FILE = LOG_DIR / "predictions.csv"


# ==================================================
# LOG SCHEMA
# ==================================================

FIELDNAMES = [
    "timestamp",
    "amount",
    "failure_category",
    "failure_code",
    "attempt_number",
    "customer_failure_rate",
    "model_version",
    "recovery_probability",
    "expected_revenue",
    "recommended_action",
    "confidence",
    "outcome_status",
    "recovered_amount",
]

# ==================================================
# INITIALIZE LOG
# ==================================================

def initialize_log():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not LOG_FILE.exists():

        with open(
            LOG_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES,
            )

            writer.writeheader()


# ==================================================
# WRITE PREDICTION
# ==================================================

def log_prediction(
    amount: float,
    failure_category: str,
    failure_code: str,
    attempt_number: int,
    customer_failure_rate: float,
    model_version: str,
    recovery_probability: float,
    expected_revenue: float,
    recommended_action: str,
    confidence: str,
    outcome_status: str = "PENDING",
    recovered_amount: float = 0.0,
):

    initialize_log()

    record = {
    "timestamp": datetime.now(
        timezone.utc
    ).isoformat(),

    "amount": amount,

    "failure_category":
        failure_category,

    "failure_code":
        failure_code,

    "attempt_number":
        attempt_number,

    "customer_failure_rate":
        customer_failure_rate,

    "model_version":
        model_version,

    "recovery_probability":
        recovery_probability,

    "expected_revenue":
        expected_revenue,

    "recommended_action":
        recommended_action,

    "confidence":
        confidence,

    "outcome_status":
        outcome_status,

    "recovered_amount":
        recovered_amount,
}
    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writerow(record)