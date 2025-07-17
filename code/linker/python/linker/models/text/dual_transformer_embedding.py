import dataclasses

import torch


from ...utils import logs
from ..utils import device
from ..utils.shared_args import MlpArgs
from ..utils.transformer_models import resolve_and_wrap_transformer_model
from .base import BaseTextModel


@dataclasses.dataclass
class DualTransformerArgs:
    issue_model: str
    code_model: str
    mlp: MlpArgs



class DualLinkerWithTransformer(BaseTextModel):

    def __init__(self, args: DualTransformerArgs):
        super().__init__(args)
        self._device = device.compute_device()
        issue_model = resolve_and_wrap_transformer_model(args.issue_model)
        code_model = resolve_and_wrap_transformer_model(args.code_model)
        size = issue_model.output_size + code_model.output_size
        del issue_model, code_model
        self._mlp = args.mlp.build(size, 1)
        self._logger = logs.get_logger(self.__class__.__name__)
        self._logged_max_length = False

    @staticmethod
    def get_args() -> type[DualTransformerArgs]:
        return DualTransformerArgs

    def forward(self, x):
        return self._mlp(x).flatten()

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {'issue': 'issue-features', 'source': 'source-code', 'filename': 'filenames'}

    def transform(self, issue, source, filename):
        if not source:
            return torch.cat([issue, filename])
        return torch.cat([issue, filename, source])
