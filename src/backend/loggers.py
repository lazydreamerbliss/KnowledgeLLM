from functools import wraps
from logging import Logger
from time import time
from typing import Any

from utils.logging import CategoryLogger, DefaultLogger

# Default logger
logger: Logger = DefaultLogger.get_logger('default')

# Logger for gRPC calls
rpc_logger: Logger = CategoryLogger.get_logger('grpc', 'grpc')

# Loggers for library's internal operations
lib_logger: Logger = CategoryLogger.get_logger('lib', 'lib')
doc_lib_logger: Logger = CategoryLogger.get_logger('lib', 'doc_lib')
image_lib_logger: Logger = CategoryLogger.get_logger('lib', 'img_lib')

# Loggers for embedding process
doc_embedder_logger: Logger = CategoryLogger.get_logger('embedder', 'doc_embedder')
img_embedder_logger: Logger = CategoryLogger.get_logger('embedder', 'img_embedder')

# Loggers for DBs
db_logger: Logger = DefaultLogger.get_logger('db')
vector_db_logger: Logger = DefaultLogger.get_logger('vector_db')


def log_time_cost(start_log: str, end_log: str, LOGGER: Logger = logger):
    def wrapper(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            LOGGER.info(start_log)
            start: float = time()
            try:
                result: Any = func(*args, **kwargs)
                time_taken: float = time() - start
                LOGGER.info(f'{end_log}, cost: {time_taken:.2f}s')
                return result
            except Exception as e:
                time_taken: float = time() - start
                LOGGER.error(f'{end_log} with error, cost: {time_taken:.2f}s, error: {e}')
                raise e
        return wrapper_func
    return wrapper
