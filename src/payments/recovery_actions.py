from dataclasses import dataclass
from typing import Dict


# ==================================================
# RECOVERY ACTION RESULT
# ==================================================

@dataclass
class RecoveryActionResult:

    action: str

    status: str

    message: str

    metadata: Dict


# ==================================================
# RETRY
# ==================================================

def execute_retry(event):

    return RecoveryActionResult(

        action="RETRY",

        status="SIMULATED",

        message=(
            "Retry workflow initiated for "
            "potentially recoverable payment."
        ),

        metadata={
            "payment_id": event["payment_id"],
            "attempt_number": event["attempt_number"] + 1,
        },
    )


# ==================================================
# PAYMENT LINK
# ==================================================

def execute_payment_link(event):

    return RecoveryActionResult(

        action="PAYMENT_LINK",

        status="SIMULATED",

        message=(
            "Alternative payment-link workflow "
            "initiated."
        ),

        metadata={
            "payment_id": event["payment_id"],
            "amount": event["amount"],
        },
    )


# ==================================================
# PAYMENT METHOD UPDATE
# ==================================================

def execute_payment_method_update(event):

    return RecoveryActionResult(

        action="PAYMENT_METHOD_UPDATE",

        status="SIMULATED",

        message=(
            "Customer payment-method update "
            "workflow initiated."
        ),

        metadata={
            "payment_id": event["payment_id"],
        },
    )


# ==================================================
# NO ACTION
# ==================================================

def execute_no_action(event):

    return RecoveryActionResult(

        action="NO_ACTION",

        status="SKIPPED",

        message=(
            "No recovery action recommended."
        ),

        metadata={
            "payment_id": event["payment_id"],
        },
    )


# ==================================================
# ACTION DISPATCHER
# ==================================================

def execute_recovery_action(
    action: str,
    event,
):

    actions = {

        "RETRY": execute_retry,

        "PAYMENT_LINK": execute_payment_link,

        "PAYMENT_METHOD_UPDATE":
            execute_payment_method_update,

        "NO_ACTION": execute_no_action,
    }

    if action not in actions:

        raise ValueError(
            f"Unsupported recovery action: {action}"
        )

    return actions[action](event)