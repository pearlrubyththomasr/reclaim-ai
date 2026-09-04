"""
RECLAIM — Investor / Pitch Demo

A deterministic demonstration of the RECLAIM revenue recovery loop.

IMPORTANT:
The payment events and outcomes in this demo are synthetic.
The ML prediction and decision policy are real.
"""

from __future__ import annotations

import sys
import uuid

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# PATH SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# EXISTING RECLAIM COMPONENTS
# ============================================================

from mlops.inference import predict_recovery
from payments.recovery_actions import execute_recovery_action


# ============================================================
# DEMO DATA MODEL
# ============================================================

@dataclass
class DemoScenario:

    name: str
    description: str

    amount: float

    failure_category: str
    failure_code: str

    payment_method: str

    attempt_number: int
    customer_failure_rate: float

    customer_id: str

    # Expected outcome for the controlled demo.
    #
    # This is NOT used to make the AI decision.
    # It only controls the synthetic result after
    # the AI has made its decision.
    demo_outcome: str

    recovery_fraction: float


@dataclass
class DemoResult:

    scenario: str
    transaction_id: str

    amount: float

    failure_category: str
    failure_code: str

    recovery_probability: float
    expected_revenue: float

    recommended_action: str
    confidence: str
    reason: str

    action_status: str

    outcome_status: str
    recovered_amount: float


# ============================================================
# CONTROLLED SCENARIOS
# ============================================================

def get_demo_scenarios() -> list[DemoScenario]:
    """
    Three deliberately chosen investor-demo scenarios.

    1. Recoverable transient/network failure
    2. Recoverable customer-side failure
    3. Merchant-side failure where intervention should stop
    """

    return [

        # ----------------------------------------------------
        # SCENARIO 1
        # ----------------------------------------------------

        DemoScenario(

            name="Network Timeout",

            description=(
                "Temporary gateway/network failure "
                "on a normally reliable customer."
            ),

            amount=4999.00,

            failure_category="network_failure",

            failure_code="gateway_timeout",

            payment_method="card",

            attempt_number=1,

            customer_failure_rate=0.08,

            customer_id="DEMO-CUSTOMER-001",

            # Synthetic outcome
            demo_outcome="RECOVERED",

            recovery_fraction=0.82,
        ),

        # ----------------------------------------------------
        # SCENARIO 2
        # ----------------------------------------------------

        DemoScenario(

            name="Insufficient Funds",

            description=(
                "Customer payment fails because "
                "funds are temporarily unavailable."
            ),

            amount=3247.00,

            failure_category="insufficient_funds",

            failure_code="insufficient_funds",

            payment_method="upi",

            attempt_number=1,

            customer_failure_rate=0.15,

            customer_id="DEMO-CUSTOMER-002",

            # Synthetic outcome
            demo_outcome="RECOVERED",

            recovery_fraction=0.75,
        ),

        # ----------------------------------------------------
        # SCENARIO 3
        # ----------------------------------------------------

        DemoScenario(

            name="Merchant Configuration Error",

            description=(
                "Merchant-side configuration problem "
                "where another payment attempt is unlikely "
                "to recover the payment."
            ),

            amount=6999.00,

            failure_category="merchant_error",

            failure_code="merchant_configuration_error",

            payment_method="card",

            attempt_number=1,

            customer_failure_rate=0.12,

            customer_id="DEMO-CUSTOMER-003",

            # Synthetic outcome
            demo_outcome="NOT_RECOVERED",

            recovery_fraction=0.00,
        ),
    ]


# ============================================================
# CREATE PAYMENT EVENT
# ============================================================

