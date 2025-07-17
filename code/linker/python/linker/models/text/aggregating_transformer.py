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
        issue_model = resolve_and_wrap_transformer_model(args.issue_model)
        code_model = resolve_and_wrap_transformer_model(args.code_model)

        if args.aggregation == 'mean':
            self.issue_aggregation = DummyLayer()
            self.code_aggregation = DummyLayer()
            self.fn_aggregation = DummyLayer()

            size = 0
            size += issue_model.output_size
            size += code_model.output_size      # code
            size += code_model.output_size      # filename
        elif args.aggregation == 'bilstm':
            self.issue_aggregation = BidirectionalLSTMAggregator(
                input_size=issue_model.output_size,
                hidden_size=issue_model.output_size
            )
            self.code_aggregation = BidirectionalLSTMAggregator(
                input_size=code_model.output_size,
                hidden_size=code_model.output_size
            )
            self.fn_aggregation = BidirectionalLSTMAggregator(
                input_size=code_model.output_size,
                hidden_size=code_model.output_size
            )
            size = 0
            size += self.issue_aggregation.output_size
            size += self.code_aggregation.output_size
            size += self.fn_aggregation.output_size
        else:
            raise ValueError(f'Unknown aggregation type: {args.aggregation}')
        del issue_model, code_model
        self._mlp = args.mlp.build(size, 1)

    @staticmethod
    def get_args() -> type[AggregatingTransformerArgs]:
        return AggregatingTransformerArgs

    def forward(self, issue, source, filename):
        issue = self.issue_aggregation(issue)
        source = self.code_aggregation(source)
        filename = self.fn_aggregation(filename)
        # Batch x S
        x = torch.cat([issue, source, filename], dim=1)
        return self._mlp(x).flatten()

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {'issue': 'issue-features', 'source': 'source-code', 'filename': 'filenames'}

    def transform(self, issue, source, filename):
        if self.args.aggregation == 'mean':
            issue = issue.mean(dim=0)
            if source.numel() == 0:
                source = torch.zeros(*source.shape)
            else:
                source = source.mean(dim=0)
            filename = filename.mean(dim=0)
            return {'issue': issue, 'source': source, 'filename': filename}
        else:
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