from pathlib import Path

import numpy as np
import pandas as pd


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

LOG_FILE = (
    ROOT_DIR /
    "logs" /
    "predictions.csv"
)


# ==================================================
# PSI
# ==================================================

def calculate_psi(
    reference,
    current,
    bins=10,
):
    """
    Population Stability Index.

    PSI interpretation:

    < 0.10  -> little/no drift
    0.10-0.25 -> moderate drift
    > 0.25 -> significant drift
    """

    reference = np.asarray(
        reference,
        dtype=float
    )

    current = np.asarray(
        current,
        dtype=float
    )

    reference = reference[
        np.isfinite(reference)
    ]

    current = current[
        np.isfinite(current)
    ]

    if len(reference) < 10:
        return 0.0

    if len(current) < 10:
        return 0.0

    breakpoints = np.percentile(
        reference,
        np.linspace(
            0,
            100,
            bins + 1,
        ),
    )

    breakpoints = np.unique(
        breakpoints
    )

    if len(breakpoints) < 3:

        return 0.0

    reference_counts, _ = np.histogram(
        reference,
        bins=breakpoints,
    )

    current_counts, _ = np.histogram(
        current,
        bins=breakpoints,
    )

    reference_pct = (
        reference_counts /
        len(reference)
    )

    current_pct = (
        current_counts /
        len(current)
    )

    epsilon = 1e-6

    reference_pct = np.clip(
        reference_pct,
        epsilon,
        None,
    )

    current_pct = np.clip(
        current_pct,
        epsilon,
        None,
    )

    psi = np.sum(
        (
            current_pct -
            reference_pct
        )
        *
        np.log(
            current_pct /
            reference_pct
        )
    )

    return float(psi)


# ==================================================
# NUMERIC DRIFT
# ==================================================

def numeric_drift(
    reference_df,
    current_df,
    columns,
):

    results = {}

    for column in columns:

        if (
            column not in reference_df
            or column not in current_df
        ):
            continue

        results[column] = calculate_psi(
            reference_df[column],
            current_df[column],
        )

    return results


# ==================================================
# CATEGORICAL DRIFT
# ==================================================

def categorical_drift(
    reference_df,
    current_df,
    columns,
):

    results = {}

    for column in columns:

        if (
            column not in reference_df
            or column not in current_df
        ):
            continue

        reference_dist = (
            reference_df[column]
            .value_counts(
                normalize=True
            )
        )

        current_dist = (
            current_df[column]
            .value_counts(
                normalize=True
            )
        )

        categories = set(
            reference_dist.index
        ).union(
            current_dist.index
        )

        psi = 0.0

        for category in categories:

            ref = max(
                reference_dist.get(
                    category,
                    0.0,
                ),
                1e-6,
            )

            cur = max(
                current_dist.get(
                    category,
                    0.0,
                ),
                1e-6,
            )

            psi += (
                (cur - ref)
                *
                np.log(cur / ref)
            )

        results[column] = float(
            psi
        )

    return results


# ==================================================
# DRIFT STATUS
# ==================================================

def classify_drift(psi):

    if psi < 0.10:

        return "STABLE"

    if psi < 0.25:

        return "MODERATE"

    return "SIGNIFICANT"