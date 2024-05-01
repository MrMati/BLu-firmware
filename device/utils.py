import asyncio


class EnumVal:
    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        return self._value == other

    def __repr__(self):
        return f'<EnumVal: {self._value}>'


class Enum:
    def __init__(self, **kwargs):
        self._members = {}
        for name, value in kwargs.items():
            enum_val = EnumVal(value)
            setattr(self, name, enum_val)
            self._members[name] = enum_val

    def __getitem__(self, key):
        return self._members[key]


class ThreadSafeEvent(asyncio.ThreadSafeFlag):
    def __init__(self, default_val):
        self.value = default_val

    def set(self, value):
        self.value = value
        super().set()

    async def wait(self):
        await super().wait()
        return self.value
