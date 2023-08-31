import tensorflow as tf
from tensorflow.io import TFRecordWriter
import numpy as np
from typing import List, Tuple, Dict, Callable


def getWriter(file_path: str, is_zip: bool = True) -> tf.io.TFRecordWriter:
    if bool:
        return tf.io.TFRecordWriter(file_path, tf.io.TFRecordOptions(compression_type="GZIP"))
    else:
        return tf.io.TFRecordWriter(file_path)

def storeTFRecord(file_path: str, datas: Dict[str, np.array], is_zip: bool = True):
    writer = getWriter(file_path, is_zip)
    
    for data in zip(*datas.values()):
        feature = {}
        for idx, name in enumerate(datas.keys()):
            feature[name] = tf.train.Feature(bytes_list=tf.train.BytesList(value=[data[idx].tobytes()]))
        example = tf.train.Example(features=tf.train.Features(feature=feature))
        writer.write(example.SerializeToString())

def getTFRecordDecoder(datas: Dict[str, tf.DType], shape_in: Dict[str, Tuple[int]], shape_out: Dict[str, Tuple[int]]) -> Callable:
    def tfrecordParseAndDecode(dataset):
        feature_shape = {}
        for name in datas.keys():
            feature_shape[name] = tf.io.FixedLenFeature([], tf.string)
        features = tf.io.parse_single_example(dataset, features=feature_shape)
        
        ins = {}
        for name, shape in shape_in.items():
            raw = tf.io.decode_raw(features[name], datas[name])
            ins[name] = tf.reshape(raw, shape=shape)
        outs = {}
        for name, shape in shape_out.items():
            raw = tf.io.decode_raw(features[name], datas[name])
            outs[name] = tf.reshape(raw, shape=shape)

        return ins, outs
    return tfrecordParseAndDecode

def restoreTFRecord(files: List[str], decoder: Callable, is_zip: bool = True) -> tf.data.TFRecordDataset:
    if is_zip:
        rds = tf.data.TFRecordDataset(files, "GZIP")
    else:
        rds = tf.data.TFRecordDataset(files)
    
    rds = rds.map(decoder)
    
    return rds
