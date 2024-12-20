import time
from logging import Logger, getLogger

from request_id_helper import init_logger

from src.conf import LOG_CONFIG


def create_logger(name: str) -> Logger:
    init_logger(LOG_CONFIG)
    return getLogger(name)


class TimeLogger:
    def __init__(self, start_message: str):
        self._start_message = start_message
        self.logger = getLogger("")

    def __enter__(self):
        self._t = time.perf_counter()

        self.logger.info(f"{self._start_message}")
        return self

    def __exit__(self, type, value, traceback):
        delta = time.perf_counter() - self._t
        self.logger.info(f"Processing time: {delta:.6f} sec")
