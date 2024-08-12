import logging
from functools import lru_cache

logging.basicConfig(level=logging.INFO)

@lru_cache(maxsize=128)
def cache_result(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper

def log_error(error):
    logging.error(error)