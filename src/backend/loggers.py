from logging import Logger

from utils.logging import CategoryLogger, DefaultLogger

# Default logger
logger: Logger = DefaultLogger.get_logger('default')

# Logger for gRPC calls
RPC_LOGGER: Logger = CategoryLogger.get_logger('grpc')

# Loggers for library's internal operations
doc_lib_logger: Logger = CategoryLogger.get_logger('doc_lib')
image_lib_logger: Logger = CategoryLogger.get_logger('img_lib')

# Loggers for embedding process
doc_embedder_logger: Logger = CategoryLogger.get_logger('doc_embedder')
img_embedder_logger: Logger = CategoryLogger.get_logger('img_embedder')

# Loggers for DBs
db_logger: Logger = CategoryLogger.get_logger('db')
vector_db_logger: Logger = CategoryLogger.get_logger('vector_db')
