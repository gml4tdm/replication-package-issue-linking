import dataclasses
import typing

import torch

from ..utils.shared_args import MlpArgs
from ..utils import device
from ..utils.lstm_aggregator import BidirectionalLSTMAggregator
from ..utils.transformer_models import resolve_and_wrap_transformer_model
from ..utils.dummy import DummyLayer
from .base import BaseTextModel


@dataclasses.dataclass
class AggregatingTransformerArgs:
    issue_model: str
    code_model: str
    aggregation: typing.Literal['mean', 'bilstm']
    mlp: MlpArgs


class AggregatingTransformer(BaseTextModel):

    def __init__(self, args: AggregatingTransformerArgs):
        super().__init__(args)
        self._device = device.compute_device()
        self.issue_model = resolve_and_wrap_transformer_model(args.issue_model)
        self.code_model = resolve_and_wrap_transformer_model(args.code_model)
        # The wrapped transformers are not subclasses of nn.Module,
        # so we need to register them explicitly.
        self.register_module('issue-model', self.issue_model.get_module())
        self.register_module('code-model', self.code_model.get_module())

        if args.aggregation == 'mean':
            self.issue_aggregation = MeanLayer(dim=1)
            self.code_aggregation = MeanLayer(dim=1)
            self.fn_aggregation = MeanLayer(dim=1)

            size = 0
            size += self.issue_model.output_size
            size += self.code_model.output_size      # code
            size += self.code_model.output_size      # filename
        elif args.aggregation == 'bilstm':
            self.issue_aggregation = BidirectionalLSTMAggregator(
                input_size=self.issue_model.output_size,
                hidden_size=self.issue_model.output_size
            )
            self.code_aggregation = BidirectionalLSTMAggregator(
                input_size=self.code_model.output_size,
                hidden_size=self.code_model.output_size
            )
            self.fn_aggregation = BidirectionalLSTMAggregator(
                input_size=self.code_model.output_size,
                hidden_size=self.code_model.output_size
            )
            size = 0
            size += self.issue_aggregation.output_size
            size += self.code_aggregation.output_size
            size += self.fn_aggregation.output_size
        else:
            raise ValueError(f'Unknown aggregation type: {args.aggregation}')

        self._mlp = args.mlp.build(size, 1)

    @staticmethod
    def get_args() -> type[AggregatingTransformerArgs]:
        return AggregatingTransformerArgs

    def forward(self, issue, source, filename):
        issue_mask, issue = self._pack(issue)
        source_mask, source = self._pack(source)
        filename_mask, filename = self._pack(filename)

        issue = self.issue_model.forward_get_vector(issue)
        source = self.code_model.forward_get_vector(source)
        filename = self.code_model.forward_get_vector(filename)

        issue = self._unpack(issue, issue_mask)
        source = self._unpack(source, source_mask)
        filename = self._unpack(filename, filename_mask)

        issue = self.issue_aggregation(issue)
        source = self.code_aggregation(source)
        filename = self.fn_aggregation(filename)

        x = torch.cat([issue, source, filename])
        return self._mlp(x).flatten()

    def _pack(self, x):
        mask = []
        stacked = []
        for i, y in enumerate(x):
            mask.extend([i] * len(y))
            stacked.extend(y)
        return mask, torch.utils.data.default_collate(stacked)

    def _unpack(self, x, mask):
        sequences = []
        y = torch.tensor(mask)
        for i in set(mask):
            sequences.append(x[y == i])
        return sequences

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {'issue': 'issue-features',
                'source': 'source-code',
                'filename': 'filenames'}

    def transform(self, issue, source, filename):
        return {'issue': issue, 'source': source, 'filename': filename}

    def collate_factory(self):
        if self.args.aggregation == 'mean':
            return None
        def collate(x):
            return {
                'issue': BidirectionalLSTMAggregator.prepare_sequence([
                    y['issue'] for y in x
                ]),
                'source': BidirectionalLSTMAggregator.prepare_sequence([
                    y['source'] for y in x
                ]),
                'filename': BidirectionalLSTMAggregator.prepare_sequence([
                    y['filename'] for y in x
                ])
            }
        return collate


class MeanLayer(torch.nn.Module):

    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        return x.mean(dim=self.dim)
