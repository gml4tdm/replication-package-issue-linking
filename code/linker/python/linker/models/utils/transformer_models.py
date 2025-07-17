from __future__ import annotations

import abc
import typing

import torch
from transformers import AutoTokenizer, AutoModel, PreTrainedTokenizer, PreTrainedModel

_MODELS = {
    'modern-bert-base': 'answerdotai/ModernBERT-base',
    'modern-bert-large': 'answerdotai/ModernBERT-large',
    'bert-tiny': 'google/bert_uncased_L-2_H-128_A-2',
    'codet5p-small': 'Salesforce/codet5p-220m'
}

_SIZES = {
    'answerdotai/ModernBERT-base': (8192, 768),
    'answerdotai/ModernBERT-large': (8192, 768),
    'google/bert_uncased_L-2_H-128_A-2': (512, 128),
    'Salesforce/codet5p-220m': (512, 768)
}


def resolve_transformer_model(name: str) -> tuple[str, tuple[int, int] | None]:
    r = _MODELS.get(name, name)
    return r, _SIZES.get(r, None)


def resolve_and_wrap_transformer_model(name: str) -> WrappedTransformer:
    resolved_name, _ = resolve_transformer_model(name)
    if resolved_name.startswith('Salesforce/'):
        return WrappedEncoderDecoder.from_pretrained(resolved_name)
    return DefaultWrappedTransformer.from_pretrained(resolved_name)


def _max_length_helper(name, model, tokenizer):
    if hasattr(tokenizer, 'model_max_length'):
        candidate = tokenizer.model_max_length
        if candidate < 10**9:
            # Sometimes this value exists, but it is set
            # to a very large value
            return candidate
    attributes = [
        'max_position_embeddings',
        'max_length',
        'model_max_length',
    ]
    for attr in attributes:
        if hasattr(model.config, attr):
            candidate = getattr(model.config, attr)
            if candidate < 10**9:
                return candidate
    return _SIZES[name][0]


class WrappedTransformer(abc.ABC):

    @abc.abstractmethod
    def get_module(self) -> torch.nn.Module:
        pass

    @abc.abstractmethod
    def forward(self, x):
        pass

    @abc.abstractmethod
    def forward_get_vector(self, x):
        pass

    @abc.abstractmethod
    def tokenize(self, text: str | list[str]) -> typing.Any:
        pass

    @abc.abstractmethod
    def tokenize_raw(self, text: str) -> typing.Any:
        pass

    @abc.abstractmethod
    def to(self, device):
        pass

    @property
    @abc.abstractmethod
    def output_size(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def max_length(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def special_start_token(self) -> tuple[int, float | int] | None:
        pass

    @property
    @abc.abstractmethod
    def special_end_token(self) -> tuple[int, float | int] | None:
        pass

    @property
    @abc.abstractmethod
    def padding_side(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def pad_token(self) -> tuple[int, float | int]:
        pass



class DefaultWrappedTransformer(WrappedTransformer):

    def __init__(self,
                 tokenizer: PreTrainedTokenizer,
                 model: PreTrainedModel,
                 name: str):
        super().__init__()
        self._tokenizer = tokenizer
        self._model = model
        self._device = 'cpu'    # Default
        self._name = name

    def get_module(self) -> torch.nn.Module:
        return self._model

    @classmethod
    def from_pretrained(cls, name: str):
        resolved_name = _MODELS.get(name, name)
        tokenizer = AutoTokenizer.from_pretrained(resolved_name)
        model = AutoModel.from_pretrained(resolved_name)
        return cls(tokenizer, model, resolved_name)

    def tokenize(self, text: str | list[str]):
        if isinstance(text, str):
            text = [text]
        out = self._tokenizer(
            *text,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
            max_length=self.max_length
        )
        # Tokenizers are designed to work on batches,
        # but we assume single examples.
        return {k: v[0] for k, v in out.items()}

    def tokenize_raw(self, text: str):
        return self._tokenizer(
            text,
            truncation=False,
            padding=False,
            add_special_tokens=False
        )

    def to(self, device):
        self._model = self._model.to(device)
        self._device = device

    def forward(self, x):
        y = {k: v.to(self._device) for k, v in x.items()}       # .squeeze(1)
        return self._model(**y)

    def forward_get_vector(self, x):
        y = self.forward(x)
        return y.last_hidden_state[:,0,:]

    @property
    def output_size(self) -> int:
        return self._model.config.hidden_size

    @property
    def max_length(self) -> int:
        return _max_length_helper(self._name, self._model, self._tokenizer)

    @property
    def special_start_token(self) -> tuple[int, float | int] | None:
        return self._tokenizer.cls_token_id, 1

    @property
    def special_end_token(self) -> tuple[int, float | int] | None:
        return self._tokenizer.sep_token_id, 1

    @property
    def pad_token(self) -> tuple[int, float | int]:
        return self._tokenizer.pad_token_id, 0

    @property
    def padding_side(self) -> str:
        return self._tokenizer.padding_side


class WrappedEncoderDecoder(DefaultWrappedTransformer):

    def forward(self, x):
        x = {k: v.to(self._device) for k, v in x.items()}
        return self._model.encoder(**x)
