import tensorflow as tf
from tensorflow.io import TFRecordWriter
import numpy as np
from typing import List
from functools import partial


def getWriter(file_path: str, is_zip: bool = True) -> tf.io.TFRecordWriter:
    if bool:
        return tf.io.TFRecordWriter(
            file_path,
            tf.io.TFRecordOptions(compression_type="GZIP")
        )
    else:
        return tf.io.TFRecordWriter(
            file_path,
        )

def write(writer: tf.io.TFRecordWriter, data: np.array, label: np.array):
    example = tf.train.Example(features=tf.train.Features(feature={
        "data": tf.train.Feature(bytes_list=tf.train.BytesList(value=[data.tobytes()])),
        "label": tf.train.Feature(bytes_list=tf.train.BytesList(value=[label.tobytes()])),
    }))
    writer.write(example.SerializeToString())

def storeTFRecord(file_path: str, datas: np.array, labels: np.array, is_zip: bool = True):
    writer = getWriter(file_path, is_zip)
    for data, label in zip(datas, labels):
        write(writer, data, label)


def tfrecordParseAndDecode(dataset, window_size: int, data_size: int, data_type: tf.dtypes.DType, label_size: int, label_type: tf.dtypes.DType):
    features = tf.io.parse_single_example(dataset, features={
        'data': tf.io.FixedLenFeature([], tf.string),
        'label': tf.io.FixedLenFeature([], tf.string)
    })
    data = tf.io.decode_raw(features["data"], data_type)
    data = tf.reshape(data, shape=(window_size, data_size))
    label = tf.io.decode_raw(features["label"], label_type)
    label = tf.reshape(label, shape=(label_size,))
    
    return data, label


def restoreTFRecord(files: List[str], window_size: int, data_size: int, data_type: tf.dtypes.DType, label_size: int, label_type: tf.dtypes.DType, is_zip: bool = True):
    if is_zip:
        rds = tf.data.TFRecordDataset(files, "GZIP")
    else:
        rds = tf.data.TFRecordDataset(files)
    pd_map = partial(tfrecordParseAndDecode, window_size = window_size, data_size = data_size, data_type = data_type, label_size = label_size, label_type = label_type)
    rds = rds.map(pd_map)
    
    return rds



