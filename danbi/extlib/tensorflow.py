from typing import List, Union
import pandas as pd, numpy as np

import tensorflow as tf


def convDfToTimeseriesTfDataset(df: pd.DataFrame, x: List[str], y: Union[None, List[str]], window: int, batch: int, shuffle: int = 0, stride: int = 1, shift: int = 1, prefetch: int = 2):
    """Convert pandas dataframe to tensorflow dataset for timeseries data.

    Args:
        df (pd.DataFrame): Target pandas dataframe.
        x (List[str]): Feature list amoung columns of target df.
        y (Union[None, List[str]]): Label list amoung columns of target df. 
        window (int): size of time window. if the value is none, label data is not generated. it means you can use in case of data for prediction.
        batch (int): size of batch.
        shuffle (int, optional): size of shuffle. if the value  Defaults to 0.
        stride (int, optional): _description_. Defaults to 1.
        shift (int, optional): _description_. Defis 0, shuffling is not performed. aults to 1.
        prefetch (int, optional): size of prefetch. Defaults to 2.

    Returns:
        _type_: _description_
    """
    ds_x = tf.data.Dataset.from_tensor_slices(df[x].values)
    ds_x = ds_x.window(size=window, stride=stride, shift=shift, drop_remainder=True)
    ds_x = ds_x.flat_map(lambda w: w.batch(window))
    
    if y is not None:
        ds_y = tf.data.Dataset.from_tensor_slices(df[y].values)
        ds_y = ds_y.window(size=window, stride=stride, shift=shift, drop_remainder=True)
        ds_y = ds_y.flat_map(lambda w: w.batch(window))
        ds_y = ds_y.map(lambda w: w[-1])

        ds = tf.data.Dataset.zip((ds_x, ds_y))
    else:
        ds = ds_x
        
    if shuffle > 0:
        ds.shuffle(shuffle)
    ds = ds.batch(batch).cache().prefetch(prefetch)
    
    return ds


def convDfsToTimeseriesTfDataset(dfs: List[pd.DataFrame], x: List[str], y: Union[None, List[str]], window: int, batch: int, shuffle: int = 0, stride: int = 1, shift: int = 1, prefetch: int = 2):
    """Convert bunch of pandas dataframes to tensorflow dataset for timeseries data.

    Args:
        dfs (List[pd.DataFrame]): Target pandas dataframes list.
        x (List[str]): Feature list amoung columns of target df.
        y (Union[None, List[str]]): Label list amoung columns of target df. 
        window (int): size of time window. if the value is none, label data is not generated. it means you can use in case of data for prediction.
        batch (int): size of batch.
        shuffle (int, optional): size of shuffle. if the value  Defaults to 0.
        stride (int, optional): _description_. Defaults to 1.
        shift (int, optional): _description_. Defis 0, shuffling is not performed. aults to 1.
        prefetch (int, optional): size of prefetch. Defaults to 2.

    Returns:
        _type_: _description_
    """
    ds_result = convDfToTimeseriesTfDataset(dfs[0], x, y, window, batch, shuffle, stride, shift, prefetch)
    for df in dfs:
        ds = convDfToTimeseriesTfDataset(df, x, y, window, batch, shuffle, stride, shift, prefetch)
        ds_result = ds_result.concatenate(ds)

    return ds_result
