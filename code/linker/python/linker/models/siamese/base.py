import abc
import typing

import torch

T = typing.TypeVar('T')


class BaseSiameseTextModel(abc.ABC, torch.nn.Module):

    def __init__(self, args: T):
        super().__init__()
        self.args = args

    @staticmethod
    @abc.abstractmethod
    def feature_sources_user() -> dict[str, str]:
        pass

    @staticmethod
    @abc.abstractmethod
    def feature_sources_item() -> dict[str, str]:
        pass

    @abc.abstractmethod
    def transform_user(self, **kwargs) -> torch.Tensor | dict:
        pass

    @abc.abstractmethod
    def transform_item(self, **kwargs) -> torch.Tensor | dict:
        pass

    def item_collate_factory(self):
        return None

    @staticmethod
    @abc.abstractmethod
    def get_args() -> type[T]:
        pass

