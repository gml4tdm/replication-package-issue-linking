import dataclasses
import typing

import torch


from .base import BaseSiameseTextModel
from ..utils.transformer_models import resolve_and_wrap_transformer_model
from ..utils.lstm_aggregator import BidirectionalLSTMAggregator
from ..utils.shared_args import MlpArgs
from ..utils.dummy import DummyLayer


@dataclasses.dataclass
class MLPEnhancedAggregatingCosineSimilarityArgs:
    text_model: str
    code_model: str
    aggregation: typing.Literal['mean', 'bilstm'] = 'mean'
    alpha: float | None = None
    transformed_size: int | None = None
    issue_mlp: MlpArgs | None = None
    code_mlp: MlpArgs | None = None
    filename_mlp: MlpArgs | None = None


class MLPEnhancedSiameseAggregatingCosineSimilarityModel(BaseSiameseTextModel):

    def __init__(self, args: MLPEnhancedAggregatingCosineSimilarityArgs):
        super().__init__(args)
        issue_model = resolve_and_wrap_transformer_model(args.text_model)
        code_model = resolve_and_wrap_transformer_model(args.code_model)

        if args.aggregation == 'mean':
            self.issue_aggregation = DummyLayer()
            self.code_aggregation = DummyLayer()
            self.fn_aggregation = DummyLayer()

            issue_size = issue_model.output_size
            code_size = code_model.output_size
            filename_size = code_model.output_size
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
            issue_size = issue_model.output_size
            code_size = code_model.output_size
            filename_size = code_model.output_size
        else:
            raise ValueError(f'Unknown aggregation type: {args.aggregation}')

        if any(x is not None for x in [args.issue_mlp, args.code_mlp, args.filename_mlp]):
            assert args.transformed_size is not None
        if args.issue_mlp is not None:
            self.issue_mlp = args.issue_mlp.build(
                input_size=issue_size, output_size=args.transformed_size
            )
        else:
            self.issue_mlp = None
        if args.code_mlp is not None:
            self.code_mlp = args.code_mlp.build(
                input_size=code_size, output_size=args.transformed_size
            )
        else:
            self.code_mlp = None
        if args.filename_mlp is not None:
            self.filename_mlp = args.filename_mlp.build(
                input_size=filename_size, output_size=args.transformed_size
            )
        else:
            self.filename_mlp = None
        if args.alpha is not None:
            self.alpha = torch.nn.Parameter(torch.tensor(args.alpha))
        else:
            self.alpha = 0.5
        self.code_sim = torch.nn.CosineSimilarity()
        self.name_sim = torch.nn.CosineSimilarity()
        self.is_empty = all(x is None for x in [args.issue_mlp, args.code_mlp, args.filename_mlp]) and args.alpha is None
        self.dummy = torch.nn.Parameter(torch.tensor(0.0))

    def forward(self, issue, code_info):
        code, filename = code_info

        issue = self.issue_aggregation(issue)
        code = self.code_aggregation(code)
        filename = self.fn_aggregation(filename)

        if self.issue_mlp is not None:
            issue = self.issue_mlp(issue)
        if self.code_mlp is not None:
            code = self.code_mlp(code)
        if self.filename_mlp is not None:
            filename = self.filename_mlp(filename)
        phi_code = self.code_sim(issue, code)
        phi_name = self.name_sim(issue, filename)
        return self.alpha*phi_code + (1 - self.alpha)*phi_name + self.dummy - self.dummy

    @staticmethod
    def feature_sources_user() -> dict[str, str]:
        return {'issue': 'issue-features'}

    @staticmethod
    def feature_sources_item() -> dict[str, str]:
        return {'source': 'source-code',
                'filename': 'filenames'}

    def transform_item(self, source, filename) -> torch.Tensor | dict:
        if self.args.aggregation == 'mean':
            if source.numel() == 0:
                source = torch.zeros(*source.shape)
            else:
                source = source.mean(dim=0)
            filename = filename.mean(dim=0)
            return source, filename
        else:
            return source, filename

    def transform_user(self, issue) -> torch.Tensor | dict:
        if self.args.aggregation == 'mean':
            issue = issue.mean(dim=0)
            return issue
        else:
            return BidirectionalLSTMAggregator.prepare_sequence([issue])

    def item_collate_factory(self):
        if self.args.aggregation == 'mean':
            return None
        def collate(x):
            return (
                BidirectionalLSTMAggregator.prepare_sequence([
                    y[0] for y in x
                ]),
                BidirectionalLSTMAggregator.prepare_sequence([
                    y[1] for y in x
                ])
            )
        return collate

    @staticmethod
    def get_args():
        return MLPEnhancedAggregatingCosineSimilarityArgs
