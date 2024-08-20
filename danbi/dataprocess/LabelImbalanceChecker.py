import numpy as np


class LabelImbalanceChecker:
    def __init__(self):
        self._df_map = None
        self._map = None

    def getBalanceMap(self):
        return self._df_map

    def fit(self, df, cols):
        df_map = df.groupby(cols).size().reset_index(name='counts')
        df_map["rate"] = (df_map["counts"].max() / (df_map["counts"])).astype(int)
        self._df_map = df_map.sort_values(by='counts', ascending=False).reset_index(drop=True)
        self._map = self._df_map.iloc[:, :-2].values

    def check(self, target):
        matches = np.ones(len(self._map), dtype=bool)
        for i in range(len(target)):
            matches &= (self._map[:, i] == target[i])
        indices = np.where(matches)[0]
        if len(indices) > 0:
            return self._df_map.iloc[indices[0]][["counts", "rate"]].astype(int).tolist()
        else:
            return [0, 0]

    def checkCounts(self, target):
        return self.check(target)[0]

    def checkRate(self, target):
        return self.check(target)[1]