from datetime import datetime
from typing import List, Union, Dict


class WeatherAgent:
    def get_available_features(
        self,
        meter_ids: Union[str, List[str]] = None,
        coords: Union[Dict[str, float], List[Dict[str, float]]] = None,
    ):
        """
        Returns a list of available feature names. The features may depend on the meter_ids or coordinates data is requested for,
        and either represent aggregations of weather feature of all meters or the raw weather features of each meter.
        Example 1 return value: ["temperature (°C)", "precipitation (mm)", "precipitation (yes/no)"]
        Example 2 return value: ["temperature (°C) - meter_1", "temperature (°C) - meter_2", "precipitation (mm) - meter_1", ...]
        :param meter_ids: String or list of meter ids.
        :param coords: Dict or list of dicts of the form {"lat": lat, "lon": lon}
        :return: List of string feature names.
        """
        raise NotImplementedError

    def get_historical_data(
        self,
        meter_ids: Union[str, List[str]] = None,
        coords: Union[Dict[str, float], List[Dict[str, float]]] = None,
        start_date: datetime = None,
    ):
        """
        Returns a DataFrame of historical weather data given either (a) meter_id(s) or lat/lon coordinates (or both).        
        :param meter_ids: String or list of meter ids.
        :param coords: Dict or list of dicts of the form {"lat": lat, "lon": lon}
        :param start_date: Optionally, the start date of the requested weather data (inclusive).
        :return: Pandas DataFrame with hourly datetime index where each column is named after a feature from get_available_features().
        """
        raise NotImplementedError

    def get_future_data(
        self,
        end_date: datetime,
        meter_ids: Union[str, List[str]] = None,
        coords: Union[Dict[str, float], List[Dict[str, float]]] = None,
    ):
        """
        Returns a DataFrame of hourly future weather data starting from the next full hour
        given either (a) meter_id(s) or lat/lon coordinates (or both). Columns must match
        the names returned by get_historical_data().
        :param end_date: The end date of the requested weather data (inclusive).
        :param meter_ids: String or list of meter ids.
        :param coords: Dict or list of dicts of the form {"lat": lat, "lon": lon}
        :return: Pandas DataFrame with hourly datetime index where each column is named after a feature from get_available_features().
        """
        raise NotImplementedError
