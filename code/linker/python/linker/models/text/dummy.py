import dataclasses

import torch
from transformers import AutoTokenizer
from .base import BaseTextModel


@dataclasses.dataclass
class NullArgs:
    pass


class DummyDualTransformerLinker(BaseTextModel):

    def __init__(self, args: NullArgs):
        super().__init__(args)
        self._dummy = torch.nn.Linear(1, 1)
        self._tokenizer = AutoTokenizer.from_pretrained('google/bert_uncased_L-2_H-128_A-2')

    @staticmethod
    def get_args() -> type[NullArgs]:
        return NullArgs

    def forward(self, issue, source):
        batch_size = issue['input_ids'].shape[0]
        return torch.randint(-10, 10, (batch_size,)).to(dtype=torch.float32).requires_grad_(True)

    def prepare_issue(self, text):
        return self._tokenizer(text,
                               padding='max_length',
                               max_length=128,
                               truncation=True,
                               return_tensors='pt')

    def prepare_code(self, text):
        return self._tokenizer(text,
                               padding='max_length',
                               max_length=128,
                               truncation=True,
                               return_tensors='pt')
