#!/usr/bin/env python3
"""
contains a Cache class
"""


from typing import Union, Callable
import redis
import uuid


class Cache:
    """
    serves as a simple cache by interacting with redis
    """

    def __init__(self) -> None:
        """
        Initializes a Cache instance and readies redis.
        """
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Sets a key-value pair in a Redis and returns the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        """
        get value from the Redis storage
        """
        data = self._redis.get(key)
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        get key with string value from the Redis storage
        """
        return self.get(key, lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        get key with integer value from the Redis storage
        """
        return self.get(key, lambda x: int(x))
