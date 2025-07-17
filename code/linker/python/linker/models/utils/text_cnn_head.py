import typing

import torch

from .dummy import DummyLayer


class TextCNNHead(torch.nn.Module):

    def __init__(self,
                 embedding_size: int,
                 kernels: tuple[int, ...],
                 n_kernels: int = 1,
                 dense_layer_size: int | None = None,
                 normalisation: typing.Literal['none', 'before', 'after'] = 'none',
                 dropout: float | None = None):
        super().__init__()
        if len(kernels) == 0:
            raise ValueError('Must have at least one kernel')
        self.convolutions = torch.nn.ModuleList([
            torch.nn.Sequential(
                *self._build_cnn_module(k, embedding_size, n_kernels),
            )
            for k in kernels
        ])
        if len(kernels) == 1:
            self.concat = DummyLayer()
        else:
            self.concat = Concatenation(dim=-1)
        if dense_layer_size is not None:
            layers = []
            if dropout is not None:
                layers.append(torch.nn.Dropout(dropout))
            layers.append(
                torch.nn.Linear(len(kernels) * n_kernels, dense_layer_size)
            )
            layers.append(torch.nn.ReLU())
            self.dense = torch.nn.Sequential(*layers)
            self.output_size = dense_layer_size
        else:
            if dropout is not None:
                raise ValueError('Cannot use dropout without dense layer')
            self.dense = DummyLayer()
            self.output_size = len(kernels) * n_kernels

    @staticmethod
    def _build_cnn_module(k: int,
                          embedding_size: int,
                          n_kernels: int,
                          normalisation: typing.Literal['none', 'before', 'after'] = 'none',):
        layers = []
        layers.append(
            torch.nn.Conv2d(
                in_channels=1,
                out_channels=n_kernels,
                kernel_size=(k, embedding_size)
            )
        )
        if normalisation == 'before':
            layers.append(torch.nn.BatchNorm2d(n_kernels))
        layers.append(torch.nn.ReLU())
        if normalisation == 'after':
            layers.append(torch.nn.BatchNorm2d(n_kernels))
        layers.append(torch.nn.Flatten(start_dim=2, end_dim=3))  # Convolution removes embedding dimension
        layers.append(GlobalMaxPool1D())
        layers.append(torch.nn.Flatten(start_dim=1, end_dim=2))  # Global max pooling removes convolution dimension
        return layers

    def forward(self, x):
        xs = [conv(x) for conv in self.convolutions]
        x = self.concat(*xs)
        return self.dense(x)


class GlobalMaxPool1D(torch.nn.Module):

    def forward(self, x):
        return torch.nn.functional.max_pool1d(
            x, kernel_size=x.shape[-1]
        )


class Concatenation(torch.nn.Module):

    def __init__(self, dim=-1):
        super().__init__()
        self.dim = dim

    def forward(self, *xs):
        return torch.cat(xs, dim=self.dim)

