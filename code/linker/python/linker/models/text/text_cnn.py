import dataclasses

import torch

from ..utils.shared_args import MlpArgs, TextCNNArgs
from .base import BaseTextModel, T


@dataclasses.dataclass
class TextCNNArgs:
    embedding_size: int
    vocabulary_size: int
    issue_text_cnn_args: TextCNNArgs
    code_text_cnn_args: TextCNNArgs
    filename_text_cnn_args: TextCNNArgs
    issue_length: int
    code_length: int
    filename_length: int
    mlp: MlpArgs | None = None
    pretrained_embeddings: str | None = None


class TextCNN(BaseTextModel):

    def __init__(self, args: TextCNNArgs):
        super().__init__(args)
        self.issue_length = args.issue_length
        self.code_length = args.code_length
        self.filename_length = args.filename_length
        self.padding_index = args.vocabulary_size
        if args.pretrained_embeddings is not None:
            weights = torch.load(args.pretrained_embeddings, weights_only=False)
            weights.append(torch.zeros(args.embedding_size))
            weights = torch.tensor(weights)
            self.embedding = torch.nn.Embedding.from_pretrained(weights,
                                                                freeze=True)
        else:
            self.embedding = torch.nn.Embedding(args.vocabulary_size + 1,
                                                args.embedding_size,
                                                padding_idx=self.padding_index)
        self.issue_text_cnn = args.issue_text_cnn_args.build(
            embedding_size=args.embedding_size
        )
        self.code_text_cnn = args.code_text_cnn_args.build(
            embedding_size=args.embedding_size
        )
        self.filename_text_cnn = args.filename_text_cnn_args.build(
            embedding_size=args.embedding_size
        )
        combined_size = 0
        combined_size += self.issue_text_cnn.output_size
        combined_size += self.code_text_cnn.output_size
        combined_size += self.filename_text_cnn.output_size
        if args.mlp is not None:
            self.mlp = args.mlp.build(input_size=combined_size, output_size=1)
        else:
            self.mlp = None

    def forward(self,
                issue: torch.Tensor,
                code: torch.Tensor,
                filename: torch.Tensor):
        issue_features = self._forward_cnn(issue, self.issue_text_cnn)
        code_features = self._forward_cnn(code, self.code_text_cnn)
        filename_features = self._forward_cnn(filename, self.filename_text_cnn)
        x = torch.cat([issue_features, code_features, filename_features], dim=1)
        if self.mlp is not None:
            x = self.mlp(x)
        return x.flatten()

    def _forward_cnn(self, x, cnn):
        x = self.embedding(x)
        batch_size, w, h = x.shape
        x = x.reshape((batch_size, 1, w, h))
        return cnn(x)

    @staticmethod
    def feature_sources() -> dict[str, str]:
        return {
            'issue': 'issue-features',
            'code': 'source-code',
            'filename': 'filenames'
        }

    def transform(self, issue, code, filename) -> torch.Tensor | dict:
        return {
            'issue': _trim_or_pad(issue, self.issue_length, self.padding_index),
            'code': _trim_or_pad(code, self.code_length, self.padding_index),
            'filename': _trim_or_pad(filename, self.filename_length, self.padding_index)
        }

    @staticmethod
    def get_args() -> type[T]:
        return TextCNNArgs


def _trim_or_pad(x: torch.Tensor, length: int, padding_index: int) -> torch.Tensor:
    if len(x) > length:
        return x[:length]
    elif len(x) < length:
        return torch.cat([x, torch.full([length - len(x)], padding_index)], dim=0)
    else:
        return x
