from typing import Union, List, Any
import numpy as np
from scipy.stats import rankdata

class GroupCorrelation:
    def __init__(self, rate_min: int = 0.75, rate_max: int = 1):
        self._col_target = None
        self._rate_min = rate_min
        self._rate_max = rate_max
        self._corr_map = None
        self._corr_pos = None
        self._corr_neg = None
        self._corr_set = None
        self._corr_set_pos = None
        self._corr_set_neg = None

    def _genColumnString(self, target, idx_range: str = "pos"):
        if isinstance(target, set):
            if idx_range == "pos":
                return [self._col_target[idx] for idx in self._corr_set_pos]
            elif idx_range == "neg":
                return [self._col_target[idx] for idx in self._corr_set_neg]
            else:
                raise Exception("The vale of idx_range can only be 'pos' or 'neg'.")
        if isinstance(target, dict):
            result = {}
            for key in target.keys():
                result[self._col_target[key]] = [self._col_target[value] for value in target[key]]
            return result
        result = []
        for item in target:
            result.append([self._col_target[v] for v in item])
        return result

    def getColumnTarget(self):
        return self._col_target

    def getRelationMap(self):
        return self._corr_map

    def getRelationPositive(self, as_col_idx: bool = False):
        return self._corr_pos if as_col_idx else self._genColumnString(self._corr_pos)

    def getRelationNegative(self, as_col_idx: bool = False):
        return self._corr_neg if as_col_idx else self._genColumnString(self._corr_neg, "neg")

    def getColumnPositive(self, as_col_idx: bool = False):
        return list(self._corr_set_pos) if as_col_idx else self._genColumnString(self._corr_set_pos)

    def getColumnNegative(self, as_col_idx: bool = False):
        return list(self._corr_set_neg) if as_col_idx else self._genColumnString(self._corr_set_neg, "neg")

    def fit(self, pandas_corr, cols: List = None, method: str = "spearman", corr_abs: bool = False):
        self._col_target = pandas_corr.select_dtypes("number").columns.tolist() if cols is None else cols
        self._corr_map = pandas_corr

        if corr_abs:
            self._corr_map = np.absolute(self._corr_map)
        pos_col, pos_row = np.where((self._corr_map >= self._rate_min) & (self._corr_map <= self._rate_max))
        neg_col, neg_row = np.where((self._corr_map <= -self._rate_min) & (self._corr_map >= -self._rate_max))

        self._corr_pos = {}
        self._corr_neg = {}
        self._corr_set_pos, self._corr_set_neg = set(), set()
        for position in zip(*np.where((self._corr_map >= self._rate_min) & (self._corr_map <= self._rate_max))):
            if position[0] < position[1]:
                if position[0] in self._corr_pos:
                    self._corr_pos[position[0]].append(position[1])
                    self._corr_set_pos.add(position[1])
                else:
                    self._corr_pos[position[0]] = [position[1]]
                    self._corr_set_pos.add(position[0])
                    self._corr_set_pos.add(position[1])

        for position in zip(*np.where((self._corr_map <= -self._rate_min) & (self._corr_map >= -self._rate_max))):
            if position[0] < position[1]:
                if position[0] in self._corr_neg:
                    self._corr_neg[position[0]].append(position[1])
                    self._corr_set_neg.add(position[1])
                else:
                    self._corr_neg[position[0]] = [position[1]]
                    self._corr_set_neg.add(position[0])
                    self._corr_set_neg.add(position[1])

    def _chkGroup(self, cluster):
        check_duplicate = set.intersection(*[self.__group_dic[c] for c in cluster])
        if not check_duplicate: # if it is empty
            self.__group.append(cluster)
            for c in cluster:
                self.__group_dic[c].add(self.__group_idx)
            self.__group_idx += 1

    def _genGroup(self, data: dict, corr_set: set):
        self.__group_idx, self.__group = 0, []
        self.__group_dic = {n: set() for n in corr_set}
        for corr_key, corr_value in data.items():
            full_conn = [corr_key]
            corr_value_size = len(corr_value)
            if corr_value_size == 1:
                cluster = full_conn + corr_value
                self._chkGroup(cluster)
            else:
                for idx in range(corr_value_size):
                    sub_key = corr_value[idx]
                    sub_value = set(corr_value[idx+1:])
                    intersection = sub_value & set(data[sub_key]) if sub_key in data else set()

                    if not intersection: # 연관관계가 없을 경우 : full_conn과 sub_key를 합쳐서 append
                        cluster = full_conn + [sub_key]
                        self._chkGroup(cluster)
                    elif sub_value == intersection: # sub_set이 완전 연관관계 일 경우: full_conn에 sub_key를 append.
                        full_conn.append(sub_key)
                        if idx == corr_value_size - 1: # 만약 마지막 subset_item이면 sub_value를 append
                            full_conn.append(sub_value.pop())
                    else: # sub_set이 부분 연관관계 일 경우.
                        for inter_item in intersection:
                            cluster = full_conn + [sub_key, inter_item]
                            self._chkGroup(cluster)
                self._chkGroup(full_conn)

        return self.__group

    def getGroupPositive(self, as_col_idx: bool = False):
        corr_set = self._genGroup(self._corr_pos, self._corr_set_pos)
        return corr_set if as_col_idx else self._genColumnString(corr_set)

    def getGroupNegative(self, as_col_idx: bool = False):
        corr_set = self._genGroup(self._corr_neg, self._corr_set_neg)
        return corr_set if as_col_idx else self._genColumnString(corr_set, "neg")
    
    def getHighestGroupOfCorr(self, corr_map, cols: List = None, cnt: int = 1, positive: bool = True, negative: bool = False, abs_min: int = 0.75, abs_max: int = 1, verbose: bool = False):
        self._col_target = corr_map.columns.tolist() if cols is None else cols
        highest_group = [[col] for col in self._col_target]
        for i, tag in enumerate(self._col_target):
            tmp_map = np.concatenate([corr_map[self._col_target[i]].iloc[:i].values, np.array([0]), corr_map[self._col_target[i]].iloc[i+1:].values])
            if positive and not negative:
                ranks = rankdata(-tmp_map)
            elif not positive and negative:
                ranks = rankdata(tmp_map)
            else:
                raise Exception("Only positive or negative must be true.")
            for c in range(1, cnt+1):
                max_idx = np.where(ranks==c)[0][0]
                max_col = corr_map.columns[max_idx]
                max_val = corr_map[tag][max_col]
                if (positive and max_val<0) or (negative and max_val>0):
                    print("break")
                    break
                if abs(max_val)>=abs_min and abs(max_val)<=abs_max:
                    highest_group[i].append(max_col)
                    if verbose:
                        print(f'{tag}, {max_col} : {max_val}')
        return highest_group
