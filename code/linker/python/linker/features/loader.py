from __future__ import annotations

import bisect
import dataclasses
import json
import math
import pathlib

import torch

from .abstract import PeekableDataset
from .. import _accelerator


@dataclasses.dataclass
class TwoWaySplitResult:
    first: IssueLinkingDatasetSplit
    second: IssueLinkingDatasetSplit
    target_ratio: float
    actual_ratio: float


@dataclasses.dataclass
class ThreeWaySplitResult:
    first: IssueLinkingDatasetSplit
    second: IssueLinkingDatasetSplit
    third: IssueLinkingDatasetSplit
    target_ratios: tuple[float, float, float]
    actual_ratios: tuple[float, float, float]


class IssueLinkingDatasetSplit(PeekableDataset):

    def __init__(self, *, _ds, _offset, _length, _buckets):
        self._ds = _ds
        self._offset = _offset
        self._length = _length
        self._bucket_start, self._bucket_end = _buckets

    def __getitem__(self, idx):
        return self._ds[self._offset + idx]

    def get_raw(self, idx: int):
        return self._ds.get_raw(self._offset + idx)

    def get_lightweight(self, idx: int):
        return self._ds.get_lightweight(self._offset + idx)

    def __len__(self):
        return self._length

    def label_of(self, idx: int) -> bool:
        return self._ds.label_of(self._offset + idx)

    def indexes(self, start: int, stop: int):
        idx = self._ds.indexes(self._offset + start, self._offset + stop)
        return idx

    def buckets(self) -> list[tuple[int, int]]:
        offset = 0
        result = []
        for b in range(self._bucket_start, self._bucket_end + 1):
            bucket = self._ds.get_bucket(b)
            result.append((offset, offset + bucket.total_samples))
            offset += bucket.total_samples
        return result

    @property
    def number_of_buckets(self) -> int:
        return self._bucket_end - self._bucket_start + 1

    def get_bucket_collection(self, index: int, *, return_raw=False, return_file_indexes=False):
        if index < 0 or index >= self.number_of_buckets:
            raise IndexError(f'Bucket index {index} out of range [0, {self.number_of_buckets})')
        return self._ds.get_bucket_collection(index + self._bucket_start,
                                              return_raw=return_raw,
                                              return_file_indexes=return_file_indexes)

    def split(self, r: float):
        assert 0 < r < 1
        ratios = []
        rev_map = {}
        total = 0
        for b in range(self._bucket_start, self._bucket_end + 1):
            bucket = self._ds.get_bucket(b)
            total += bucket.total_samples
            ratios.append(total / len(self))
            rev_map[b] = bucket.sample_offset
        index = bisect.bisect_left(ratios, r) + self._bucket_start
        bucket = self._ds.get_bucket(index)
        global_index = rev_map[index]
        assert self._length - bucket.sample_offset + self._offset == self._length - (global_index - self._offset), (
            self._length,
            bucket.sample_offset,
            global_index,
            self._offset
        )
        return TwoWaySplitResult(
            first=IssueLinkingDatasetSplit(
                _ds=self._ds,
                _offset=self._offset,
                _length=global_index - self._offset,
                _buckets=(self._bucket_start, index - 1)
            ),
            second=IssueLinkingDatasetSplit(
                _ds=self._ds,
                _offset=bucket.sample_offset,
                _length=self._length - bucket.sample_offset + self._offset,
                _buckets=(index, self._bucket_end)
            ),
            target_ratio=r,
            actual_ratio=ratios[index - 1 - self._bucket_start]
        )



class _PeekableSubsetProxy(PeekableDataset):

    def __init__(self, indices, dataset):
        self.indices = indices
        self.dataset = dataset

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        return self.dataset[self.indices[idx]]

    def label_of(self, idx: int) -> bool:
        return self.dataset.label_of(self.indices[idx])


