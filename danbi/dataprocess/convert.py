import pandas as pd
from typing import List

def convDfsToContinuousDfs(dfs: List[pd.DataFrame], time_column: str, freq: str, replace_method: str = "mean") -> List[pd.DataFrame]:
    '''
    example : res = convDfsToContinuousDfs([df1, df2], "Timestamp", "1d", "min")
    '''
    df = pd.concat(dfs).drop_duplicates().sort_values(by=time_column).reset_index(drop=True)    
    df.set_index(time_column, inplace=True)
    if replace_method == "mean":
        df = df.resample(freq).mean(numeric_only=True).dropna()
    elif replace_method == "median":
        df = df.resample(freq).median(numeric_only=True).dropna()
    elif replace_method == "min":
        df = df.resample(freq).min(numeric_only=True).dropna()
    elif replace_method == "max":
        df = df.resample(freq).max(numeric_only=True).dropna()
    else:
        raise Exception('Please enter one of four values: mean, median, min_max_mean.')
    df.reset_index(inplace=True)
    
    delta = pd.Timedelta(freq)
    offsets = df[[time_column]].diff()
    offsets.iloc[0, 0] = delta
    points = offsets[offsets[time_column] != delta].index
    offsets = offsets.drop(time_column, axis=1)
    
    point_start = 0
    df_results = []
    for point in points:
        df_results.append(offsets[point_start:point].merge(df, left_index=True, right_index=True))
        point_start = point
    df_results.append(offsets[point_start:].merge(df, left_index=True, right_index=True))

    return df_results
