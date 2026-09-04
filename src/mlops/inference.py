from pathlib import Path
import sys

import pandas as pd


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.append(str(ROOT_DIR))
sys.path.append(str(SRC_DIR))


# ==================================================
# IMPORT RECLAIM COMPONENTS
# ==================================================

from configs.model_config import FEATURES
from decision.policy import decide_recovery_action
from mlops.model_loader import load_model


# ==================================================
# LOAD REGISTERED MODEL
# ==================================================

model = load_model()


# ==================================================
# REUSABLE PREDICTION FUNCTION
# ==================================================

def predict_recovery(
    amount,
    payment_method,
    merchant_category,
    subscription_status,
    failure_category,
    failure_code,
    attempt_number,
    previous_transactions,
    previous_successes,
    previous_failures,
    previous_recovery_successes,
    customer_failure_rate,
    hour_of_day,
    day_of_week,
    is_weekend,
):
    """
    Run the registered RECLAIM model and decision policy
    for a single payment failure.
    """

    transaction = {
        "amount": amount,
        "attempt_number": attempt_number,
        "previous_transactions": previous_transactions,
        "previous_successes": previous_successes,
        "previous_failures": previous_failures,
        "previous_recovery_successes": previous_recovery_successes,
        "customer_failure_rate": customer_failure_rate,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "payment_method": payment_method,
        "merchant_category": merchant_category,
        "subscription_status": subscription_status,
        "failure_category": failure_category,
        "failure_code": failure_code,
    }

    transaction_df = pd.DataFrame([transaction])

    # ------------------------------
    # ML prediction
    # ------------------------------

    probability = model.predict_proba(
        transaction_df[FEATURES]
    )[0][1]

    # ------------------------------
    # Decision engine
    # ------------------------------

    decision = decide_recovery_action(
        recovery_probability=float(probability),
        amount=amount,
        failure_category=failure_category,
        attempt_number=attempt_number,
        customer_failure_rate=customer_failure_rate,
    )

    return decision


# ==================================================
# STANDALONE PRODUCTION DEMO
# ==================================================

if __name__ == "__main__":

    transaction = {
        "amount": 2998.41,
        "attempt_number": 1,
        "previous_transactions": 22,
        "previous_successes": 18,
        "previous_failures": 4,
        "previous_recovery_successes": 2,
        "customer_failure_rate": 0.181818,
        "hour_of_day": 0,
        "day_of_week": 3,
        "is_weekend": 0,
        "payment_method": "credit_card",
        "merchant_category": "saas",
        "subscription_status": "active",
        "failure_category": "insufficient_funds",
        "failure_code": "INSUFFICIENT_FUNDS",
    }

    transaction_df = pd.DataFrame([transaction])

    probability = model.predict_proba(
        transaction_df[FEATURES]
    )[0][1]

    decision = decide_recovery_action(
        recovery_probability=float(probability),
        amount=transaction["amount"],
        failure_category=transaction["failure_category"],
        attempt_number=transaction["attempt_number"],
        customer_failure_rate=transaction["customer_failure_rate"],
    )

    print("\n" + "=" * 70)
    print("RECLAIM — PRODUCTION INFERENCE")
    print("=" * 70)

    print("\nTransaction")
    print("-" * 70)

    print(f"Amount:             ₹{transaction['amount']:,.2f}")
    print(f"Failure category:   {transaction['failure_category']}")
    print(f"Failure code:       {transaction['failure_code']}")
    print(f"Attempt:            {transaction['attempt_number']}")

    print("\nMODEL OUTPUT")
    print("-" * 70)

    print(f"Recovery probability: {probability:.2%}")
    print(f"Expected recovery:     ₹{decision.expected_revenue:,.2f}")

    print("\nRECLAIM DECISION")
    print("-" * 70)

    print(f"Confidence: {decision.confidence}")
    print(f"Recommended action: {decision.recommended_action}")

    print("\nReasons:")

    for reason in decision.reason:
        print(f"  • {reason}")

    print("\n" + "=" * 70)
    print("✅ PRODUCTION INFERENCE COMPLETE")
    print("=" * 70)