import collections
from math import modf
from typing import Deque, Generic, List, TypeVar

"""Misc helper functions"""


def number_to_string_with_stepsize(value: float, decimals: int, stepsize: float):

    negative = value < 0

    steps = round(value / stepsize)
    stepped_value = steps * stepsize
    after_the_point, before_the_point = modf(stepped_value)

    before_the_point = abs(before_the_point)
    after_the_point = int(abs(after_the_point * (10**decimals)))

    output = "-" if negative and (before_the_point > 0 or after_the_point > 0) else ""
    output += str(int(before_the_point))
    if decimals > 0:
        output += f".{str(after_the_point).rjust(decimals, '0')}"

    return output


# From: https://stackoverflow.com/a/3862957/4124648
def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


T = TypeVar("T")


class RingBuffer(Generic[T]):
    """Simple ringbuffer that hold size amount of items, adding more will discard oldest items"""

    def __init__(self, size):
        self._buffer: Deque = collections.deque(maxlen=size)

    def add(self, item: T):
        self._buffer.append(item)

    def get_buffer(self) -> List[T]:
        return list(self._buffer)
