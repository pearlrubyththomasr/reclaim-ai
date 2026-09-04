from pathlib import Path
import sys

import pandas as pd


# ==================================================
# PROJECT PATH
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_NAME = "RECLAIM-Recovery-Model"
PRODUCTION_VERSION = 1

VALIDATION_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "validation.csv"
)

PRODUCTION_LOG = (
    ROOT_DIR
    / "logs"
    / "predictions.csv"
)


# ==================================================
# MODEL LIFECYCLE
# ==================================================

class ModelLifecycle:

    """
    RECLAIM model lifecycle controller.

    Lifecycle:

        Production Model
              ↓
        Monitor
              ↓
        Detect Drift
              ↓
        Retraining Decision
              ↓
        Candidate Model
              ↓
        Promotion Gate
              ↓
        Production
    """

    def __init__(
        self,
        model_name=MODEL_NAME,
        production_version=PRODUCTION_VERSION,
    ):

        self.model_name = model_name

        self.production_version = (
            production_version
        )

    # ==================================================
    # FILE STATUS
    # ==================================================

    def check_data_sources(self):

        validation_exists = (
            VALIDATION_FILE.exists()
        )

        production_log_exists = (
            PRODUCTION_LOG.exists()
        )

        production_rows = 0

        if production_log_exists:

            production_df = pd.read_csv(
                PRODUCTION_LOG
            )

            production_rows = len(
                production_df
            )

        return {

            "validation_dataset":
                validation_exists,

            "validation_path":
                str(VALIDATION_FILE),

            "production_log":
                production_log_exists,

            "production_log_path":
                str(PRODUCTION_LOG),

            "production_rows":
                production_rows,
        }

    # ==================================================
    # MODEL STATUS
    # ==================================================

    def get_status(self):

        data_status = (
            self.check_data_sources()
        )

        return {

            "model":
                self.model_name,

            "production_version":
                self.production_version,

            "monitoring":
                "ACTIVE",

            "drift_detection":
                "ACTIVE",

            "retraining":
                "CONDITIONAL",

            "promotion_gate":
                "ACTIVE",

            "validation_dataset":
                data_status[
                    "validation_dataset"
                ],

            "production_log":
                data_status[
                    "production_log"
                ],

            "production_predictions":
                data_status[
                    "production_rows"
                ],
        }

    # ==================================================
    # PRINT STATUS
    # ==================================================

    def print_status(self):

        status = self.get_status()

        print("\n")
        print("=" * 70)
        print("RECLAIM — MODEL LIFECYCLE")
        print("=" * 70)

        print("\nMODEL")
        print("-" * 70)

        print(
            f"Model:                  "
            f"{status['model']}"
        )

        print(
            f"Production version:     "
            f"{status['production_version']}"
        )

        print("\nMLOPS COMPONENTS")
        print("-" * 70)

        print(
            f"Monitoring:             "
            f"{status['monitoring']}"
        )

        print(
            f"Drift detection:        "
            f"{status['drift_detection']}"
        )

        print(
            f"Retraining:             "
            f"{status['retraining']}"
        )

        print(
            f"Promotion gate:         "
            f"{status['promotion_gate']}"
        )

        print("\nDATA SOURCES")
        print("-" * 70)

        validation_status = (
            "AVAILABLE"
            if status["validation_dataset"]
            else "MISSING"
        )

        production_status = (
            "AVAILABLE"
            if status["production_log"]
            else "MISSING"
        )

        print(
            f"Validation dataset:     "
            f"{validation_status}"
        )

        print(
            f"Production log:         "
            f"{production_status}"
        )

        print(
            f"Production predictions: "
            f"{status['production_predictions']}"
        )

        print("\nPATHS")
        print("-" * 70)

        print(
            f"Validation: "
            f"{VALIDATION_FILE}"
        )

        print(
            f"Production: "
            f"{PRODUCTION_LOG}"
        )

        print("\nLIFECYCLE")
        print("-" * 70)

        print(
            "Production Model"
        )

        print(
            "      ↓"
        )

        print(
            "Monitoring + Drift Detection"
        )

        print(
            "      ↓"
        )

        print(
            "Retraining Decision"
        )

        print(
            "      ↓"
        )

        print(
            "Candidate Model"
        )

        print(
            "      ↓"
        )

        print(
            "Promotion Gate"
        )

        print(
            "      ↓"
        )

        print(
            "New Production Version"
        )

        print("\n" + "=" * 70)

        print(
            "MODEL LIFECYCLE STATUS COMPLETE"
        )

        print("=" * 70)


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    lifecycle = ModelLifecycle()

    lifecycle.print_status()