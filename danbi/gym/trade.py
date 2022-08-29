from enum import Enum

class ExtendEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class ACT(ExtendEnum):
    BUY = 0
    HOLD = 1
    SELL = 2
