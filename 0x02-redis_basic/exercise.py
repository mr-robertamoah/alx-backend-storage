#!/usr/bin/env python3
"""
contains a Cache class
"""


from typing import Union
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
        eturn key
