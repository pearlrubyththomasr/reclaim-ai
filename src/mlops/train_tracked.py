from pathlib import Path
import sys

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ==================================================
# PROJECT ROOT
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

sys.path.append(
    str(ROOT_DIR)
)


# ==================================================
# IMPORT CONFIGURATION
# ==================================================

from configs.model_config import (
    MODEL_NAME,
    MODEL_VERSION,
    RANDOM_STATE,
    MAX_ITER,
    DECISION_THRESHOLD,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURES,
    TARGET,
)
REGISTERED_MODEL_NAME = "RECLAIM-Recovery-Model"

# ==================================================
# DATA PATHS
# ==================================================

TRAIN_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "train.csv"
)

VALIDATION_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "validation.csv"
)


# ==================================================
# LOAD DATA
# ==================================================

train_df = pd.read_csv(
    TRAIN_PATH
)

validation_df = pd.read_csv(
    VALIDATION_PATH
)

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_validation = validation_df[FEATURES]
y_validation = validation_df[TARGET]


# ==================================================
# PREPROCESSOR
# ==================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            NUMERIC_FEATURES,
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES,
        ),
    ]
)


# ==================================================
# MODEL
# ==================================================

model = LogisticRegression(
    max_iter=MAX_ITER,
    random_state=RANDOM_STATE,
)


pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# ==================================================
# MLflow CONFIGURATION
# ==================================================

MLFLOW_DB = (
    ROOT_DIR / "mlflow.db"
)

mlflow.set_tracking_uri(
    f"sqlite:///{MLFLOW_DB.as_posix()}"
)

mlflow.set_experiment(
    "RECLAIM-Recovery-Prediction"
)


# ==================================================
# START RUN
# ==================================================

with mlflow.start_run():

    print("=" * 70)
    print("RECLAIM — MLFLOW TRAINING RUN")
    print("=" * 70)

    print("\nTraining model...")

    pipeline.fit(
        X_train,
        y_train,
    )

    print("✓ Training complete")


    # ==================================================
    # PREDICTIONS
    # ==================================================

    probabilities = pipeline.predict_proba(
        X_validation
    )[:, 1]

    predictions = (
        probabilities
        >= DECISION_THRESHOLD
    ).astype(int)


    # ==================================================
    # METRICS
    # ==================================================

    accuracy = accuracy_score(
        y_validation,
        predictions,
    )

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_validation,
        probabilities,
    )

    pr_auc = average_precision_score(
        y_validation,
        probabilities,
    )

    brier = brier_score_loss(
        y_validation,
        probabilities,
    )

    logloss = log_loss(
        y_validation,
        probabilities,
    )


    # ==================================================
    # LOG PARAMETERS
    # ==================================================

    mlflow.log_param(
        "model_name",
        MODEL_NAME,
    )

    mlflow.log_param(
        "model_version",
        MODEL_VERSION,
    )

    mlflow.log_param(
        "random_state",
        RANDOM_STATE,
    )

    mlflow.log_param(
        "max_iter",
        MAX_ITER,
    )

    mlflow.log_param(
        "decision_threshold",
        DECISION_THRESHOLD,
    )

    mlflow.log_param(
        "num_numeric_features",
        len(NUMERIC_FEATURES),
    )

    mlflow.log_param(
        "num_categorical_features",
        len(CATEGORICAL_FEATURES),
    )


    # ==================================================
    # LOG METRICS
    # ==================================================

    mlflow.log_metric(
        "accuracy",
        accuracy,
    )

    mlflow.log_metric(
        "precision",
        precision,
    )

    mlflow.log_metric(
        "recall",
        recall,
    )

    mlflow.log_metric(
        "f1",
        f1,
    )

    mlflow.log_metric(
        "roc_auc",
        roc_auc,
    )

    mlflow.log_metric(
        "pr_auc",
        pr_auc,
    )

    mlflow.log_metric(
        "brier_score",
        brier,
    )

    mlflow.log_metric(
        "log_loss",
        logloss,
    )


    # ==================================================
    # LOG DATASET INFORMATION
    # ==================================================

    mlflow.log_param(
        "training_rows",
        len(train_df),
    )

    mlflow.log_param(
        "validation_rows",
        len(validation_df),
    )

    mlflow.log_param(
        "training_recovery_rate",
        round(
            float(y_train.mean()),
            4,
        ),
    )

    mlflow.log_param(
        "validation_recovery_rate",
        round(
            float(y_validation.mean()),
            4,
        ),
    )


    # ==================================================
    # LOG AND REGISTER MODEL
    # ==================================================

    model_info = mlflow.sklearn.log_model(
        pipeline,
        name="reclaim_logistic_regression",
        registered_model_name=REGISTERED_MODEL_NAME,
    )

    print("\n✓ Model logged to MLflow")
    print(
        f"Model URI: {model_info.model_uri}"
    )

    # ==================================================
    # TERMINAL OUTPUT
    # ==================================================

    print("\nValidation Metrics")
    print("-" * 70)

    print(
        f"Accuracy:          {accuracy:.4f}"
    )

    print(
        f"Precision:         {precision:.4f}"
    )

    print(
        f"Recall:            {recall:.4f}"
    )

    print(
        f"F1:                {f1:.4f}"
    )

    print(
        f"ROC-AUC:           {roc_auc:.4f}"
    )

    print(
        f"PR-AUC:            {pr_auc:.4f}"
    )

    print(
        f"Brier Score:       {brier:.4f}"
    )

    print(
        f"Log Loss:           {logloss:.4f}"
    )

    print("\nMLflow Run")
    print("-" * 70)

    print(
        f"Run ID: {mlflow.active_run().info.run_id}"
    )

    print(
        f"Experiment: {mlflow.get_experiment_by_name(
            'RECLAIM-Recovery-Prediction'
        ).name}"
    )

    print("\n" + "=" * 70)
    print("✅ MLFLOW RUN COMPLETE")
    print("=" * 70)