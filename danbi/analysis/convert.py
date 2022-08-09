from typing import List
import pandas as pd, numpy as np

def convDfTypes(df: pd.DataFrame, src: List[str], dst: str) -> pd.DataFrame:
    """Change all columns of a specific type to the target type.

    Args:
        df (pd.DataFrame): target pandas dataframe.
        src (List[str]): list of types to change.
        dst (str): target type.

    Returns:
        pd.DataFrame: pandas dataframe that has been changed.
    """
    return df.astype({
        col: dst
        for col in df.dtypes[df.dtypes.isin([np.dtype(ty) for ty in src])].keys()
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
    df = pd.concat(dfs).drop_duplicates().reset_index(drop=True)
    delta = pd.Timedelta(freq)
    offsets = df[[time_column]].drop_duplicates().diff()
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
