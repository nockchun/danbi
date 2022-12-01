import pandas as pd
import numpy as np
from typing import Union, List, Callable

@pd.api.extensions.register_dataframe_accessor("bi")
class DanbiExtendFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._len = len(pandas_obj)

    def rollapply(self, window: int, func: Callable, test: int = 0, future: bool = False):
        results = []
        if test > 0:
            for idx, df in enumerate(self._obj.rolling(window)):
                if len(df) < window:
                    continue
                if idx + 1 >= window + test:
                    break
                results.append(func(df))

            return results
        else:
            for df in self._obj.rolling(window):
                if len(df) < window:
                    continue
                results.append(func(df))
            
            if len(results) > 0:
                if isinstance(results[0], tuple):
                    nan = [[np.nan for _ in range(len(results[0]))] for _ in range(window-1)]
                else:
                    nan = [np.nan for _ in range(window-1)]
            
            return results + nan if future else nan + results
    




