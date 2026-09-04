from pathlib import Path

import mlflow
import mlflow.sklearn


# ==================================================
# RECLAIM MODEL LOADER
# ==================================================

ROOT_DIR = Path(
    __file__
).resolve().parents[2]


MLFLOW_DB = (
    ROOT_DIR / "mlflow.db"
)


REGISTERED_MODEL_NAME = (
    "RECLAIM-Recovery-Model"
)


MODEL_VERSION = "1"


# ==================================================
# CONFIGURE MLFLOW
# ==================================================

mlflow.set_tracking_uri(
    f"sqlite:///{MLFLOW_DB.as_posix()}"
)


# ==================================================
# LOAD REGISTERED MODEL
# ==================================================

def load_model():

    model_uri = (
        f"models:/{REGISTERED_MODEL_NAME}/{MODEL_VERSION}"
    )

    print(
        f"Loading model: "
        f"{REGISTERED_MODEL_NAME} "
        f"v{MODEL_VERSION}"
    )

    model = mlflow.sklearn.load_model(
        model_uri
    )

    print("✓ Model loaded successfully")

    return model