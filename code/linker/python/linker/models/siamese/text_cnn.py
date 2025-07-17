import dataclasses

import torch

from ..utils.shared_args import TextCNNArgs
from .base import BaseSiameseTextModel, T


@dataclasses.dataclass
class SiameseCosineSimilarityTextCNNArgs:
    embedding_size: int
    vocabulary_size: int
    text_cnn_args: TextCNNArgs
    code_cnn_args: TextCNNArgs
    issue_length: int
    code_length: int
    filename_length: int
    pretrained_embeddings: str | None = None
    separate_embeddings: bool = False


class SiameseCosineSimilarityTextCNN(BaseSiameseTextModel):

    @staticmethod
    def get_args() -> type[T]:
        return SiameseCosineSimilarityTextCNNArgs

    def __init__(self, args: SiameseCosineSimilarityTextCNNArgs):
        super().__init__(args)
        self.issue_length = args.issue_length
        self.code_length = args.code_length
        self.filename_length = args.filename_length
        self.padding_index = args.vocabulary_size
        if args.pretrained_embeddings is not None:
            if args.separate_embeddings:
                raise ValueError('Cannot use separate embeddings with pretrained embeddings')
            weights = torch.load(args.pretrained_embeddings, weights_only=False)
            weights.append(torch.zeros(args.embedding_size))
            weights = torch.tensor(weights)
            self.embedding = torch.nn.Embedding.from_pretrained(weights,
                                                                freeze=True)
        else:
            if args.separate_embeddings:
                self.embedding = None
                self.issue_embedding = torch.nn.Embedding(args.vocabulary_size + 1,
                                                          args.embedding_size,
                                                          padding_idx=self.padding_index)
                self.code_embedding = torch.nn.Embedding(args.vocabulary_size + 1,
                                                         args.embedding_size,
                                                         padding_idx=self.padding_index)
            else:
                self.embedding = torch.nn.Embedding(args.vocabulary_size + 1,
                                                    args.embedding_size,
                                                    padding_idx=self.padding_index)
                self.issue_embedding = self.embedding
                self.code_embedding = self.embedding

        self.text_cnn = args.text_cnn_args.build(
            embedding_size=args.embedding_size
        )
        self.code_cnn = args.code_cnn_args.build(
            embedding_size=args.embedding_size
        )
        self.code_sim = torch.nn.CosineSimilarity(dim=1)
        self.name_sim = torch.nn.CosineSimilarity(dim=1)
        self.alpha = torch.nn.Parameter(torch.tensor(0.5))

    def forward(self, issue, code_info):
        code, filename = code_info
        issue_features = self._forward_cnn(issue, self.issue_embedding, self.text_cnn)
        code_features = self._forward_cnn(code, self.code_embedding, self.code_cnn)
        filename_features = self._forward_cnn(filename, self.code_embedding, self.code_cnn)
        phi_code = self.code_sim(code_features, issue_features)
        phi_name = self.name_sim(issue_features, filename_features)
        return self.alpha*phi_code + (1 - self.alpha)*phi_name

    def _forward_cnn(self, x, embedding, cnn):
        x = embedding(x)
        batch_size, w, h = x.shape
        x = x.reshape((batch_size, 1, w, h))
        return cnn(x)

    @staticmethod
    def feature_sources_user() -> dict[str, str]:
        return {'issue': 'issue-features'}

    @staticmethod
    def feature_sources_item() -> dict[str, str]:
        return {'source': 'source-code',
                'filename': 'filenames'}

    def transform_user(self, issue) -> torch.Tensor | dict:
        return _trim_or_pad(issue, self.issue_length, self.padding_index)

    def transform_item(self, source, filename) -> torch.Tensor | dict:
        return (
            _trim_or_pad(source, self.code_length, self.padding_index),
            _trim_or_pad(filename, self.filename_length, self.padding_index)
        )


def _trim_or_pad(x: torch.Tensor, length: int, padding_index: int) -> torch.Tensor:
    if len(x) > length:
        return x[:length]
    elif len(x) < length:
        return torch.cat([x, torch.full([length - len(x)], padding_index)], dim=0)
    else:
        return x