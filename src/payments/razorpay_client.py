import os
from pathlib import Path

import razorpay
from dotenv import load_dotenv


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv(ROOT_DIR / ".env")


# ==================================================
# RAZORPAY TEST CREDENTIALS
# ==================================================

KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


if not KEY_ID or not KEY_SECRET:
    raise RuntimeError(
        "Razorpay test credentials are not configured. "
        "Check the .env file."
    )


# ==================================================
# RAZORPAY CLIENT
# ==================================================

client = razorpay.Client(
    auth=(KEY_ID, KEY_SECRET)
)


# ==================================================
# CREATE TEST ORDER
# ==================================================

def create_test_order(
    amount: float,
    currency: str = "INR",
    receipt: str = "reclaim_test_order",
):

    amount_paise = int(
        round(amount * 100)
    )

    order_data = {
        "amount": amount_paise,
        "currency": currency,
        "receipt": receipt,
    }

    order = client.order.create(
        data=order_data
    )

    return order