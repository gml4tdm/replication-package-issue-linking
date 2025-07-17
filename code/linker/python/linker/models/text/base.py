import abc
import typing

import torch

T = typing.TypeVar('T')


class BaseTextModel(abc.ABC, torch.nn.Module):

    def __init__(self, args: T):
        super().__init__()
        self.args = args

    @staticmethod
    @abc.abstractmethod
    def feature_sources() -> dict[str, str]:
        pass

    @abc.abstractmethod
    def transform(self, **kwargs) -> torch.Tensor | dict:
        pass

    def collate_factory(self):
        return None

    @staticmethod
    @abc.abstractmethod
    def get_args() -> type[T]:
        pass