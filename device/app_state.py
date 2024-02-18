import asyncio

import async_queue


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class State(Singleton):
    def __init__(self):
        self.sensor_sub_update_rate: int = 1
        self.sensor_sub_enabled = asyncio.Event()
        self.response_queue = async_queue.Queue()


app_state = State()
