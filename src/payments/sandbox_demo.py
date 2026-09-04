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

from payments.reclaim_payment_flow import (
    process_payment_failure,
)


# ==================================================
# TEST CASES
# ==================================================

test_cases = [

    {
        "name": "Transient Failure",

        "failure_category":
            "transient",

        "failure_code":
            "gateway_timeout",
    },

    {
        "name": "Insufficient Funds",

        "failure_category":
            "insufficient_funds",

        "failure_code":
            "INSUFFICIENT_FUNDS",
    },

    {
        "name": "Expired Payment Method",

        "failure_category":
            "expired_payment_method",

        "failure_code":
            "CARD_EXPIRED",
    },

    {
        "name": "Merchant Error",

        "failure_category":
            "merchant_error",

        "failure_code":
            "INVALID_REQUEST",
    },

    {
        "name": "Authentication Failure",

        "failure_category":
            "authentication_failure",

        "failure_code":
            "AUTH_FAILED",
    },
]


# ==================================================
# RUN TESTS
# ==================================================

if __name__ == "__main__":

    for index, test in enumerate(
        test_cases,
        start=1,
    ):

        print("\n\n")

        print(
            "#" * 70
        )

        print(
            f"TEST CASE {index}: "
            f"{test['name']}"
        )

        print(
            "#" * 70
        )

        event = create_payment_failure_event(

            payment_id=(
                f"pay_reclaim_{index:03d}"
            ),

            amount=2999.00,

            customer_id=(
                f"cust_{index:04d}"
            ),

            payment_method="card",

            failure_category=(
                test["failure_category"]
            ),

            failure_code=(
                test["failure_code"]
            ),

            attempt_number=1,
        )

        process_payment_failure(
            event
        )