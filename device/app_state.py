import asyncio
from collections import deque
import async_queue


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)  # , *args, **kwargs)
        return cls._instance


# many defaults set here should be retrieved from persistent storage
class State(Singleton):
    def __init__(self):
        self.response_queue = async_queue.Queue()

        # sensor
        self.scaling_factor = 1.0
        self.zero_point = 0
        self._avg_window_size = 1
        self.sensor_samples = deque((), self._avg_window_size)

        # subscription
        self.sensor_sub_update_rate: int = 1
        self.sensor_sub_enabled = asyncio.Event()

    def set_avg_window_size(self, size: int):
        self._avg_window_size = size
        self.sensor_samples = deque((), size)


app_state = State()
