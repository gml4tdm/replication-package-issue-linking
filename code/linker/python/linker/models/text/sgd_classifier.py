import dataclasses

import torch
from sklearn.linear_model import SGDClassifier

from .base import BaseTextModel


@dataclasses.dataclass
class SgdArgs:
    pass


class SGDClassifierWrapperWithAggregation(BaseTextModel):

    def __init__(self, args: SgdArgs):
        super().__init__(args)
        self._model = None

    @staticmethod
    def get_args() -> type[SgdArgs]:
        return SgdArgs

    def set_class_weights(self, weights):
        self._model = SGDClassifier(class_weight=weights,
                                    learning_rate='optimal',
                                    loss='log_loss')

    def forward(self, *_args, **_kwargs):
        return NotImplementedError()

    def partial_fit(self, x, y, classes):
        assert self._model is not None
        self._model.partial_fit(x, y, classes=classes)

    def predict_proba(self, x):
        assert self._model is not None
        return self._model.predict_proba(x)

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {'issue': 'issue-features',
                'source': 'source-code',
                'filename': 'filenames'}

    def transform(self, issue, source, filename) -> torch.Tensor | dict:
        issue = issue.mean(dim=0)
        if source.numel() == 0:
            source = filename
        else:
            source = torch.cat([filename, source])
        source = source.mean(dim=0)
        out = torch.cat([issue, source])
        return out
