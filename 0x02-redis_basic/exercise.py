#!/usr/bin/env python3
"""
contains a Cache class
"""


from typing import Any, Callable, Union
import redis
import uuid
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Tracks the number of calls made to the store method in a Cache class
    """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        calls the given method after incrementing its call counter
        """
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return invoker


def call_history(method: Callable) -> Callable:
    """
    Tracks the history of inputs and outputs of a method in a Cache class
    """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        returns the output of a method after storing its inputs and output.
        """

        input_key = "{}:inputs".format(method.__qualname__)
        output_key = "{}:outputs".format(method.__qualname__)

        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
            self._redis.rpush(output_key, output)

        return output

    return invoker


def replay(fn: Callable) -> None:
    """
    Displays the history of inputs and outputs
    used to call a Cache class method
    """
    if fn is None or not hasattr(fn, "__self__"):
        return

    redis_store = getattr(fn.__self__, "_redis", None)

    if not isinstance(redis_store, redis.Redis):
        return

    qualname = fn.__qualname__
    func_call_count = 0

    if redis_store.exists(qualname) != 0:
        func_call_count = int(redis_store.get(qualname))

    print("{} was called {} times:".format(qualname, func_call_count))

    input_key = "{}:inputs".format(qualname)
    output_key = "{}:outputs".format(qualname)
    func_inputs = redis_store.lrange(input_key, 0, -1)
    func_outputs = redis_store.lrange(output_key, 0, -1)

    for func_input, func_output in zip(func_inputs, func_outputs):
        print("{}(*{}) -> {}".format(
            qualname,
            func_input.decode("utf-8"),
            func_output,
        ))


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

    @call_history
    @count_calls
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
