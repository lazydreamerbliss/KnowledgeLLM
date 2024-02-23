from logging import Logger

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
