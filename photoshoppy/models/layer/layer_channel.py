from __future__ import annotations
from typing import BinaryIO

import numpy as np

import photoshoppy
from photoshoppy.models.layer.channel_data import get_channel_data

CHANNEL_RED = "red"
CHANNEL_GREEN = "green"
CHANNEL_BLUE = "blue"
CHANNEL_TRANSPARENCY_MASK = "transparency mask"
CHANNEL_USER_LAYER_MASK = "user-supplied layer mask"
CHANNEL_REAL_USER_LAYER_MASK = "real user-supplied layer mask"


class LayerChannel:
    def __init__(self, channel_id: int, layer: photoshoppy.models.layer.model.Layer):
        self._id = channel_id
        self._channel_data = np.empty(0)
        self._layer = layer

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        channel_names = {
            0: CHANNEL_RED,
            1: CHANNEL_GREEN,
            2: CHANNEL_BLUE,
            -1: CHANNEL_TRANSPARENCY_MASK,
            -2: CHANNEL_USER_LAYER_MASK,
            -3: CHANNEL_REAL_USER_LAYER_MASK,
        }
        return channel_names.get(self.id)

    @property
    def channel_data(self) -> np.array:
        return self._channel_data

    @property
    def layer(self) -> photoshoppy.models.layer.model.Layer:
        return self._layer

    def read_channel_data(self, file: BinaryIO) -> np.array:
        if self.name in [CHANNEL_RED, CHANNEL_GREEN, CHANNEL_BLUE, CHANNEL_TRANSPARENCY_MASK]:
            self._channel_data = get_channel_data(file, self.layer.width, self.layer.height)
        elif self.name in [CHANNEL_USER_LAYER_MASK, CHANNEL_REAL_USER_LAYER_MASK]:
            self._channel_data = get_channel_data(file, self.layer.layer_mask.width, self.layer.layer_mask.height)