def create_payment_event(
    scenario: DemoScenario,
) -> dict:
    """
    Create a normalized payment.failed event.

    The event contains all features required by the
    trained RECLAIM recovery prediction model.
    """

    transaction_id = (
        f"demo_txn_{uuid.uuid4().hex[:10]}"
    )

    payment_id = (
        f"demo_pay_{uuid.uuid4().hex[:10]}"
    )

    now = datetime.now(timezone.utc)

    return {

        # ----------------------------------------------------
        # EVENT IDENTITY
        # ----------------------------------------------------

        "event_type": "payment.failed",

        "transaction_id": transaction_id,

        "payment_id": payment_id,

        "customer_id": scenario.customer_id,

        "timestamp": now.isoformat(),

        # ----------------------------------------------------
        # PAYMENT
        # ----------------------------------------------------

        "amount": scenario.amount,

        "currency": "INR",

        "payment_method": scenario.payment_method,

        # ----------------------------------------------------
        # MERCHANT / SUBSCRIPTION
        # ----------------------------------------------------

        "merchant_category": "ecommerce",

        "subscription_status": "active",

        # ----------------------------------------------------
        # FAILURE
        # ----------------------------------------------------

        "failure_category": (
            scenario.failure_category
        ),

        "failure_code": (
            scenario.failure_code
        ),

        "attempt_number": (
            scenario.attempt_number
        ),

        # ----------------------------------------------------
        # CUSTOMER HISTORY
        # ----------------------------------------------------

        "previous_transactions": 20,

        "previous_successes": 18,

        "previous_failures": 2,

        "previous_recovery_successes": 1,

        "customer_failure_rate": (
            scenario.customer_failure_rate
        ),

        # ----------------------------------------------------
        # TEMPORAL FEATURES
        # ----------------------------------------------------

        "hour_of_day": now.hour,

        "day_of_week": now.weekday(),

        "is_weekend": (
            1 if now.weekday() >= 5 else 0
        ),
    }


# ============================================================
# RUN REAL RECLAIM MODEL
# ============================================================

def get_reclaim_decision(event: dict):
    """
    Run the actual registered RECLAIM model and
    decision policy.

    predict_recovery() returns a RecoveryDecision
    dataclass.
    """

    prediction = predict_recovery(

        # ----------------------------------------------------
        # PAYMENT
        # ----------------------------------------------------

        amount=event["amount"],

        payment_method=(
            event["payment_method"]
        ),

        # ----------------------------------------------------
        # MERCHANT
        # ----------------------------------------------------

        merchant_category=(
            event["merchant_category"]
        ),

        subscription_status=(
            event["subscription_status"]
        ),

        # ----------------------------------------------------
        # FAILURE
        # ----------------------------------------------------

        failure_category=(
            event["failure_category"]
        ),

        failure_code=(
            event["failure_code"]
        ),

        attempt_number=(
            event["attempt_number"]
        ),

        # ----------------------------------------------------
        # CUSTOMER HISTORY
        # ----------------------------------------------------

        previous_transactions=(
            event["previous_transactions"]
        ),

        previous_successes=(
            event["previous_successes"]
        ),

        previous_failures=(
            event["previous_failures"]
        ),

        previous_recovery_successes=(
            event["previous_recovery_successes"]
        ),

        customer_failure_rate=(
            event["customer_failure_rate"]
        ),

        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        hour_of_day=(
            event["hour_of_day"]
        ),

        day_of_week=(
            event["day_of_week"]
        ),

        is_weekend=(
            event["is_weekend"]
        ),
    )

    return prediction


# ============================================================
# SYNTHETIC OUTCOME
# ============================================================

def simulate_outcome(
    scenario: DemoScenario,
    action: str,
) -> tuple[str, float]:
    """
    Controlled demo outcome.

    The outcome is deterministic so that the investor
    presentation produces the same result every time.

    IMPORTANT:

    In production, this function would NOT exist.

    The real system would receive the actual payment
    outcome from Razorpay through payment events/webhooks.
    """

    # --------------------------------------------------------
    # NETWORK FAILURE
    # --------------------------------------------------------

    if scenario.failure_category == "network_failure":

        if action == "RETRY":

            recovered = (
                scenario.amount
                * scenario.recovery_fraction
            )

            return "RECOVERED", recovered

        return "FAILED", 0.0

    # --------------------------------------------------------
    # INSUFFICIENT FUNDS
    # --------------------------------------------------------

    if scenario.failure_category == "insufficient_funds":

        if action == "PAYMENT_LINK":

            recovered = (
                scenario.amount
                * scenario.recovery_fraction
            )

            return "RECOVERED", recovered

        return "FAILED", 0.0

    # --------------------------------------------------------
    # MERCHANT ERROR
    # --------------------------------------------------------

    if scenario.failure_category == "merchant_error":

        if action == "NO_ACTION":

            return "NOT_RECOVERED", 0.0

        return "FAILED", 0.0

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return "FAILED", 0.0


