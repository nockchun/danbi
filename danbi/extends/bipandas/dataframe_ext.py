import pandas as pd
import numpy as np
from typing import List, Tuple, Callable

@pd.api.extensions.register_dataframe_accessor("bi")
class DanbiExtendFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._len = len(pandas_obj)

    def rollapply(self, win: int, func: Callable, test: int = 0, future: bool = False):
        results = []
        if test > 0:
            for idx, df in enumerate(self._obj.rolling(win)):
                if len(df) < win:
                    continue
                if idx + 1 >= win + test:
                    break
                results.append(func(df))

            return results
        else:
            for df in self._obj.rolling(win):
                if len(df) < win:
                    continue
                results.append(func(df))
            
            if len(results) > 0:
                if isinstance(results[0], tuple):
                    nan = [[np.nan for _ in range(len(results[0]))] for _ in range(win-1)]
                else:
                    nan = [np.nan for _ in range(win-1)]
            
            return results + nan if future else nan + results
    
    def split(self, rate: float, suffle=False, seed=None) -> Tuple[pd.DataFrame, pd.DataFrame]: 
        if suffle:
            self._obj = self._obj.sample(frac=1, random_state=seed).reset_index(drop=True)
        idx = int(len(self._obj) * rate)
        return self._obj[:idx].reset_index(drop=True), self._obj[idx:].reset_index(drop=True)
    
    def getTimeseries(self, win: int, col_data: List[str], col_label: List[str], next_label: List[int] = [1]) -> Tuple[np.array, np.array]:
        win_data = []
        win_label = []
        next_label = np.array(next_label)
        
        datas = self._obj[col_data].values
        labels = self._obj[col_label].values
        for idx in range(win, len(datas) - next_label[-1] + 1):
            win_data.append(datas[idx-win:idx])
            win_label.append(labels[next_label + idx - 1].flatten())
        
        return np.array(win_data), np.array(win_label)