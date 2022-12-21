import logging
from datetime import datetime, timezone

from utils import create_dir_if_not_exist, to_sp_timezone_without_delay, check_existing_dir

_logger = None
_existing_loggers = []


def set_logger(name='Monitoring-Cryptos'):
    global _existing_loggers
    found_log = check_if_log_exists(name)
    if found_log is not None:
        return found_log
    logger = logging.getLogger(name)
    _existing_loggers.append(logger)

    right_now = datetime.now(timezone.utc)
    #right_now = to_sp_timezone_without_delay(right_now)

    create_dir_if_not_exist('logs')
    global _logger
    if _logger is None:
        logging.basicConfig(filename=f'logs/log.{name}-{right_now.strftime("%Y-%m-%d-%I-%M-%S.%f")}.txt',
                            level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

    formatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] - %(message)s')
    logging.addLevelName(25, "NOTICE")

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger


def check_if_log_exists(name):
    global _existing_loggers
    found_log = list(filter(lambda l: l.name == name, _existing_loggers))
    return found_log[0] if found_log else None
