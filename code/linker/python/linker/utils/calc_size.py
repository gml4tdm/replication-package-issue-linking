import sys
from collections import deque
from collections.abc import Set
from numbers import Number
from typing import Mapping


# Taken from https://stackoverflow.com/a/30316760/5153960
ZERO_DEPTH_BASES = (str, bytes, Number, range, bytearray)



def calculate_object_size(o: object):
    _seen_ids = set()

    def inner(obj):
        obj_id = id(obj)
        if obj_id in _seen_ids:
            return 0
        _seen_ids.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, ZERO_DEPTH_BASES):
            pass  # bypass remaining control flow and return
        elif isinstance(obj, (tuple, list, Set, deque)):
            size += sum(inner(i) for i in obj)
        elif isinstance(obj, Mapping) or hasattr(obj, 'items'):
            size += sum(inner(k) + inner(v) for k, v in getattr(obj, 'items')())
        # Check for custom object instances - may subclass above too
        if hasattr(obj, '__dict__'):
            size += inner(vars(obj))
        if hasattr(obj, '__slots__'):  # can have __slots__ with __dict__
            raise ValueError(obj.__class__.__name__)
            size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
        return size

    return inner(o)
