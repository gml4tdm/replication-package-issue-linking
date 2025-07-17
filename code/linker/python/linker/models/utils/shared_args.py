import dataclasses
import typing

import torch
from .text_cnn_head import TextCNNHead


@dataclasses.dataclass
class MlpArgs:
    layers: list[int]
    activation: str
    use_normalisation: bool = False
    normalisation_loc: typing.Literal['before', 'after'] = 'after'
    dropout: float | None = None
    input_dropout: float | None = None

    def build(self, input_size: int, output_size: int):
        layers = []
        layer_sizes = self.layers.copy()
        layer_sizes.insert(0, input_size)
        if self.input_dropout is not None:
            layers.append(torch.nn.Dropout(self.input_dropout))
        for i, layer_size in enumerate(layer_sizes[:-1]):
            in_size = layer_sizes[i]
            out_size = layer_sizes[i + 1]
            layers.append(torch.nn.Linear(in_size, out_size))
            if self.use_normalisation and self.normalisation_loc == 'before':
                layers.append(torch.nn.BatchNorm1d(out_size))
            layers.append(getattr(torch.nn, self.activation)())
            if self.use_normalisation and self.normalisation_loc == 'after':
                layers.append(torch.nn.BatchNorm1d(out_size))
            if self.dropout is not None:
                layers.append(torch.nn.Dropout(self.dropout))
        layers.append(torch.nn.Linear(layer_sizes[-1], output_size))
        return torch.nn.Sequential(*layers)


@dataclasses.dataclass
class TextCNNArgs:
    kernels: list[int]
    n_kernels: int = 1
    normalisation: typing.Literal['none', 'before', 'after'] = 'none'
    dropout: float | None = None
    dense_layer_size: int | None = None

    def build(self, embedding_size: int):
        return TextCNNHead(
            embedding_size=embedding_size,
            kernels=tuple(self.kernels),
            n_kernels=self.n_kernels,
            dense_layer_size=self.dense_layer_size,
            normalisation=self.normalisation,
            dropout=self.dropout
        )
