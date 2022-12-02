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

    def colsUnique(self, *args):
        return np.unique(self._obj[list(args)].values, axis=0).tolist()
    
    def colsGroupValue(self, group: str, columns: List[str], value: str, ascending: bool = True):
        uniques = self.colsUnique(*columns)
        base = pd.DataFrame(self._obj[group].unique(), columns=[group]).sort_values(by=group, ascending=ascending).reset_index(drop=True)
        
        for unique in uniques:
            base = pd.merge(base, self._obj[np.all(self._obj[columns].values == unique, axis=1)][[group, value]], left_on=group, right_on=group, how="left")
            base.rename(columns = {value: "_".join([str(x) for x in unique])}, inplace=True)
        
        return base
