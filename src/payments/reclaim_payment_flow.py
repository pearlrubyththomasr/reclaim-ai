import sys
from pathlib import Path


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

SRC_DIR = ROOT_DIR / "src"

sys.path.append(str(ROOT_DIR))
sys.path.append(str(SRC_DIR))


# ==================================================
# IMPORTS
# ==================================================

from payments.payment_event import (
    create_payment_failure_event,
)

from payments.recovery_actions import (
    execute_recovery_action,
)

from mlops.inference import (
    predict_recovery,
)


# ==================================================
# PROCESS PAYMENT FAILURE
# ==================================================

def process_payment_failure(event):

    print("\n")
    print("=" * 70)
    print("RECLAIM — AUTONOMOUS REVENUE RECOVERY")
    print("=" * 70)

    # --------------------------------------------------
    # EVENT
    # --------------------------------------------------

    print("\nPAYMENT EVENT")
    print("-" * 70)

    print(
        f"Payment ID:         "
        f"{event['payment_id']}"
    )

    print(
        f"Customer ID:        "
        f"{event['customer_id']}"
    )

    print(
        f"Amount:             "
        f"₹{event['amount']:,.2f}"
    )

    print(
        f"Failure category:   "
        f"{event['failure_category']}"
    )

    print(
        f"Failure code:       "
        f"{event['failure_code']}"
    )

    print(
        f"Attempt:            "
        f"{event['attempt_number']}"
    )

    # --------------------------------------------------
    # ML INFERENCE
    # --------------------------------------------------

    decision = predict_recovery(

        amount=event["amount"],

        payment_method=event[
            "payment_method"
        ],

        merchant_category="subscription",

        subscription_status="active",

        failure_category=event[
            "failure_category"
        ],

        failure_code=event[
            "failure_code"
        ],

        attempt_number=event[
            "attempt_number"
        ],

        previous_transactions=10,

        previous_successes=7,

        previous_failures=3,

        previous_recovery_successes=2,

        customer_failure_rate=0.30,

        hour_of_day=14,

        day_of_week=2,

        is_weekend=0,
    )

    # --------------------------------------------------
    # MODEL OUTPUT
    # --------------------------------------------------

    print("\nMODEL OUTPUT")
    print("-" * 70)

    print(
        f"Recovery probability: "
        f"{decision.recovery_probability:.2%}"
    )

    print(
        f"Expected recovery:    "
        f"₹{decision.expected_revenue:,.2f}"
    )

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------

    print("\nRECLAIM DECISION")
    print("-" * 70)

    print(
        f"Confidence:           "
        f"{decision.confidence}"
    )

    print(
        f"Recommended action:   "
        f"{decision.recommended_action}"
    )

    print("\nReasons:")

    for reason in decision.reason:

        print(
            f"  • {reason}"
        )

    # --------------------------------------------------
    # EXECUTE ACTION
    # --------------------------------------------------

    print("\nRECOVERY EXECUTION")
    print("-" * 70)

    action_result = execute_recovery_action(

        decision.recommended_action,

        event,
    )

    print(
        f"Action:               "
        f"{action_result.action}"
    )

    print(
        f"Status:               "
        f"{action_result.status}"
    )

    print(
        f"Message:              "
        f"{action_result.message}"
    )

    print("\nMetadata:")

    for key, value in (
        action_result.metadata.items()
    ):

        print(
            f"  {key}: {value}"
        )

    print("\n" + "=" * 70)

    print(
        "RECLAIM WORKFLOW COMPLETE"
    )

    print("=" * 70)

    return decision, action_result


# ==================================================
# DEMO
# ==================================================

if __name__ == "__main__":

    event = create_payment_failure_event(

        payment_id="pay_reclaim_001",

        amount=2999.00,

        customer_id="cust_1001",

        payment_method="card",

        failure_category="transient",

        failure_code="gateway_timeout",

        attempt_number=1,
    )

    process_payment_failure(event)