class IssueLinkingDataset(PeekableDataset):

    def __init__(self, *,
                 loader: _accelerator.IndexLoader,
                 issue_loader: BulkFileLoader,
                 source_loader: BulkFileLoader,
                 cached_features: pathlib.Path,
                 required_features: dict[str, str] | tuple[dict[str, str], dict[str, str]],
                 transform=None,
                 collate=None,
                 bucket_mask: list[bool] | None = None):
        self._loader = loader
        self._issue_loader = issue_loader
        self._source_loader = source_loader
        self._cached_features_path = cached_features
        self._cached_features = None
        self._cached_buckets = None
        if transform is not None and isinstance(transform, tuple):
            self._user_transform, self._item_transform = transform
            self._transform = None
        elif transform is not None:
            self._user_transform = self._item_transform = transform
            self._transform = transform
        else:
            self._user_transform = self._item_transform = lambda x: x
            self._transform = lambda x: x
        if isinstance(required_features, tuple):
            self._required_user_features, self._required_item_features = required_features
            self._required_features = None
        else:
            self._required_user_features = self._required_item_features = None
            self._required_features = required_features
            assert collate is None
        if collate is not None:
            self._item_collate = collate
        else:
            self._item_collate = torch.utils.data.dataloader.default_collate
        self._bucket_mask = bucket_mask
        self._cached_samples = None

    @classmethod
    def from_files(cls, *,
                   directory: pathlib.Path,
                   required_features: dict[str, str] | tuple[dict[str, str], dict[str, str]],
                   transform,
                   cached_features: pathlib.Path | None = None,
                   collate=None,
                   bucket_mask: list[bool] | None = None):
        loader = _accelerator.IndexLoader.from_file(
            plan_path=str(directory / 'index.json'),
        )
        if cached_features is None:
            cached_features = directory
        return cls(
            loader=loader,
            issue_loader=BulkFileLoader(directory / 'issue-features'),
            source_loader=BulkFileLoader(directory / 'source-code'),
            required_features=required_features,
            transform=transform,
            cached_features=cached_features,
            collate=collate,
            bucket_mask=bucket_mask
        )

    @staticmethod
    def wrap_subset(subset: torch.utils.data.Subset):
        return _PeekableSubsetProxy(subset.indices, subset.dataset)

    @property
    def _buckets(self):
        if self._cached_buckets is None:
            self._cached_buckets = self._loader.get_issue_buckets()
        return self._cached_buckets

    def get_bucket(self, idx: int):
        return self._buckets[idx]

    @property
    def number_of_buckets(self):
        return self._loader.number_of_buckets()

    @property
    def _samples(self):
        if self._cached_samples is None:
            self._cached_samples = self._loader.lightweight_samples()
        return self._cached_samples

    @property
    def index_loader(self) -> _accelerator.IndexLoader:
        return self._loader

    def __len__(self) -> int:
        return len(self._loader)

    def __iter__(self):
        for i, b in enumerate(self._buckets):
            for s in self._loader.get_samples_for_bucket(i):
                yield s

    @property
    def positive_samples(self):
        return self._loader.total_positive_samples()

    @property
    def dropped_samples(self):
        return sum(bucket.dropped_samples for bucket in self._buckets)

    def label_of(self, idx: int) -> bool:
        return self._samples[idx].label

    @torch.no_grad()
    def indexes(self, start: int, stop: int):
        start_bucket = self._find_bucket(start)
        stop_bucket = self._find_bucket(stop - 1)
        indexes = []
        selected_buckets = self._buckets[start_bucket:stop_bucket+1]
        for i, b in enumerate(selected_buckets, start=start_bucket):
            if i == start_bucket and i == stop_bucket:
                rep = len(range(start - b.sample_offset, stop - b.sample_offset))
            elif i == start_bucket:
                rep = len(range(start - b.sample_offset, b.total_samples))
            elif i == stop_bucket:
                rep = len(range(stop - b.sample_offset))
            else:
                rep = b.total_samples
            indexes.append(torch.ones(rep, dtype=torch.long) * (i + 1))
        return torch.cat(indexes)

    def _find_bucket(self, idx: int):
        buckets= self._buckets
        low = 0
        high = len(buckets)
        while low < high:
            mid = (low + high) // 2
            bucket = buckets[mid]
            if bucket.sample_offset <= idx < bucket.sample_offset + bucket.total_samples:
                return mid
            elif idx < bucket.sample_offset:
                high = mid
            else:
                low = mid + 1
        raise IndexError(idx)

    def get_raw(self, idx: int):
        if not 0 <= idx < len(self):
            raise IndexError(idx)
        return self._loader[idx]

    def get_lightweight(self, idx: int):
        if not 0 <= idx < len(self):
            raise IndexError(idx)
        return self._samples[idx]

    def __getitem__(self, idx: int):
        if self._required_features is None:
            raise ValueError('required features not set')
        if not 0 <= idx < len(self):
            raise IndexError(idx)
        sample = self._loader[idx]
        features = self._fetch_from_cache(sample.issue_file_index,
                                          sample.source_file_index,
                                          sample.file_name_index,
                                          self._required_features)
        group_index = self.indexes(idx, idx + 1).item()
        if self._bucket_mask is not None and not self._bucket_mask[group_index]:
            return None
        result = self._transform(**features), sample.label, group_index
        return result

    def get_bucket_collection_with_indices(self, index: int):
        base = self.get_bucket_collection(index)
        collection = self._loader.get_bucket_sample_collection(index)
        indices = (
            collection.issue_file_index,
            [(sample.source_file_index, sample.file_name_index)
             for sample in collection.positives],
            [(sample.source_file_index, sample.file_name_index)
             for sample in collection.negatives]
        )
        return base, indices

    def get_bucket_collection(self,
                              index: int, *,
                              return_raw=False,
                              return_file_indexes=False):
        if self._required_user_features is None or self._required_item_features is None:
            raise ValueError('required user/item features not set')
        if self._bucket_mask is not None and not self._bucket_mask[index]:
            exclude = True
        else:
            exclude = False
        if exclude and not return_raw:
            return None
        collection = self._loader.get_bucket_sample_collection(index)
        issue_features = self._fetch_from_cache(collection.issue_file_index,
                                                None,
                                                None,
                                                self._required_user_features)
        positives = [
            self._fetch_from_cache(None,
                                   pos.source_file_index,
                                   pos.file_name_index,
                                   self._required_item_features)
            for pos in collection.positives
        ]
        negatives = [
            self._fetch_from_cache(None,
                                   neg.source_file_index,
                                   neg.file_name_index,
                                   self._required_item_features)
            for neg in collection.negatives
        ]
        inputs = (
            self._user_transform(**issue_features),
            self._item_collate([self._item_transform(**pos) for pos in positives]),
            self._item_collate([self._item_transform(**neg) for neg in negatives])
        )

        targets = torch.tensor([True] * len(positives) + [False] * len(negatives))
        n = len(positives) + len(negatives)
        indexes = torch.tensor([index + 1] * n)

        if not return_file_indexes:
            if exclude:
                return inputs, None, None
            return inputs, targets, indexes

        issue_index = collection.issue_file_index
        positives_src_index = [pos.source_file_index for pos in collection.positives]
        negatives_src_index = [neg.source_file_index for neg in collection.negatives]
        positives_fn_index = [pos.file_name_index for pos in collection.positives]
        negatives_fn_index = [neg.file_name_index for neg in collection.negatives]
        positives_index = (positives_src_index, positives_fn_index)
        negatives_index = (negatives_src_index, negatives_fn_index)
        inputs_index = (issue_index, positives_index, negatives_index)

        # targets/indexes: first pos, then neg
        if exclude:
            return inputs, None, None, inputs_index
        return inputs, targets, indexes, inputs_index

    def _fetch_from_cache(self,
                          issue_index,
                          source_index,
                          filename_index,
                          required_features):
        if self._cached_features is None:
            self._cached_features = {k: {} for k in required_features}
        for k in required_features:
            if k not in self._cached_features:
                self._cached_features[k] = {}
        out = {}
        indices = {'issue': issue_index,
                   'source': source_index,
                   'code': source_index,
                   'filename': filename_index}
        for key, path_hint in required_features.items():
            index = indices[key]
            if index is None:
                raise ValueError(f'Feature {key} (type {path_hint}) not available now')
            out[key] = self._cache_fetch(self._cached_features[key], index, path_hint)
        return out

    def _cache_fetch(self, cache, index, directory):
        file_index, item_index = index
        if file_index not in cache:
            fn1 = self._cached_features_path / directory / f'{file_index}.json.pt'
            if fn1.exists():
                cache[file_index] = torch.load(fn1)
            else:
                fn2 = self._cached_features_path / directory / f'{file_index}.json'
                if fn2.exists():
                    with open(fn2) as f:
                        cache[file_index] = json.load(f)
                else:
                    raise FileNotFoundError(f'File {fn1} or {fn2} not found')
        return cache[file_index][item_index]

    def split_on_history_three_way(self,
                                   r1: float,
                                   r2: float,
                                   r3: float) -> ThreeWaySplitResult:
        assert math.isclose(r1 + r2 + r3, 1)
        assert r1 > 0
        assert r2 > 0
        assert r3 > 0
        ratios = self._build_ratio_list()
        index_1 = bisect.bisect_left(ratios, r1)
        index_2 = bisect.bisect_right(ratios, r1 + r2)
        rev_map = {i: bucket.sample_offset
                   for i, bucket in enumerate(self._buckets)}
        global_index_1 = rev_map[index_1]
        global_index_2 = rev_map[index_2]
        first = IssueLinkingDatasetSplit(
            _ds=self,
            _offset=0,
            _length=global_index_1,
            _buckets=(0, index_1 - 1)
        )
        second = IssueLinkingDatasetSplit(
            _ds=self,
            _offset=global_index_1,
            _length=global_index_2 - global_index_1,
            _buckets=(index_1, index_2 - 1)
        )
        third = IssueLinkingDatasetSplit(
            _ds=self,
            _offset=global_index_2,
            _length=len(self) - global_index_2,
            _buckets=(index_2, len(self._buckets) - 1)
        )
        return ThreeWaySplitResult(
            first=first,
            second=second,
            third=third,
            target_ratios=(r1, r2, r3),
            actual_ratios=(
                len(first) / len(self),
                len(second) / len(self),
                len(third) / len(self)
            )
        )

    def _build_ratio_list(self):
        n = len(self)
        return [
            (b.sample_offset + b.total_samples) / n
            for b in self._buckets
        ]



class BulkFileLoader:

    def __init__(self, directory: pathlib.Path):
        self._dir = directory
        self._cache = {}

    def __getitem__(self, idx: tuple[int, int]):
        file_id, index = idx
        if file_id not in self._cache:
            self._cache[file_id] = self._load_file(file_id)
        return self._cache[file_id][index]

    def _load_file(self, file_id: int):
        with open(self._dir / f'{file_id}.json') as f:
            return json.load(f)
