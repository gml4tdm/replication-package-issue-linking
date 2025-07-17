import dataclasses

import torch

from ..utils.shared_args import MlpArgs
from .base import BaseTextModel, T


@dataclasses.dataclass
class MLPEnhancedCosineSimilarityArgs:
    input_size: int
    alpha: float | None = None
    transformed_size: int | None = None
    issue_mlp: MlpArgs | None = None
    code_mlp: MlpArgs | None = None
    filename_mlp: MlpArgs | None = None


class MLPEnhancedCosineSimilarityModel(BaseTextModel):

    def __init__(self, args: MLPEnhancedCosineSimilarityArgs):
        super().__init__(args)
        if any(x is not None for x in [args.issue_mlp, args.code_mlp, args.filename_mlp]):
            assert args.transformed_size is not None
        if args.issue_mlp is not None:
            self.issue_mlp = args.issue_mlp.build(
                input_size=args.input_size, output_size=args.transformed_size
            )
        else:
            self.issue_mlp = None
        if args.code_mlp is not None:
            self.code_mlp = args.code_mlp.build(
                input_size=args.input_size, output_size=args.transformed_size
            )
        else:
            self.code_mlp = None
        if args.filename_mlp is not None:
            self.filename_mlp = args.filename_mlp.build(
                input_size=args.input_size, output_size=args.transformed_size
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
        self.dummy = torch.nn.Parameter(torch.zeros(1))

    def forward(self, issue, code, filename):
        if self.issue_mlp is not None:
            issue = self.issue_mlp(issue)
        if self.code_mlp is not None:
            code = self.code_mlp(code)
        if self.filename_mlp is not None:
            filename = self.filename_mlp(filename)
        phi_code = self.code_sim(issue, code)
        phi_name = self.name_sim(issue, filename)
        return self.alpha*phi_code + (1 - self.alpha)*phi_name

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {
            'issue': 'issue-features',
            'code': 'source-code',
            'filename': 'filenames'
        }

    def transform(self, **kwargs) -> torch.Tensor | dict:
        return kwargs

    @staticmethod
    def get_args() -> type[T]:
        return MLPEnhancedCosineSimilarityArgs
