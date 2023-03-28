import os

### Database
# NOTE: MONGO_CONTAINER_NAME is not defined in the .env file, but in the
# docker-compose.yml file for consistency with the container naming
MONGO_HOST = os.getenv("MONGO_CONTAINER_NAME")
MONGO_USER = os.getenv("MONGO_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_ROOT_PASSWORD")
DB_NAME = os.getenv("MONGO_DATABASE")

PM_COLCTN = os.getenv("PHYSICAL_METER_COLLECTION", "devices")
VM_COLCTN = os.getenv("VIRTUAL_METER_COLLECTION", "virtualDevices")
PM_MEAS_COLCTN = os.getenv(
    "PHYSICAL_METER_MEASUREMENT_COLLECTION", "deviceMeasurements"
)
MODEL_COLCTN = os.getenv("ML_MODEL_COLLECTION", "mlModels")


### Locality for holiday features
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "DE")
SUBDIVISION_CODE = os.getenv("SUBDIVISION_CODE", "")

### Models
DEFAULT_ALGORITHM = os.getenv("DEFAULT_ALGORITHM", "xgboost")
DEFAULT_MEASUREMENT_UNIT = os.getenv("DEFAULT_MEASUREMENT_UNIT", None)

MONGO_DB_NAME = os.getenv("MONGO_DATABASE")
MODEL_FOLDER = os.path.join("app", "data", "models")
os.makedirs(MODEL_FOLDER, exist_ok=True)

N_EPOCHS_TORCH = int(os.getenv("N_EPOCHS_TORCH", 100))

### Hyperparameter optimization with Ray Tune (BOHB)
RAY_N_MODELS = int(os.getenv("RAY_N_MODELS", 32))
RAY_MAX_CONCURRENT = int(os.getenv("RAY_MAX_CONCURRENT", 4))
RAY_REDUCTION_FACTOR = int(os.getenv("RAY_REDUCTION_FACTOR", 2))
RAY_NUM_CPUS = int(os.getenv("RAY_NUM_CPUS", 8))
RAY_NUM_GPUS = int(os.getenv("RAY_NUM_GPUS", 0))
RAY_MAX_T = int(os.getenv("RAY_MAX_T", 100))
