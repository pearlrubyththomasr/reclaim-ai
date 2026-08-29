from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("data/processed/train.csv")


def main():
    df = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("RECLAIM DATA EXPLORATION")
    print("=" * 60)

    # --------------------------------------------------
    # Basic information
    # --------------------------------------------------

    print("\nDataset shape:")
    print(df.shape)

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    # --------------------------------------------------
    # Target
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("RECOVERY DISTRIBUTION")
    print("-" * 60)

    print(
        df["recovered"]
        .value_counts()
        .sort_index()
    )

    print("\nRecovery rate:")
    print(f"{df['recovered'].mean():.2%}")

    # --------------------------------------------------
    # Failure categories
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("RECOVERY BY FAILURE CATEGORY")
    print("-" * 60)

    failure_analysis = (
        df.groupby("failure_category")
        .agg(
            transactions=("recovered", "count"),
            recovered=("recovered", "sum"),
            recovery_rate=("recovered", "mean"),
        )
        .sort_values(
            "recovery_rate",
            ascending=False,
        )
    )

    print(
        failure_analysis.to_string(
            float_format=lambda x: f"{x:.3f}"
        )
    )

    # --------------------------------------------------
    # Payment method
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("RECOVERY BY PAYMENT METHOD")
    print("-" * 60)

    payment_analysis = (
        df.groupby("payment_method")
        .agg(
            transactions=("recovered", "count"),
            recovery_rate=("recovered", "mean"),
        )
        .sort_values(
            "recovery_rate",
            ascending=False,
        )
    )

    print(
        payment_analysis.to_string(
            float_format=lambda x: f"{x:.3f}"
        )
    )

    # --------------------------------------------------
    # Attempt number
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("RECOVERY BY ATTEMPT NUMBER")
    print("-" * 60)

    attempt_analysis = (
        df.groupby("attempt_number")
        .agg(
            transactions=("recovered", "count"),
            recovery_rate=("recovered", "mean"),
        )
        .sort_index()
    )

    print(
        attempt_analysis.to_string(
            float_format=lambda x: f"{x:.3f}"
        )
    )

    # --------------------------------------------------
    # Customer history
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("RECOVERY BY CUSTOMER FAILURE RATE")
    print("-" * 60)

    df["failure_rate_bucket"] = pd.cut(
        df["customer_failure_rate"],
        bins=[-0.01, 0.10, 0.25, 0.50, 1.0],
        labels=[
            "0-10%",
            "10-25%",
            "25-50%",
            "50%+",
        ],
    )

    customer_analysis = (
        df.groupby(
            "failure_rate_bucket",
            observed=False,
        )
        .agg(
            transactions=("recovered", "count"),
            recovery_rate=("recovered", "mean"),
        )
    )

    print(
        customer_analysis.to_string(
            float_format=lambda x: f"{x:.3f}"
        )
    )

    # --------------------------------------------------
    # Amount
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("TRANSACTION AMOUNT")
    print("-" * 60)

    print(
        df["amount"].describe()
    )

    # --------------------------------------------------
    # Correlations
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("NUMERIC CORRELATIONS WITH RECOVERY")
    print("-" * 60)

    numeric_columns = [
        "amount",
        "attempt_number",
        "previous_transactions",
        "previous_successes",
        "previous_failures",
        "previous_recovery_successes",
        "customer_failure_rate",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "recovered",
    ]

    correlations = (
        df[numeric_columns]
        .corr()["recovered"]
        .sort_values(
            ascending=False
        )
    )

    print(correlations)

    # --------------------------------------------------
    # Visualizations
    # --------------------------------------------------

    # Recovery by failure category
    failure_analysis["recovery_rate"].plot(
        kind="bar",
        figsize=(10, 5),
    )

    plt.title(
        "Recovery Rate by Failure Category"
    )

    plt.ylabel(
        "Recovery Rate"
    )

    plt.xlabel(
        "Failure Category"
    )

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.tight_layout()
    plt.show()

    # Recovery by attempt number
    attempt_analysis["recovery_rate"].plot(
        kind="bar",
        figsize=(8, 5),
    )

    plt.title(
        "Recovery Rate by Attempt Number"
    )

    plt.ylabel(
        "Recovery Rate"
    )

    plt.xlabel(
        "Attempt Number"
    )

    plt.tight_layout()
    plt.show()

    # Recovery by customer failure rate
    customer_analysis["recovery_rate"].plot(
        kind="bar",
        figsize=(8, 5),
    )

    plt.title(
        "Recovery Rate by Customer Failure Rate"
    )

    plt.ylabel(
        "Recovery Rate"
    )

    plt.xlabel(
        "Customer Failure Rate"
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()