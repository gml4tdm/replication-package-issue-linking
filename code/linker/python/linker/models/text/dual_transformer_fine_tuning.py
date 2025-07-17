import dataclasses

import torch

from ...utils import logs
from ..utils.transformer_models import resolve_and_wrap_transformer_model
from ..utils.shared_args import MlpArgs
from .base import BaseTextModel, T


@dataclasses.dataclass
class DualTransformerArgs:
    issue_model: str
    code_model: str
    mlp: MlpArgs



class DualTransformerLinker(BaseTextModel):

    def __init__(self, args: DualTransformerArgs):
        super().__init__(args)
        self._issue_model = resolve_and_wrap_transformer_model(args.issue_model)
        self._code_model = resolve_and_wrap_transformer_model(args.code_model)
        size = self._issue_model.output_size + self._code_model.output_size
        # The wrapped transformers are not subclasses of nn.Module,
        # so we need to register them explicitly.
        self.register_module('issue-model', self._issue_model.get_module())
        self.register_module('code-model', self._code_model.get_module())
        self._mlp = args.mlp.build(size, 1)
        self._logger = logs.get_logger(self.__class__.__name__)
        self._logged_max_length = False

    @staticmethod
    def get_args() -> type[T]:
        return DualTransformerArgs

    def forward(self, issue, source):
        #issue = {k: v.squeeze(1) for k, v in issue.items()}
        #source = {k: v.squeeze(1) for k, v in source.items()}
        issue = self._issue_model.forward_get_vector(**issue)
        source = self._code_model.forward_get_vector(**source)
        x = self._mlp(
            torch.cat([issue, source], dim=1)
        )
        return x.flatten()

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {'issue': 'issue-features',
                'source': 'source-code',
                'filename': 'filenames'}

    def transform(self, issue, source, filename):
        return {
            'issue': self._issue_model.tokenize(issue),
            'source': self._code_model.tokenize([filename, source])
        }

