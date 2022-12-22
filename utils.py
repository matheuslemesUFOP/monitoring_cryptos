import json
import os
from datetime import datetime

import pytz


def create_dir_if_not_exist(file_path: str) -> bool:
    if not check_existing_dir(file_path):
        os.makedirs(file_path)
        return True
    return False


def check_existing_dir(file_path: str) -> bool:
    return bool(os.path.exists(file_path))


def to_sp_timezone_without_delay(time) -> datetime:
    """set datetime to timezone UTC-3 SaoPaulo, without add -3 (delay) to time"""
    local_tz = pytz.timezone('America/Sao_Paulo')
    return local_tz.localize(time)


def get_sma(prices, rate):
    return prices.rolling(rate).mean()


def get_bollinger_bands(prices, rate=5):
    sma = get_sma(prices, rate)
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2  # Calculate top band
    bollinger_down = sma - std * 2  # Calculate bottom band
    return bollinger_up, bollinger_down


def read_json_file_as_dict(json_name: str):
    j = open(json_name)
    return json.load(j)
