import tensorflow as tf
from tensorflow.keras import layers, saving


@saving.register_keras_serializable(package="danbi.bitensorflow.layers", name="FeatureMasking")
class FeatureMasking(layers.Layer):
    """ A custom Keras layer for feature masking during training.
    Args:
        indices (list or None): A list of indices representing the features to be masked.
            If None or an empty list ([]), no masking is applied, and all features are used.
        retain (bool): If True, the features specified by `indices` are retained and the rest are masked off.
            If False, the specified features are masked off, and the rest are retained.
        axis (int): The axis along which the masking should be applied. Default is the last axis (-1).
        **kwargs: Additional keyword arguments to be passed to the base Layer class.
    Example:
>>> inputs = tf.keras.Input(shape=(10,))
>>> x = FeatureMasking(indices=[0, 2, 4], retain=True)(inputs)
>>> x = tf.keras.layers.Dense(10, activation='relu')(x)
>>> outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
>>> model = tf.keras.Model(inputs=inputs, outputs=outputs)
>>> model.compile(optimizer='adam', loss='binary_crossentropy')
    """
    def __init__(self, indices=None, retain=True, axis=-1, **kwargs):
        super(FeatureMasking, self).__init__(**kwargs)
        self._indices = indices
        self._retain = retain
        self._axis = axis
 
    def build(self, input_shape):
        # 입력 shape에 따라 마스크를 생성합니다.
        if self._indices is None or len(self._indices) == 0:
            # 마스크 인덱스가 주어지지 않으면 모든 피쳐를 활성화합니다.
            self.mask = tf.ones(input_shape[self._axis], dtype=tf.bool)
        else:
            self.mask = tf.zeros(input_shape[self._axis], dtype=tf.bool)
            indices = tf.constant(self._indices, dtype=tf.int32)
            self.mask = tf.tensor_scatter_nd_update(self.mask, tf.expand_dims(indices, axis=1), tf.ones_like(indices, dtype=tf.bool))
            if not self._retain:
                self.mask = tf.logical_not(self.mask)
 
    def call(self, inputs, training=None):
        if training:
            # 학습 중에는 마스크를 적용합니다.
            mask = tf.broadcast_to(self.mask, tf.shape(inputs))
            return tf.where(mask, inputs, tf.zeros_like(inputs))
        else:
            # 예측 시에는 모든 피쳐를 사용합니다.
            return inputs
 
    def get_config(self):
        config = super(FeatureMasking, self).get_config()
        config.update({
            "indices": self._indices,
            "retain": self._retain,
            "axis": self._axis,
        })
        return config