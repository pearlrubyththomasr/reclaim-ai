from dataclasses import dataclass
from datetime import datetime, timezone


# ==================================================
# FEEDBACK RECORD
# ==================================================

@dataclass
class RecoveryFeedback:

    payment_id: str

    predicted_probability: float

    recommended_action: str

    expected_revenue: float

    recovered: bool

    recovered_amount: float

    timestamp: str


# ==================================================
# CREATE FEEDBACK
# ==================================================

def create_feedback(
    payment_id: str,
    predicted_probability: float,
    recommended_action: str,
    expected_revenue: float,
    recovered: bool,
    recovered_amount: float,
):

    return RecoveryFeedback(

        payment_id=payment_id,

        predicted_probability=(
            predicted_probability
        ),

        recommended_action=(
            recommended_action
        ),

        expected_revenue=(
            expected_revenue
        ),

        recovered=recovered,

        recovered_amount=(
            recovered_amount
        ),

        timestamp=datetime.now(
            timezone.utc
        ).isoformat(),
    )


# ==================================================
# FEEDBACK SUMMARY
# ==================================================

def summarize_feedback(feedback_records):

    if not feedback_records:

        return {
            "total": 0,
            "recovered": 0,
            "recovery_rate": 0.0,
            "actual_revenue": 0.0,
            "expected_revenue": 0.0,
        }

    total = len(
        feedback_records
    )

    recovered = sum(
        1
        for record in feedback_records
        if record.recovered
    )

    actual_revenue = sum(
        record.recovered_amount
        for record in feedback_records
    )

    expected_revenue = sum(
        record.expected_revenue
        for record in feedback_records
    )

    return {

        "total": total,

        "recovered": recovered,

        "recovery_rate": (
            recovered / total
        ),

        "actual_revenue": (
            actual_revenue
        ),

        "expected_revenue": (
            expected_revenue
        ),
    }