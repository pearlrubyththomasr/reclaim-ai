from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

LOG_FILE = ROOT_DIR / "logs" / "predictions.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=5)
def load_predictions():
    """
    Load the production prediction log.

    Returns:
        pandas.DataFrame
    """

    if not LOG_FILE.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(LOG_FILE)
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    # --------------------------------------------------------
    # Normalize numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "amount",
        "attempt_number",
        "customer_failure_rate",
        "recovery_probability",
        "expected_revenue",
        "recovered_amount",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Normalize timestamps
    # --------------------------------------------------------

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )

        # Newest events first
        df = df.sort_values(
            "timestamp",
            ascending=False,
        )

    return df.reset_index(drop=True)


# ============================================================
# SAFE NUMERIC ACCESS
# ============================================================

def numeric_column(df, column, default=0.0):
    """
    Return a numeric Series safely.
    """

    if column not in df.columns:
        return pd.Series(
            default,
            index=df.index,
            dtype="float64",
        )

    return pd.to_numeric(
        df[column],
        errors="coerce",
    ).fillna(default)


# ============================================================
# CORE METRICS
# ============================================================

def calculate_metrics(df):
    """
    Calculate revenue recovery metrics used throughout
    the dashboard.
    """

    if df.empty:

        return {
            "failed_payments": 0,
            "interventions": 0,
            "intervention_rate": 0.0,
            "recovered_transactions": 0,
            "recovery_rate": 0.0,
            "intervention_success_rate": 0.0,
            "revenue_at_risk": 0.0,
            "expected_revenue": 0.0,
            "recovered_revenue": 0.0,
        }

    failed_payments = len(df)

    # --------------------------------------------------------
    # Intervention count
    # --------------------------------------------------------

    if "recommended_action" in df.columns:

        actions = (
            df["recommended_action"]
            .fillna("NO_ACTION")
            .astype(str)
            .str.upper()
        )

        interventions = int(
            (actions != "NO_ACTION").sum()
        )

    else:

        interventions = 0

    intervention_rate = (
        interventions / failed_payments
        if failed_payments
        else 0.0
    )

    # --------------------------------------------------------
    # Outcome / recovery
    # --------------------------------------------------------

    if "outcome_status" in df.columns:

        statuses = (
            df["outcome_status"]
            .fillna("")
            .astype(str)
            .str.upper()
        )

        recovered_mask = statuses == "RECOVERED"

    elif "recovered_amount" in df.columns:

        recovered_mask = (
            numeric_column(
                df,
                "recovered_amount",
            ) > 0
        )

    else:

        recovered_mask = pd.Series(
            False,
            index=df.index,
        )

    recovered_transactions = int(
        recovered_mask.sum()
    )

    recovery_rate = (
        recovered_transactions / failed_payments
        if failed_payments
        else 0.0
    )

    # --------------------------------------------------------
    # Intervention success
    # --------------------------------------------------------

    intervention_success_rate = (
        recovered_transactions / interventions
        if interventions
        else 0.0
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    amount = numeric_column(
        df,
        "amount",
    )

    revenue_at_risk = float(
        amount.sum()
    )

    expected_revenue = float(
        numeric_column(
            df,
            "expected_revenue",
        ).sum()
    )

    recovered_revenue = float(
        numeric_column(
            df,
            "recovered_amount",
        ).sum()
    )

    return {
        "failed_payments": failed_payments,
        "interventions": interventions,
        "intervention_rate": intervention_rate,
        "recovered_transactions": recovered_transactions,
        "recovery_rate": recovery_rate,
        "intervention_success_rate": intervention_success_rate,
        "revenue_at_risk": revenue_at_risk,
        "expected_revenue": expected_revenue,
        "recovered_revenue": recovered_revenue,
    }


# ============================================================
# ACTION DISTRIBUTION
# ============================================================

def action_distribution(df):
    """
    Count recovery actions selected by the agent/policy.
    """

    if df.empty or "recommended_action" not in df.columns:
        return pd.DataFrame(
            columns=[
                "recommended_action",
                "count",
            ]
        )

    result = (
        df["recommended_action"]
        .fillna("UNKNOWN")
        .astype(str)
        .value_counts()
        .rename_axis("recommended_action")
        .reset_index(name="count")
    )

    return result


# ============================================================
# FAILURE DISTRIBUTION
# ============================================================

def failure_distribution(df):
    """
    Count payment failures by failure category.
    """

    if df.empty or "failure_category" not in df.columns:
        return pd.DataFrame(
            columns=[
                "failure_category",
                "count",
            ]
        )

    result = (
        df["failure_category"]
        .fillna("unknown")
        .astype(str)
        .value_counts()
        .rename_axis("failure_category")
        .reset_index(name="count")
    )

    return result


# ============================================================
# RECENT EVENTS
# ============================================================

def recent_events(df, limit=10):
    """
    Return the most recent payment recovery events.
    """

    if df.empty:
        return pd.DataFrame()

    result = df.copy()

    if "timestamp" in result.columns:

        result = result.sort_values(
            "timestamp",
            ascending=False,
        )

    return result.head(limit).reset_index(drop=True)


# ============================================================
# ACTION SUCCESS METRICS
# ============================================================

def action_performance(df):
    """
    Calculate recovery performance by action.

    Useful for the Recovery Operations page.
    """

    if (
        df.empty
        or "recommended_action" not in df.columns
    ):
        return pd.DataFrame()

    result = df.copy()

    result["action"] = (
        result["recommended_action"]
        .fillna("UNKNOWN")
        .astype(str)
    )

    if "outcome_status" in result.columns:

        result["recovered"] = (
            result["outcome_status"]
            .fillna("")
            .astype(str)
            .str.upper()
            == "RECOVERED"
        )

    elif "recovered_amount" in result.columns:

        result["recovered"] = (
            numeric_column(
                result,
                "recovered_amount",
            ) > 0
        )

    else:

        result["recovered"] = False

    grouped = (
        result
        .groupby("action")
        .agg(
            interventions=("action", "size"),
            recovered=("recovered", "sum"),
        )
        .reset_index()
    )

    grouped["success_rate"] = (
        grouped["recovered"]
        / grouped["interventions"]
    )

    grouped["success_rate"] = (
        grouped["success_rate"]
        .fillna(0)
    )

    return grouped.sort_values(
        "interventions",
        ascending=False,
    )


# ============================================================
# FAILURE PERFORMANCE
# ============================================================

def failure_performance(df):
    """
    Calculate recovery performance by failure category.
    """

    if (
        df.empty
        or "failure_category" not in df.columns
    ):
        return pd.DataFrame()

    result = df.copy()

    result["failure"] = (
        result["failure_category"]
        .fillna("unknown")
        .astype(str)
    )

    if "outcome_status" in result.columns:

        result["recovered"] = (
            result["outcome_status"]
            .fillna("")
            .astype(str)
            .str.upper()
            == "RECOVERED"
        )

    elif "recovered_amount" in result.columns:

        result["recovered"] = (
            numeric_column(
                result,
                "recovered_amount",
            ) > 0
        )

    else:

        result["recovered"] = False

    grouped = (
        result
        .groupby("failure")
        .agg(
            failed_payments=("failure", "size"),
            recovered=("recovered", "sum"),
        )
        .reset_index()
    )

    grouped["recovery_rate"] = (
        grouped["recovered"]
        / grouped["failed_payments"]
    )

    grouped["recovery_rate"] = (
        grouped["recovery_rate"]
        .fillna(0)
    )

    return grouped.sort_values(
        "failed_payments",
        ascending=False,
    )


# ============================================================
# MODEL SUMMARY
# ============================================================

def model_summary():
    """
    Static summary of the currently frozen production model.

    These values correspond to the evaluated RECLAIM v1 model.
    """

    return {
        "model_name": "RECLAIM-Recovery-Model",
        "version": "1",
        "algorithm": "Logistic Regression",
        "threshold": 0.35,

        "accuracy": 0.6567,
        "precision": 0.6013,
        "recall": 0.8341,
        "f1": 0.6988,

        "roc_auc": 0.7340,
        "pr_auc": 0.6880,

        "brier": 0.2094,
        "log_loss": 0.6075,
    }


# ============================================================
# SYSTEM STATUS
# ============================================================

def system_status(df):
    """
    Determine basic dashboard health from available data.
    """

    if df.empty:
        return {
            "status": "WAITING",
            "message": "No prediction events recorded",
        }

    return {
        "status": "OPERATIONAL",
        "message": f"{len(df):,} prediction events available",
    }