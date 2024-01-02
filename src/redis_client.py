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


class RedisClient:
    def __init__(self, host: str, port: int = 6379, password: str | None = None, decode_responses: bool = True):
        self.client: Redis = Redis(host=host, port=port, password=password, decode_responses=decode_responses)
        try:
            self.connected: bool = bool(self.client.ping())
        except:
            self.connected: bool = False

    def set(self, key: str, value: Any):
        self.client.set(key, value)

    def get(self, key: str) -> Any:
        return self.client.get(key)

    def delete(self, key: str):
        self.client.delete(key)

    def delete_by_prefix(self, prefix: str):
        for key in self.client.scan_iter(f'{prefix}*'):
            self.client.delete(key)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def json_set(self, name: str, obj: Any, path: str | None = None):
        if not path:
            path = '$'
        self.client.json().set(name, path, obj)

    def json_get(self, name: str) -> Any:
        return self.client.json().get(name)

    def json_delete(self, name: str, path: str | None = None) -> Any:
        if not path:
            path = '$'
        return self.client.json().delete(name, path)

    def pipeline(self) -> Pipeline:
        if not self.connected:
            raise ConnectionError('Redis client is not connected')
        return self.client.pipeline()

    def batched_pipeline(self, batch_size: int = 1000) -> BatchedPipeline | None:
        if not self.connected:
            return None
        return BatchedPipeline(self, batch_size)

    def close(self) -> None:
        self.client.close()

    def snapshot(self) -> None:
        """Create a snapshot of the current database
        """
        self.client.bgrewriteaof()

    def save(self) -> None:
        """Dump whole database to disk
        """
        self.snapshot()
        self.client.save()
