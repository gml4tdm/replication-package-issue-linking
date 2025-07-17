import abc

import torch


class PeekableDataset(abc.ABC, torch.utils.data.Dataset[int]):

    @abc.abstractmethod
    def label_of(self, idx: int) -> bool:
        ...
