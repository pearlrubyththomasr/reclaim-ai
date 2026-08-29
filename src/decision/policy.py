from dataclasses import dataclass


@dataclass
class RecoveryDecision:
    recovery_probability: float
    expected_revenue: float
    recommended_action: str
    confidence: str
    reason: list[str]


def decide_recovery_action(
    recovery_probability: float,
    amount: float,
    failure_category: str,
    attempt_number: int,
    customer_failure_rate: float,
) -> RecoveryDecision:

    reasons = []

    # --------------------------------------------------
    # Determine confidence
    # --------------------------------------------------

    if recovery_probability >= 0.70:
        confidence = "HIGH"

    elif recovery_probability >= 0.35:
        confidence = "MEDIUM"

    else:
        confidence = "LOW"

    # --------------------------------------------------
    # Expected revenue
    # --------------------------------------------------

    expected_revenue = (
        recovery_probability * amount
    )

    # --------------------------------------------------
    # Decision policy
    # --------------------------------------------------

    # Very low probability:
    # Recovery is unlikely enough that intervention
    # is not worthwhile.
    if recovery_probability < 0.20:

        action = "NO_ACTION"

        reasons.append(
            "Recovery probability is too low for intervention"
        )

    # Repeated attempts:
    # Avoid automatically retrying after multiple failures.
    elif attempt_number >= 3:

        action = "NO_ACTION"

        reasons.append(
            "Multiple previous attempts detected"
        )

        reasons.append(
            "Automatic retry avoided after repeated failures"
        )

    # Medium-low probability:
    # Only allow low-friction alternatives.
    elif recovery_probability < 0.35:

        if failure_category == "insufficient_funds":

            action = "PAYMENT_LINK"

            reasons.append(
                "Low-cost alternative payment path"
            )

            reasons.append(
                "Insufficient funds detected"
            )

        elif failure_category in {
            "expired_payment_method",
            "authentication_failure",
        }:

            action = "PAYMENT_METHOD_UPDATE"

            reasons.append(
                "Customer action may resolve the failure"
            )

        else:

            action = "NO_ACTION"

            reasons.append(
                "Recovery probability below intervention threshold"
            )

    # Recovery probability >= 0.35:
    # Standard recovery actions are allowed.
    else:

        if failure_category in {
            "transient",
            "network_failure",
        } and attempt_number == 1:

            action = "RETRY"

            reasons.append(
                "Failure type is potentially transient"
            )

            reasons.append(
                "Retry count is still low"
            )

        elif failure_category in {
            "expired_payment_method",
            "authentication_failure",
        }:

            action = "PAYMENT_METHOD_UPDATE"

            reasons.append(
                "Failure may require customer action"
            )

        elif failure_category == "insufficient_funds":

            action = "PAYMENT_LINK"

            reasons.append(
                "Insufficient funds detected"
            )

            reasons.append(
                "Alternative payment method recommended"
            )

        elif failure_category == "merchant_error":

            action = "NO_ACTION"

            reasons.append(
                "Merchant-side error should be resolved first"
            )

        else:

            action = "RETRY"

            reasons.append(
                "Recovery probability exceeds decision threshold"
            )

    # --------------------------------------------------
    # Additional customer context
    # --------------------------------------------------

    if customer_failure_rate >= 0.50:

        reasons.append(
            "Customer has high historical failure rate"
        )

    elif customer_failure_rate <= 0.10:

        reasons.append(
            "Customer has strong historical payment reliability"
        )

    # --------------------------------------------------
    # Return decision
    # --------------------------------------------------

    return RecoveryDecision(
        recovery_probability=recovery_probability,
        expected_revenue=expected_revenue,
        recommended_action=action,
        confidence=confidence,
        reason=reasons,
    )