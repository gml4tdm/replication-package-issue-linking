import dataclasses

import torch

from ..utils.shared_args import MlpArgs
from .base import BaseSiameseTextModel


@dataclasses.dataclass
class SimpleMlpArgs:
    input_size: int
    mlp: MlpArgs


class SimpleSiameseMLPModel(BaseSiameseTextModel):

    def __init__(self, args: SimpleMlpArgs):
        super().__init__(args)
        self._mlp = args.mlp.build(args.input_size, 1)

    @staticmethod
    def get_args() -> type[SimpleMlpArgs]:
        return SimpleMlpArgs

    def forward(self, user, item):
        x = torch.cat([user, item], dim=1)
        return self._mlp(x).flatten()

    @staticmethod
    def feature_sources_user() -> dict[str, str]:
        return {'issue': 'issue-features'}

    @staticmethod
    def feature_sources_item() -> dict[str, str]:
        return {'source': 'source-code',
                'filename': 'filenames'}

    def transform_item(self, source, filename) -> torch.Tensor | dict:
        return torch.cat([source, filename])

    def transform_user(self, issue) -> torch.Tensor | dict:
        return issue
