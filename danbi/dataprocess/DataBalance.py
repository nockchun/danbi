import numpy as np
import random
import danbi as bi


class UniqueRateChecker:
    def __init__(self):
        self._df_map = None
        self._map = None
    
    def store(self) -> dict:
        return {
            "df_map": self._df_map,
        }
    
    def storeFile(self, file: str) -> dict:
        bi.storePickle(self.store(), file)

    def getBalanceMap(self):
        return self._df_map
    
    def restore(self, states):
        self._df_map = states["df_map"]
        self._map = self._df_map.iloc[:, :-2].values
    
    def restoreFile(self, file: str):
        stored_dict = bi.restorePickle(file)
        self.restore(stored_dict)

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


class LabelRateAugmenter(UniqueRateChecker):
    def __init__(self, augmentation_rate=1):
        self._aug_rate = augmentation_rate
        self._origins = []

    def store(self) -> dict:
        data = super().store()
        data["aug_rate"] = self._aug_rate
        
        return data

    def restore(self, states):
        data = super().restore(states)
        self._aug_rate = states["aug_rate"]

    def add(self, data, label):
        rate = self.checkRate(label) - 1
        rate = int(rate * self._aug_rate)
        
        if rate > 0:
            self._origins.append([data, label, rate - 1, rate - 1])

    def getAddedDatas(self):
        return self._origins

    def _get_random(self):
        index = random.randint(0, len(self._origins) - 1)
        item = self._origins[index]
        
        if item[-1] == 1:
            del self._origins[index]
        else:
            self._origins[index][-1] -= 1
        
        return item[0], item[1]

    def __iter__(self):
        return self

    def __next__(self):
        if len(self._origins) == 0:
            raise StopIteration
        else:
            return self._get_random()
