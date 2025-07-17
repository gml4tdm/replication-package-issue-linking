import collections.abc

import torch.nn

from .transformer_models import WrappedTransformer


class SlidingWindowSplitter:

    def __init__(self,
                 model: WrappedTransformer, *,
                 chunk_size: int,
                 overlap: int = 0,
                 padding: bool = True):
        self._model = model
        self._chunk_size = chunk_size - 2
        self._overlap = overlap
        self._pad = padding

    @classmethod
    def native(cls, model: WrappedTransformer, *, overlap: int = 0):
        return cls(
            model,
            chunk_size=model.max_length,
            overlap=overlap,
            padding=True
        )

    def split(self, x):
        # If x is a list, convert to buckets individually,
        # and then concatenate.
        if isinstance(x, str):
            x = [x]
        tokens_sets = [self._model.tokenize_raw(y) for y in x]
        buckets = [
            self._add_special_tokens(x)
            for tokens in tokens_sets
            for x in self._sliding_window_split(tokens)
        ]
        if self._pad:
            buckets = [self._pad_bucket(x) for x in buckets]
        return buckets

    def _sliding_window_split(self, tokens):
        key = next(iter(tokens.keys()))
        length = len(tokens[key])
        buckets = []
        start = 0
        while start < length and (start == 0 or length - start > self._overlap):
            end = min(start + self._chunk_size, length)
            buckets.append({k: torch.tensor(v[start:end]) for k, v in tokens.items()})
            start += self._chunk_size - self._overlap
        return buckets

    def _pad_bucket(self, tokens):
        key = next(iter(tokens.keys()))
        length = len(tokens[key])
        difference = self._model.max_length - length
        if difference == 0:
            return tokens
        if self._model.padding_side != 'right':
            raise ValueError('Padding only supported on right side')
        pad, pad_at = self._model.pad_token
        tokens['input_ids'] = self._pad_one(tokens['input_ids'], difference, pad)
        tokens['attention_mask'] = self._pad_one(tokens['attention_mask'], difference, pad_at)
        if 'token_type_ids' in tokens:
            tokens['token_type_ids'] = self._pad_one(tokens['token_type_ids'], difference, 0)
        return tokens

    @staticmethod
    def _pad_one(x, count, item):
        if isinstance(x, list):
            return x + [item]*count
        else:
            return torch.cat([x, torch.tensor([item]*count)])

    def _add_special_tokens(self, tokens):
        cls, cls_at = self._model.special_start_token
        sep, sep_at = self._model.special_end_token

        out = {}

        input_ids = tokens.pop('input_ids')
        input_ids = self._add_tokens(input_ids, cls, sep)
        out['input_ids'] = input_ids

        attention_mask = tokens.pop('attention_mask')
        attention_mask = self._add_tokens(attention_mask, cls_at, sep_at)
        out['attention_mask'] = attention_mask

        if 'token_type_ids' in tokens:
            token_type_ids = tokens.pop('token_type_ids')
            token_type_ids = self._add_tokens(token_type_ids, 0, 0)
            out['token_type_ids'] = token_type_ids

        if tokens:
            raise ValueError(f'Do not know how to add special tokens for {tokens}')
        return out

    def _add_tokens(self, x, start, end):
        if isinstance(x, list):
            x.insert(0, start)
            x.append(end)
            return x
        else:
            return torch.cat([
                torch.tensor([start]),
                x,
                torch.tensor([end])
            ])
