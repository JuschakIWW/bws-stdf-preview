from ray import tune
from app.models.algorithms.darts_base import DartsForecaster
from darts.models import NBEATSModel
from app.utils.constants import N_EPOCHS_TORCH


class NBEATSForecaster(DartsForecaster):
    def __init__(self, meter_id: str, weather_agent: object = None):
        super().__init__(
            meter_id,
            NBEATSModel,
            name="NBEATS",
            description="NBEATS (Neural Basis Expansion Analysis for Time Series) is a deep neural network architecture designed for time series forecasting. Note that this algorithm does not support future weather predictions.",
            monitors_val=True,
            weather_agent=weather_agent,
            use_time_features=True,
            use_weather_features=False,
        )

    def get_hyperparam_search_space(self):
        # Note: If the algorithm allows hyperparameter search, it also needs to provide values for
        # self.min_t and self.grace_period
        # NOTE: loguniform helps to sample equally likely from different orders of magnitude
        return {
            "input_chunk_length": tune.choice([24, 2 * 24, 3 * 24, 7 * 24]),
            "num_blocks": tune.choice([1, 2, 3]),
            "num_layers": tune.choice([2, 4]),
            "layer_widths": tune.choice([256, 512, 1024, 2048]),
            "batch_size": tune.choice([16, 32, 64, 128]),
            # "lr"?
        }

    def get_static_params(self):
        # A note on covariate lags: We need to specify the lags of the covariates for Darts implementations. For example, depending on the context, a lag of k can mean that the covariate value at time t-k will be used to predict the target value at time t.
        # See also: https://unit8.com/resources/time-series-forecasting-using-past-and-future-external-data-with-darts/
        # A tuple (past=24, future=12) means that the 24 past and future 12 hours will be used for prediction
        return {
            "n_epochs": N_EPOCHS_TORCH,
            "output_chunk_length": 24,
        }

    def get_default_tunable_params(self):
        return {
            "input_chunk_length": 72,
            "num_blocks": 1,
            "num_layers": 4,
            "layer_widths": 512,
            "batch_size": 32,
        }

    def get_param_descriptions(self):
        return {
            "input_chunk_length": "Number of past hours to use for prediction. For example, if set to 48, the model will use the past 48 hours to predict the next 24 hours.",
            "num_blocks": "The number of blocks per stack.",
            "num_layers": "Number of fully connected layers with ReLu activation per block",
            "layer_widths": "Number of neurons of the fully connected layers with ReLu activation in the blocks.",
            "batch_size": "Number of samples to process per update step.",
        }
