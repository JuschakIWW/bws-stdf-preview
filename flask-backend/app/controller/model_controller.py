import os
import joblib
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta

from app.controller import data_controller
from app.utils.feature_processing import get_time_features_darts, ts_to_list
from app.utils.exception_handling import (
    BadRequestException,
    MethodNotAllowedException,
    NotImplementedException,
    SaveResourceException,
)
from app.models.algorithms import get_model, get_all_algorithms, VALID_ALGORITHMS
from app.utils.constants import DEFAULT_MEASUREMENT_UNIT
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
)

# import openapi_client
# from openapi_client.api import entities_api
# from openapi_client.model.create_entity_request import CreateEntityRequest
# configuration = openapi_client.Configuration(
#    host="http://{0}:{1}".format(os.getenv("ORION_URL"), os.getenv("ORION_PORT"))
# )


def get_algorithms_endpoint(include_parameters: bool = False, meter_id: str = None):
    """
    Returns a list of all algorithms that are available.
    :param include_parameters: Whether to include the parameter specs of the algorithms.
    :param meter_id: The id of the meter. If specified, only algorithms for which the meter 
                     has a trained model are returned.
    :return: A list of algorithms.
    """
    algorithms = get_all_algorithms(include_parameters)

    if meter_id is not None:
        data_controller.raise_if_meter_not_exists(meter_id)
        models = data_controller.get_models(meter_id)
        algorithms_to_keep = [m["algorithm"].lower() for m in models]
        algorithms = [a for a in algorithms if a["name"].lower() in algorithms_to_keep]

    return algorithms


def get_models_endpoint(meter_id: str = None):
    """
    Returns the meta data of all existing models for the given meter.
    If meter_id is not specified, all models are returned.
    """
    if meter_id is not None:
        data_controller.raise_if_meter_not_exists(meter_id)
    models = data_controller.get_models(meter_id)
    for m in models:
        del m["_id"]
        del m["fpath"]
    return models


def delete_model_endpoint(
    meter_id: str = None, algorithm: str = None, model_id: str = None,
):
    """
    Deletes the meta data entry and the binary of the specified model
    based on the meter_id and algorithm. Uses model_id instead if given.
    """
    model_meta = data_controller.delete_model_meta(meter_id, algorithm, model_id)
    data_controller.delete_model_binary(model_meta)


def train_model_endpoint(meter_id: str, algorithm: str, hyper_opt: bool):
    """
    PUT endpoint for training a model for the given meter and algorithm.
    :param meter_id: The id of the meter.
    :param algorithm: The algorithm to use for training.
    :param hyper_opt: Whether to use hyperparameter optimization.
    """
    if data_controller.is_virtual(meter_id):
        data_controller.raise_if_orphan(meter_id)

    model = get_model(meter_id, algorithm)
    model.fit(train_size=0.8, hyper_opt=hyper_opt)

    results = model.get_evaluation_results()
    model_id = data_controller.save_model(model, meter_id, algorithm, results)

    results["modelId"] = model_id
    results["refMeter"] = meter_id
    return results


def get_forecast_endpoint(
    meter_id: str, algorithm: str, date: str = None,
):
    """
    Generates a 24-hours forecast for the given meter.
    :param meter_id: The id of the (virtual or physical) meter to create a forecast for.
    :param algorithm: The algorithm to use for the forecast. Uses the algorithm that is set as
                      default for the given meter if none is specified.
    :param date: The day for which to create the forecast in ISO8601 UTC format.
                 If None, the following day w.r.t. day of the request will be chosen.
    """
    data_controller.raise_if_meter_not_exists(meter_id)

    if algorithm is None:
        algorithm = data_controller.get_default_algorithm(meter_id)
    if algorithm.lower() not in VALID_ALGORITHMS:
        raise BadRequestException(f'Invalid algorithm: "{algorithm}".')

    data_controller.raise_if_model_not_exists(meter_id, algorithm)

    model_meta = data_controller.get_model_meta(meter_id, algorithm)
    if not model_meta["isModelValid"]:
        raise MethodNotAllowedException(
            f"Existing model for meter {meter_id} and algorithm {algorithm} is not valid anymore. "
            + "This can happen after a submeter has been deleted. Please re-train the model."
        )

    model = data_controller.load_model_binary(meter_id, algorithm)
    forecast_results = model.predict(forecast_date=date)

    results = []
    values = forecast_results["forecastValues"]
    dates = forecast_results["forecastTimestamps"]
    for v, d in zip(values, dates):
        # TODO: Include covariates
        results.append(
            {
                "id": f"{model_meta['id']}:WaterForecast:{d}",
                "numValue": v,
                "datePredicted": d,
                "refDevice": meter_id,
                "type": "WaterForecast",
                "unit": DEFAULT_MEASUREMENT_UNIT,
            }
        )
    return results
