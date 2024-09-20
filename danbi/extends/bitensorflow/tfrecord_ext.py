import tensorflow as tf
from tensorflow.io import TFRecordWriter
import numpy as np
from typing import List, Tuple, Dict, Callable


def getWriter(file_path: str, is_zip: bool = True) -> tf.io.TFRecordWriter:
    if bool:
        return tf.io.TFRecordWriter(file_path, tf.io.TFRecordOptions(compression_type="GZIP"))
    else:
        return tf.io.TFRecordWriter(file_path)

def storeTFRecord(writer: Callable, data: Dict[str, np.array], is_zip: bool = True):
    # for data in zip(*datas.values()):
    #     feature = {}
    #     for idx, name in enumerate(datas.keys()):
    #         feature[name] = tf.train.Feature(bytes_list=tf.train.BytesList(value=[data[idx].tobytes()]))
    #     example = tf.train.Example(features=tf.train.Features(feature=feature))
    #     writer.write(example.SerializeToString())

    feature = {}
    for idx, name in enumerate(data.keys()):
        feature[name] = tf.train.Feature(bytes_list=tf.train.BytesList(value=[data[name].tobytes()]))
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    writer.write(example.SerializeToString())

def getTFRecordDecoder(datas: Dict[str, tf.DType], shape_in: Dict[str, Tuple[int]], shape_out: Dict[str, Tuple[int]]) -> Callable:
    feature_shape = {}
    for name in datas.keys():
        feature_shape[name] = tf.io.FixedLenFeature([], tf.string)
        
    def tfrecordParseAndDecode(dataset):
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

def selectTFRecordIndexData(tfrecord, name, indices, axis=-1):
    """
    특정 키의 텐서에서 지정한 인덱스만 선택하여 새로운 데이터셋을 생성합니다.
    
    Args:
        tfrecord (tf.data.Dataset): 입력 데이터셋.
        name (str): 선택할 텐서가 저장된 딕셔너리 내의 키 이름.
        indices (list or tuple): 선택할 인덱스의 리스트.
        axis (int): 인덱스를 선택할 차원.
    
    Returns:
        tf.data.Dataset: 선택된 인덱스로 수정된 새로운 데이터셋.
    """
    # 인덱스를 텐서로 변환하여 map 함수 내에서 사용 가능하게 함
    indices_tensor = tf.constant(indices, dtype=tf.int32)
    
    def map_fn(*elements):
        """
        데이터셋의 각 요소에 적용될 매핑 함수.
        요소는 여러 개의 딕셔너리로 구성된 튜플일 수 있음.
        """
        new_elements = []
        for element in elements:
            new_dict = {}
            for k, v in element.items():
                if k == name:
                    # 지정한 키가 존재하면, 해당 텐서에서 지정한 축과 인덱스를 사용하여 선택
                    selected = tf.gather(v, indices_tensor, axis=axis)
                    new_dict[k] = selected
                else:
                    # 다른 키는 그대로 유지
                    new_dict[k] = v
            new_elements.append(new_dict)
        return tuple(new_elements)
    
    return tfrecord.map(map_fn)