# ============================================================
# RUN ONE SCENARIO
# ============================================================

def run_scenario(
    scenario: DemoScenario,
) -> DemoResult:
    """
    Execute one complete RECLAIM investor scenario.

    Flow:

        Payment Event
             ↓
        ML Prediction
             ↓
        Decision Policy
             ↓
        Recovery Action
             ↓
        Synthetic Outcome
             ↓
        Revenue Result
    """

    # --------------------------------------------------------
    # CREATE PAYMENT EVENT
    # --------------------------------------------------------

    event = create_payment_event(scenario)

    # --------------------------------------------------------
    # REAL ML + DECISION
    # --------------------------------------------------------

    prediction = get_reclaim_decision(event)

    # IMPORTANT:
    #
    # prediction is a RecoveryDecision object.
    #
    # Therefore:
    #
    #     prediction.recovery_probability
    #
    # NOT:
    #
    #     prediction["recovery_probability"]

    recovery_probability = float(
        prediction.recovery_probability
    )

    expected_revenue = float(
        prediction.expected_revenue
    )

    recommended_action = (
        prediction.recommended_action
    )

    confidence = prediction.confidence

    reason = prediction.reason

    # --------------------------------------------------------
    # EXECUTE EXISTING RECOVERY ACTION LAYER
    # --------------------------------------------------------
    #
    # The actual function signature is:
    #
    # execute_recovery_action(action, event)
    #
    # Therefore we pass the complete normalized event.
    # --------------------------------------------------------

    action_result = execute_recovery_action(

        action=recommended_action,

        event=event,
    )

    # --------------------------------------------------------
    # CONTROLLED SYNTHETIC OUTCOME
    # --------------------------------------------------------

    outcome_status, recovered_amount = (
        simulate_outcome(

            scenario,

            recommended_action,
        )
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return DemoResult(

        scenario=scenario.name,

        transaction_id=(
            event["transaction_id"]
        ),

        amount=scenario.amount,

        failure_category=(
            scenario.failure_category
        ),

        failure_code=(
            scenario.failure_code
        ),

        recovery_probability=(
            recovery_probability
        ),

        expected_revenue=(
            expected_revenue
        ),

        recommended_action=(
            recommended_action
        ),

        confidence=confidence,

        reason=reason,

        action_status=(
            action_result.status
        ),

        outcome_status=(
            outcome_status
        ),

        recovered_amount=(
            recovered_amount
        ),
    )


# ============================================================
# COMPLETE INVESTOR DEMO
# ============================================================

def run_investor_demo() -> dict:
    """
    Run all controlled investor scenarios and
    calculate aggregate revenue metrics.
    """

    scenarios = get_demo_scenarios()

    results: list[DemoResult] = []

    # --------------------------------------------------------
    # RUN SCENARIOS
    # --------------------------------------------------------

    for scenario in scenarios:

        result = run_scenario(scenario)

        results.append(result)

    # --------------------------------------------------------
    # BASIC COUNTS
    # --------------------------------------------------------

    payments_analyzed = len(results)

    interventions = sum(

        1

        for result in results

        if result.recommended_action != "NO_ACTION"
    )

    recovered_transactions = sum(

        1

        for result in results

        if result.outcome_status == "RECOVERED"
    )

    # --------------------------------------------------------
    # MONEY METRICS
    # --------------------------------------------------------

    total_payment_value = sum(

        result.amount

        for result in results
    )

    expected_revenue = sum(

        result.expected_revenue

        for result in results
    )

    recovered_revenue = sum(

        result.recovered_amount

        for result in results
    )

    # --------------------------------------------------------
    # RECOVERY RATE
    # --------------------------------------------------------

    recovery_rate = (

        recovered_transactions
        / payments_analyzed

        if payments_analyzed

        else 0.0
    )

    # --------------------------------------------------------
    # INTERVENTION SUCCESS
    # --------------------------------------------------------

    intervention_success_rate = (

        recovered_transactions
        / interventions

        if interventions

        else 0.0
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "demo_name": (
            "RECLAIM Investor Demo"
        ),

        "demo_type": (
            "CONTROLLED_SYNTHETIC_SCENARIO"
        ),

        "results": [

            asdict(result)

            for result in results
        ],

        "summary": {

            "payments_analyzed": (
                payments_analyzed
            ),

            "interventions": (
                interventions
            ),

            "recovered_transactions": (
                recovered_transactions
            ),

            "total_payment_value": (
                total_payment_value
            ),

            "expected_revenue": (
                expected_revenue
            ),

            "recovered_revenue": (
                recovered_revenue
            ),

            "recovery_rate": (
                recovery_rate
            ),

            "intervention_success_rate": (
                intervention_success_rate
            ),
        },
    }


# ============================================================
# TERMINAL SCENARIO DISPLAY
# ============================================================

def print_scenario(
    result: DemoResult,
) -> None:

    print()

    print("=" * 70)

    print(
        f"SCENARIO: {result.scenario}"
    )

    print("=" * 70)

    print()

    print(
        f"Payment value        : "
        f"₹{result.amount:,.2f}"
    )

    print(
        f"Failure              : "
        f"{result.failure_category}"
    )

    print(
        f"Failure code         : "
        f"{result.failure_code}"
    )

    print()

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    print("RECLAIM PREDICTION")

    print(
        f"Recovery probability : "
        f"{result.recovery_probability:.2%}"
    )

    print(
        f"Expected recovery    : "
        f"₹{result.expected_revenue:,.2f}"
    )

    print(
        f"Confidence           : "
        f"{result.confidence}"
    )

    print()

    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    print("DECISION")

    print(
        f"Action               : "
        f"{result.recommended_action}"
    )

    print(
        f"Reason               : "
        f"{result.reason}"
    )

    print()

    # --------------------------------------------------------
    # ACTION / OUTCOME
    # --------------------------------------------------------

    print("OUTCOME")

    print(
        f"Action status        : "
        f"{result.action_status}"
    )

    print(
        f"Outcome              : "
        f"{result.outcome_status}"
    )

    print(
        f"Revenue recovered    : "
        f"₹{result.recovered_amount:,.2f}"
    )

    print()


# ============================================================
# TERMINAL SUMMARY
# ============================================================

def print_summary(
    demo: dict,
) -> None:

    summary = demo["summary"]

    print()

    print("#" * 70)

    print(
        "RECLAIM — INVESTOR DEMO RESULTS"
    )

    print("#" * 70)

    print()

    print(
        f"Payments analyzed       : "
        f"{summary['payments_analyzed']}"
    )

    print(
        f"Interventions           : "
        f"{summary['interventions']}"
    )

    print(
        f"Recovered payments      : "
        f"{summary['recovered_transactions']}"
    )

    print(
        f"Payment value analyzed  : "
        f"₹{summary['total_payment_value']:,.2f}"
    )

    print(
        f"Expected recovery       : "
        f"₹{summary['expected_revenue']:,.2f}"
    )

    print(
        f"Recovered revenue       : "
        f"₹{summary['recovered_revenue']:,.2f}"
    )

    print(
        f"Recovery rate           : "
        f"{summary['recovery_rate']:.2%}"
    )

    print(
        f"Intervention success    : "
        f"{summary['intervention_success_rate']:.2%}"
    )

    print()

    print(
        "DEMO DATA: Controlled synthetic scenario"
    )

    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()

    print("#" * 70)

    print("RECLAIM")

    print(
        "AUTONOMOUS REVENUE RECOVERY"
    )

    print("INVESTOR DEMO")

    print("#" * 70)

    print()

    demo = run_investor_demo()

    for item in demo["results"]:

        result = DemoResult(**item)

        print_scenario(result)

    print_summary(demo)