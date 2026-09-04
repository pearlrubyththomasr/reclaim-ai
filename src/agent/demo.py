from pathlib import Path
import sys


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

from payments.payment_event import (
    create_payment_failure_event
)

from agent.agent import (
    ReclaimAgent
)


# ==================================================
# TEST CASES
# ==================================================

TEST_CASES = [

    {
        "name": "Gateway Timeout",

        "failure_category": "transient",

        "failure_code": "gateway_timeout",

        "amount": 2999.00,
    },

    {
        "name": "Insufficient Funds",

        "failure_category": "insufficient_funds",

        "failure_code": "INSUFFICIENT_FUNDS",

        "amount": 4999.00,
    },

    {
        "name": "Expired Card",

        "failure_category": "expired_payment_method",

        "failure_code": "CARD_EXPIRED",

        "amount": 1999.00,
    },

    {
        "name": "Merchant Configuration",

        "failure_category": "merchant_error",

        "failure_code": "INVALID_REQUEST",

        "amount": 9999.00,
    },
]


# ==================================================
# MAIN
# ==================================================

def main():

    agent = ReclaimAgent()

    for index, test in enumerate(
        TEST_CASES,
        start=1
    ):

        event = create_payment_failure_event(

            payment_id=(
                f"agent_payment_{index:03d}"
            ),

            amount=test["amount"],

            customer_id=(
                f"agent_customer_{index:03d}"
            ),

            payment_method="credit_card",

            failure_category=(
                test["failure_category"]
            ),

            failure_code=(
                test["failure_code"]
            ),

            attempt_number=1,
        )

        print("\n\n")

        print("#" * 70)

        print(
            f"SCENARIO {index}: "
            f"{test['name']}"
        )

        print("#" * 70)

        result = agent.run(event)

        print("\nDIAGNOSIS")
        print("-" * 70)

        print(
            f"Category: "
            f"{result.diagnosis.category}"
        )

        print(
            f"Severity: "
            f"{result.diagnosis.severity}"
        )

        print(
            f"Recoverability: "
            f"{result.diagnosis.recoverability}"
        )

        print(
            f"Explanation: "
            f"{result.diagnosis.explanation}"
        )

        print("\nMODEL")
        print("-" * 70)

        print(
            f"Recovery probability: "
            f"{result.recovery_probability:.2%}"
        )

        print(
            f"Expected revenue: "
            f"₹{result.expected_revenue:,.2f}"
        )

        print(
            f"Confidence: "
            f"{result.confidence}"
        )

        print("\nACTION")
        print("-" * 70)

        print(
            f"Recommended action: "
            f"{result.recommended_action}"
        )

        print(
            f"Execution status: "
            f"{result.action_status}"
        )

        print(
            f"Message: "
            f"{result.action_message}"
        )

    print("\n\n")

    print("=" * 70)

    print(
        "RECLAIM AGENT DEMONSTRATION COMPLETE"
    )

    print("=" * 70)


# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()