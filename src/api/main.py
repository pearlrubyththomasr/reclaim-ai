from contextlib import asynccontextmanager
from pathlib import Path
import sys

import pandas as pd


# ==================================================
# PROJECT PATHS
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

SRC_DIR = ROOT_DIR / "src"

sys.path.append(
    str(ROOT_DIR)
)

sys.path.append(
    str(SRC_DIR)
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from mlops.prediction_logger import (
    log_prediction,
)
# ==================================================
# PROJECT PATHS
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

SRC_DIR = ROOT_DIR / "src"

sys.path.append(
    str(ROOT_DIR)
)

sys.path.append(
    str(SRC_DIR)
)


# ==================================================
# RECLAIM IMPORTS
# ==================================================

from configs.model_config import FEATURES

from decision.policy import (
    decide_recovery_action,
)

from mlops.model_loader import (
    load_model,
)


# ==================================================
# MODEL STORAGE
# ==================================================

model = None
MODEL_VERSION = "1"

# ==================================================
# APPLICATION LIFESPAN
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global model

    print(
        "Loading RECLAIM production model..."
    )

    model = load_model()

    print(
        "✓ RECLAIM model ready"
    )

    yield

    print(
        "Shutting down RECLAIM API"
    )


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="RECLAIM API",
    description=(
        "AI-powered failed payment "
        "recovery decision service"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ==================================================
# REQUEST SCHEMA
# ==================================================

class PaymentFailureRequest(BaseModel):

    amount: float = Field(
        gt=0
    )

    attempt_number: int = Field(
        ge=1
    )

    previous_transactions: int = Field(
        ge=0
    )

    previous_successes: int = Field(
        ge=0
    )

    previous_failures: int = Field(
        ge=0
    )

    previous_recovery_successes: int = Field(
        ge=0
    )

    customer_failure_rate: float = Field(
        ge=0,
        le=1,
    )

    hour_of_day: int = Field(
        ge=0,
        le=23,
    )

    day_of_week: int = Field(
        ge=0,
        le=6,
    )

    is_weekend: int = Field(
        ge=0,
        le=1,
    )

    payment_method: str

    merchant_category: str

    subscription_status: str

    failure_category: str

    failure_code: str


# ==================================================
# RESPONSE SCHEMA
# ==================================================

class RecoveryResponse(BaseModel):

    recovery_probability: float

    expected_revenue: float

    recommended_action: str

    confidence: str

    reasons: list[str]


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {
        "service": "RECLAIM",
        "status": "running",
        "model": "RECLAIM-Recovery-Model",
        "version": "1",
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": (
            "healthy"
            if model is not None
            else "model_not_loaded"
        )
    }


# ==================================================
# PREDICTION ENDPOINT
# ==================================================

@app.post(
    "/predict",
    response_model=RecoveryResponse,
)
def predict_payment_recovery(
    payment: PaymentFailureRequest,
):

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="Model is not loaded",
        )

    # ----------------------------------------------
    # Convert request to model input
    # ----------------------------------------------

    transaction = payment.model_dump()

    transaction_df = pd.DataFrame(
        [transaction]
    )

    # ----------------------------------------------
    # ML prediction
    # ----------------------------------------------

    try:

        probability = model.predict_proba(
            transaction_df[FEATURES]
        )[0][1]

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Prediction failed",
        ) from exc

    # ----------------------------------------------
    # Decision engine
    # ----------------------------------------------

    decision = decide_recovery_action(
        recovery_probability=float(
            probability
        ),
        amount=payment.amount,
        failure_category=(
            payment.failure_category
        ),
        attempt_number=(
            payment.attempt_number
        ),
        customer_failure_rate=(
            payment.customer_failure_rate
        ),
    )
        # ----------------------------------------------
    # AUDIT LOG
    # ----------------------------------------------

    log_prediction(
        amount=payment.amount,
        failure_category=(
            payment.failure_category
        ),
        failure_code=(
            payment.failure_code
        ),
        attempt_number=(
            payment.attempt_number
        ),
        customer_failure_rate=(
            payment.customer_failure_rate
        ),
        model_version=MODEL_VERSION,
        recovery_probability=float(
            probability
        ),
        expected_revenue=float(
            decision.expected_revenue
        ),
        recommended_action=(
            decision.recommended_action
        ),
        confidence=decision.confidence,
    )

    # ----------------------------------------------
    # Response
    # ----------------------------------------------

    return RecoveryResponse(
        recovery_probability=round(
            decision.recovery_probability,
            4,
        ),
        expected_revenue=round(
            decision.expected_revenue,
            2,
        ),
        recommended_action=(
            decision.recommended_action
        ),
        confidence=decision.confidence,
        reasons=decision.reason,
    )