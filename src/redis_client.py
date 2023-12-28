from typing import Any

from redis import Redis
from redis.client import Pipeline


class RedisClient:
    def __init__(self, host, port=6379, decode_responses=True):
        self.client: Redis = Redis(host, port, decode_responses)
        try:
            self.connected: bool = bool(self.client.ping())
        except:
            self.connected: bool = False

    def set(self, key: str, value: Any):
        self.client.set(key, value)

    def get(self, key: str) -> Any:
        return self.client.get(key)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def json_set(self, name: str, obj: Any, path: str | None = None):
        if not path:
            path = '$'
        self.client.json().set(name, path, obj)

    def json_get(self, name: str) -> Any:
        return self.client.json().get(name)

    def pipeline(self) -> Pipeline | None:
        if not self.connected:
            return None
        return self.client.pipeline()

    def close(self) -> None:
        self.client.close()
