from typing import List, Union
import pandas as pd, numpy as np

import tensorflow as tf

def convDfTypes(df: pd.DataFrame, src: List[str], dst: str, like: bool = False) -> pd.DataFrame:
    """Change all columns of a specific type to the target type.

    Args:
        df (pd.DataFrame): target pandas dataframe.
        src (List[str]): list of types to change.
        dst (str): target type.
        like (bool, optional): using numpy like type notation. Defaults to False.
            > example: i : int, int16, int32 ...
                       f : float, float16, float32 ...

    Returns:
        pd.DataFrame: pandas dataframe that has been changed.
    """
    return df.astype({
        col: dst
        for col in df.columns[
            [dtype.kind in src for dtype in df.dtypes]
            if like else
            df.dtypes.isin([np.dtype(ty) for ty in src])
        ]
    })

def convDfsToContinuousDfs(dfs: List[pd.DataFrame], time_column: str, freq: str) -> List[pd.DataFrame]:
    """Ensure time continuity.

    Args:
        dfs (List[pd.DataFrame]): all target pandas dataframe list.
        time_column (str): time column to check for time continuity.
        freq (str): time continuity unit. it means a frequency that can be expressed as a pandas timedelta.

    Returns:
        List[pd.DataFrame]: pandas dataframes to ensure time continuity.
    """
    df = pd.concat(dfs).drop_duplicates().sort_values(by=time_column).reset_index(drop=True)
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
