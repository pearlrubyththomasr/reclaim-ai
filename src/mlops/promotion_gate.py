from pathlib import Path
import sys

import mlflow
from mlflow import MlflowClient


# ==================================================
# PROJECT ROOT
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

MLFLOW_DB = ROOT_DIR / "mlflow.db"


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_NAME = "RECLAIM-Recovery-Model"

MIN_F1 = 0.65
MIN_ROC_AUC = 0.70
MIN_PR_AUC = 0.65


# ==================================================
# MLFLOW
# ==================================================

mlflow.set_tracking_uri(
    f"sqlite:///{MLFLOW_DB.as_posix()}"
)

client = MlflowClient()


# ==================================================
# FIND LATEST MODEL VERSION
# ==================================================

versions = client.search_model_versions(
    f"name='{MODEL_NAME}'"
)

if not versions:
    raise RuntimeError(
        f"No registered versions found for {MODEL_NAME}"
    )


latest_version = max(
    versions,
    key=lambda v: int(v.version),
)


# ==================================================
# GET RUN
# ==================================================

run_id = latest_version.run_id

run = client.get_run(run_id)

metrics = run.data.metrics


f1 = metrics.get("f1")
roc_auc = metrics.get("roc_auc")
pr_auc = metrics.get("pr_auc")


# ==================================================
# DISPLAY
# ==================================================

print("=" * 70)
print("RECLAIM — MODEL PROMOTION GATE")
print("=" * 70)

print("\nCandidate Model")
print("-" * 70)

print(
    f"Model:       {MODEL_NAME}"
)

print(
    f"Version:     {latest_version.version}"
)

print(
    f"Run ID:      {run_id}"
)


print("\nValidation Metrics")
print("-" * 70)

print(
    f"F1:          {f1:.4f}"
)

print(
    f"ROC-AUC:     {roc_auc:.4f}"
)

print(
    f"PR-AUC:      {pr_auc:.4f}"
)


# ==================================================
# VALIDATION GATE
# ==================================================

checks = {
    "F1": f1 >= MIN_F1,
    "ROC-AUC": roc_auc >= MIN_ROC_AUC,
    "PR-AUC": pr_auc >= MIN_PR_AUC,
}


print("\nPromotion Criteria")
print("-" * 70)

print(
    f"F1 >= {MIN_F1:.2f}: "
    f"{'PASS' if checks['F1'] else 'FAIL'}"
)

print(
    f"ROC-AUC >= {MIN_ROC_AUC:.2f}: "
    f"{'PASS' if checks['ROC-AUC'] else 'FAIL'}"
)

print(
    f"PR-AUC >= {MIN_PR_AUC:.2f}: "
    f"{'PASS' if checks['PR-AUC'] else 'FAIL'}"
)


# ==================================================
# PROMOTION DECISION
# ==================================================

if all(checks.values()):

    print("\n" + "=" * 70)
    print("✅ PROMOTION GATE PASSED")
    print("=" * 70)

    print(
        f"\nModel {MODEL_NAME} "
        f"v{latest_version.version} "
        f"is eligible for production."
    )

else:

    print("\n" + "=" * 70)
    print("❌ PROMOTION GATE FAILED")
    print("=" * 70)

    print(
        "\nModel does not meet the minimum "
        "production criteria."
    )

    sys.exit(1)