from dataclasses import dataclass


# ==================================================
# DIAGNOSIS RESULT
# ==================================================

@dataclass
class FailureDiagnosis:

    category: str

    severity: str

    recoverability: str

    explanation: str

    recommended_strategy: str


# ==================================================
# DIAGNOSE PAYMENT FAILURE
# ==================================================

def diagnose_failure(
    failure_category: str,
    failure_code: str,
    attempt_number: int,
):
    """
    Convert a raw payment failure into an
    interpretable diagnosis for the RECLAIM agent.
    """

    category = failure_category.lower()

    # --------------------------------------------------
    # TRANSIENT
    # --------------------------------------------------

    if category == "transient":

        return FailureDiagnosis(

            category=category,

            severity="MEDIUM",

            recoverability="HIGH",

            explanation=(
                "The failure appears temporary and "
                "may resolve without customer intervention."
            ),

            recommended_strategy="RETRY",
        )

    # --------------------------------------------------
    # NETWORK FAILURE
    # --------------------------------------------------

    if category == "network_failure":

        return FailureDiagnosis(

            category=category,

            severity="MEDIUM",

            recoverability="HIGH",

            explanation=(
                "A network or gateway communication "
                "failure was detected."
            ),

            recommended_strategy="RETRY",
        )

    # --------------------------------------------------
    # INSUFFICIENT FUNDS
    # --------------------------------------------------

    if category == "insufficient_funds":

        return FailureDiagnosis(

            category=category,

            severity="HIGH",

            recoverability="MEDIUM",

            explanation=(
                "The customer's payment method does "
                "not currently have sufficient funds."
            ),

            recommended_strategy="PAYMENT_LINK",
        )

    # --------------------------------------------------
    # EXPIRED PAYMENT METHOD
    # --------------------------------------------------

    if category == "expired_payment_method":

        return FailureDiagnosis(

            category=category,

            severity="HIGH",

            recoverability="MEDIUM",

            explanation=(
                "The payment method appears to have "
                "expired and requires customer action."
            ),

            recommended_strategy="PAYMENT_METHOD_UPDATE",
        )

    # --------------------------------------------------
    # AUTHENTICATION FAILURE
    # --------------------------------------------------

    if category == "authentication_failure":

        return FailureDiagnosis(

            category=category,

            severity="HIGH",

            recoverability="MEDIUM",

            explanation=(
                "Payment authentication failed. "
                "Customer verification may be required."
            ),

            recommended_strategy="PAYMENT_METHOD_UPDATE",
        )

    # --------------------------------------------------
    # MERCHANT ERROR
    # --------------------------------------------------

    if category == "merchant_error":

        return FailureDiagnosis(

            category=category,

            severity="CRITICAL",

            recoverability="LOW",

            explanation=(
                "The failure appears related to merchant "
                "configuration or request processing."
            ),

            recommended_strategy="NO_ACTION",
        )

    # --------------------------------------------------
    # UNKNOWN FAILURE
    # --------------------------------------------------

    return FailureDiagnosis(

        category=category,

        severity="UNKNOWN",

        recoverability="UNKNOWN",

        explanation=(
            f"Unrecognized payment failure: "
            f"{failure_code}"
        ),

        recommended_strategy="NO_ACTION",
    )