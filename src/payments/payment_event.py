from datetime import datetime, timezone


# ==================================================
# CREATE PAYMENT FAILURE EVENT
# ==================================================

def create_payment_failure_event(
    payment_id: str,
    amount: float,
    customer_id: str,
    payment_method: str,
    failure_category: str,
    failure_code: str,
    attempt_number: int = 1,
):
    """
    Create a normalized payment failure event.

    This represents the event that would eventually
    arrive from Razorpay through a webhook.
    """

    return {

        "event_type": "payment.failed",

        "payment_id": payment_id,

        "customer_id": customer_id,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "amount": amount,

        "currency": "INR",

        "payment_method": payment_method,

        "failure_category": failure_category,

        "failure_code": failure_code,

        "attempt_number": attempt_number,
    }