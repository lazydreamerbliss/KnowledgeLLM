import os

REDIS_HOST: str = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PWD: str = os.environ.get('REDIS_PWD', 'test123')
REDIS_PORT: int = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DATA_DIR: str = os.environ.get('REDIS_DATA_DIR', '/data')
