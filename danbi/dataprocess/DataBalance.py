import numpy as np
import random
import danbi as bi
import threading


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
    def __init__(self, augmentation_rate: float = 1, noise_fraction: float = 0.1, noise_std: float = 0.1, noise_seed: int = None):
        self._aug_rate = augmentation_rate
        self._noise_fraction = noise_fraction
        self._noise_std = noise_std
        self._noise_rng = np.random.default_rng(noise_seed)
        self._noise_last_dim = None
        self._noise_size = None
        self._origins = []
        self._size = 0
        self._lock = threading.Lock()

    def store(self) -> dict:
        data = super().store()
        data["aug_rate"] = self._aug_rate
        data["noise_rate"] = self._noise_rate
        
        return data

    def restore(self, states):
        data = super().restore(states)
        self._aug_rate = states["aug_rate"]

    def add(self, data, label):
        if self._noise_last_dim is None:
            self._noise_last_dim = data.shape[-1]
            self._noise_size = int(self._noise_last_dim * self._noise_fraction)
        
        rate = self.checkRate(label) - 1
        rate = int(rate * self._aug_rate)
        self._size += rate
        
        if rate > 0:
            self._origins.append([data, label, rate])

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
        with self._lock:
            if len(self._origins) == 0:
                raise StopIteration
            else:
                data, label = self._get_random()
                if self._noise_fraction is not None:
                    it = np.nditer(data[..., 0], flags=['multi_index'])
                    while not it.finished:
                        idx = it.multi_index # 현재 위치에서 마지막 차원에 대한 슬라이스 가져오기
                        noise_indices = self._noise_rng.choice(self._noise_last_dim, size=self._noise_size, replace=False) # 마지막 차원에서 랜덤하게 50% 인덱스를 선택
                        data[idx + (noise_indices,)] += self._noise_rng.normal(0, self._noise_std, size=self._noise_size) # 선택된 인덱스에 대해 노이즈 추가
                        
                        it.iternext()
                return data, label
    
    def __len__(self):
        return self._size
