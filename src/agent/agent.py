import sys
from pathlib import Path

from dataclasses import dataclass, asdict


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

from agent.diagnostics import (
    diagnose_failure,
)

from mlops.inference import (
    predict_recovery,
)

from payments.recovery_actions import (
    execute_recovery_action,
)


# ==================================================
# AGENT RESULT
# ==================================================

@dataclass
class AgentResult:

    payment_id: str

    diagnosis: object

    recovery_probability: float

    expected_revenue: float

    confidence: str

    recommended_action: str

    action_status: str

    action_message: str


# ==================================================
# RECLAIM AGENT
# ==================================================

class ReclaimAgent:

    """
    Autonomous revenue recovery agent.

    Pipeline:

    Diagnose
        ↓
    Predict
        ↓
    Value
        ↓
    Decide
        ↓
    Act
    """

    def run(self, event):

        # ==========================================
        # 1. DIAGNOSE
        # ==========================================

        diagnosis = diagnose_failure(

            failure_category=event[
                "failure_category"
            ],

            failure_code=event[
                "failure_code"
            ],

            attempt_number=event[
                "attempt_number"
            ],
        )

        # ==========================================
        # 2. ML PREDICTION + DECISION
        # ==========================================

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

        # ==========================================
        # 3. AUTONOMOUS ACTION
        # ==========================================

        action_result = execute_recovery_action(

            decision.recommended_action,

            event,
        )

        # ==========================================
        # 4. PACKAGE RESULT
        # ==========================================

        return AgentResult(

            payment_id=event[
                "payment_id"
            ],

            diagnosis=diagnosis,

            recovery_probability=(
                decision.recovery_probability
            ),

            expected_revenue=(
                decision.expected_revenue
            ),

            confidence=(
                decision.confidence
            ),

            recommended_action=(
                decision.recommended_action
            ),

            action_status=(
                action_result.status
            ),

            action_message=(
                action_result.message
            ),
        )


# ==================================================
# CLI DEMO
# ==================================================

if __name__ == "__main__":

    from payments.payment_event import (
        create_payment_failure_event,
    )

    event = create_payment_failure_event(

        payment_id="pay_agent_001",

        amount=2999.00,

        customer_id="cust_agent_001",

        payment_method="card",

        failure_category="transient",

        failure_code="gateway_timeout",

        attempt_number=1,
    )

    agent = ReclaimAgent()

    result = agent.run(event)

    print("\n")
    print("=" * 70)
    print("RECLAIM — AUTONOMOUS AGENT")
    print("=" * 70)

    print("\nPAYMENT")
    print("-" * 70)

    print(
        f"Payment ID:       "
        f"{result.payment_id}"
    )

    print("\nDIAGNOSIS")
    print("-" * 70)

    print(
        f"Category:         "
        f"{result.diagnosis.category}"
    )

    print(
        f"Severity:         "
        f"{result.diagnosis.severity}"
    )

    print(
        f"Recoverability:   "
        f"{result.diagnosis.recoverability}"
    )

    print(
        f"Explanation:      "
        f"{result.diagnosis.explanation}"
    )

    print("\nDECISION")
    print("-" * 70)

    print(
        f"Recovery probability: "
        f"{result.recovery_probability:.2%}"
    )

    print(
        f"Expected revenue:     "
        f"₹{result.expected_revenue:,.2f}"
    )

    print(
        f"Confidence:           "
        f"{result.confidence}"
    )

    print(
        f"Action:               "
        f"{result.recommended_action}"
    )

    print("\nEXECUTION")
    print("-" * 70)

    print(
        f"Status:               "
        f"{result.action_status}"
    )

    print(
        f"Message:              "
        f"{result.action_message}"
    )

    print("\n" + "=" * 70)
    print("AUTONOMOUS AGENT COMPLETE")
    print("=" * 70)