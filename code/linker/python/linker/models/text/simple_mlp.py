import dataclasses

import torch

from ..utils.shared_args import MlpArgs
from .base import BaseTextModel


@dataclasses.dataclass
class SimpleMlpArgs:
    input_size: int
    mlp: MlpArgs


class SimpleMLPModel(BaseTextModel):

    def __init__(self, args: SimpleMlpArgs):
        super().__init__(args)
        self._mlp = args.mlp.build(args.input_size, 1)

    @staticmethod
    def get_args() -> type[SimpleMlpArgs]:
        return SimpleMlpArgs

    def forward(self, x):
        return self._mlp(x).flatten()

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {'issue': 'issue-features',
                'source': 'source-code',
                'filename': 'filenames'}

    def transform(self, issue, source, filename) -> torch.Tensor | dict:
        return torch.cat([issue, source, filename])
