from functools import wraps
from typing import Any

from redis import Redis
from redis.client import Pipeline


class BatchedPipeline:
    """A redis pipeline that executes commands automatically in batches of a given size as a context manager
    """

    def __init__(self, redis_client: 'RedisClient', batch_size: int = 200):
        self.batch_size: int = batch_size
        self.pipeline: Pipeline = redis_client.pipeline()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if len(self.pipeline) > 0:
            self.pipeline.execute()
        self.pipeline.close()

    def set(self, key: str, value: Any):
        self.pipeline.set(key, value)
        if len(self.pipeline) >= self.batch_size:
            self.pipeline.execute()

    def get(self, key: str) -> Any:
        return self.pipeline.get(key)

    def delete(self, key: str) -> Any:
        self.pipeline.delete(key)
        if len(self.pipeline) >= self.batch_size:
            self.pipeline.execute()

    def exists(self, key: str) -> bool:
        return bool(self.pipeline.exists(key))

    def json_set(self, name: str, obj: Any, path: str | None = None):
        if not path:
            path = '$'
        self.pipeline.json().set(name, path, obj)
        if len(self.pipeline) >= self.batch_size:
            self.pipeline.execute()

    def json_get(self, name: str) -> Any:
        return self.pipeline.json().get(name)

    def json_delete(self, name: str, path: str | None = None) -> Any:
        if not path:
            path = '$'
        self.pipeline.json().delete(name, path)
        if len(self.pipeline) >= self.batch_size:
            self.pipeline.execute()

    def execute(self) -> None:
        self.pipeline.execute()

    def save(self) -> None:
        self.pipeline.bgrewriteaof()


def ensure_redis(func):
    """Decorator to ensure the Redis client is connected
    """
    @wraps(func)
    def wrapper(self: RedisClient, *args, **kwargs):
        if not self.__connected:
            raise ValueError("Redis is not connected")
        return func(self, *args, **kwargs)
    return wrapper


class RedisClient:
    def __init__(self, host: str, port: int = 6379, password: str | None = None, decode_responses: bool = True):
        self.__client: Redis = Redis(host=host, port=port, password=password, decode_responses=decode_responses)
        try:
            self.__connected: bool = bool(self.__client.ping())
        except:
            self.__connected: bool = False

    @ensure_redis
    def client(self) -> Redis:
        return self.__client

    @ensure_redis
    def set(self, key: str, value: Any):
        self.__client.set(key, value)

    @ensure_redis
    def get(self, key: str) -> Any:
        return self.__client.get(key)

    @ensure_redis
    def delete(self, key: str):
        self.__client.delete(key)

    @ensure_redis
    def delete_by_prefix(self, prefix: str):
        for key in self.__client.scan_iter(f'{prefix}*'):
            self.__client.delete(key)

    @ensure_redis
    def exists(self, key: str) -> bool:
        return bool(self.__client.exists(key))

    @ensure_redis
    def json_set(self, name: str, obj: Any, path: str | None = None):
        if not path:
            path = '$'
        self.__client.json().set(name, path, obj)

    @ensure_redis
    def json_get(self, name: str) -> Any:
        return self.__client.json().get(name)

    @ensure_redis
    def json_delete(self, name: str, path: str | None = None) -> Any:
        if not path:
            path = '$'
        return self.__client.json().delete(name, path)

    @ensure_redis
    def pipeline(self) -> Pipeline:
        return self.__client.pipeline()

    @ensure_redis
    def batched_pipeline(self, batch_size: int = 1000) -> BatchedPipeline:
        return BatchedPipeline(self, batch_size)

    @ensure_redis
    def close(self) -> None:
        self.__client.close()

    @ensure_redis
    def snapshot(self) -> None:
        """Create a snapshot of the current database
        """
        self.__client.bgrewriteaof()

    @ensure_redis
    def save(self) -> None:
        """Dump whole database to disk
        """
        self.snapshot()
        self.__client.save()
