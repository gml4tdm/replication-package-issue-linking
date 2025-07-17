import contextlib
import logging
import time

BASE_NAME = 'Runner'


def setup_logging():
    formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]: %(message)s', style='%')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler('logs.txt', mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(BASE_NAME)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(BASE_NAME + '.' + name)


@contextlib.contextmanager
def measure_time(logger: logging.Logger, message, level=logging.INFO):
    logger.log(level, message)
    start = time.time()
    yield
    end = time.time()
    logger.log(level, f'{message} took {end - start:.2f} seconds')
