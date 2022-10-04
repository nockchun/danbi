from .trade import (
    ACT
)
from .TradeSingleEnv import TradeSingleEnv
from .simulation import simStockTrade
from gym.envs.registration import register

register(
    id='danbi-trade-v0',
    entry_point='danbi.gym:TradeSingleEnv',
    kwargs={
        'df': None,
        'window': 30,
        "future": 14
    }
)