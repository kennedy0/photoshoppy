from typing import BinaryIO

import numpy as np

from photoshoppy.models.layer.channel_data import get_channel_data


class LayerChannel:
    def __init__(self, channel_id: int):
        self._id = channel_id
        self._channel_data = np.empty(0)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        channel_names = {
            0: "red",
            1: "green",
            2: "blue",
            -1: "transparency mask",
            -2: "user supplied layer mask",
            -3: "real user supplied layer mask",
        }
        return channel_names.get(self.id)

    @property
    def channel_data(self) -> np.array:
        return self._channel_data

    def read_channel_data(self, file: BinaryIO, width: int, height: int) -> np.array:
        self._channel_data = get_channel_data(file, width, height)
