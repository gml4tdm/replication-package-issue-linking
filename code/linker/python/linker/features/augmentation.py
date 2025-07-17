import dataclasses

import torch

from ..models.utils.collation import len_collate, index_collate
from .loader import IssueLinkingDatasetSplit, IssueLinkingDataset


@dataclasses.dataclass(frozen=True)
class Dropping:
    fraction: float
    epochs: int


@dataclasses.dataclass(frozen=True)
class UnderSampling:
    max_imbalance_ratio: float | None = None
    max_samples: int | None = None
    dynamic: bool = False


@dataclasses.dataclass(frozen=True)
class OverSampling:
    max_imbalance_ratio: float | None = None
    min_samples: int | None = None
    dynamic: bool = False



class IssueBucketBatcher(torch.utils.data.Dataset):

    def __init__(self,
                 ds: IssueLinkingDataset | IssueLinkingDatasetSplit, *,
                 under_sample: UnderSampling | None = None,
                 generator=None):
        super().__init__()
        self._ds = ds
        self._length = ds.number_of_buckets
        self._under_sample = under_sample
        self._generator = generator
        self._cached_mask = None
        self._cached_cls = None

    def __len__(self):
        return self._length

    def __getitem__(self, idx):
        out = self._ds.get_bucket_collection(idx)
        if out is None:
            return None
        (user, positives, negatives), targets, indexes = out
        if self._under_sample is not None:
            if self._under_sample.dynamic:
                mask, cls = self._compute_under_sampling(positives, negatives)
            elif self._cached_mask is None:
                mask, cls = self._compute_under_sampling(positives, negatives)
                self._cached_mask = mask
                self._cached_cls = cls
            else:
                mask = self._cached_mask
                cls = self._cached_cls

            if cls:
                targets = torch.cat([
                    targets[:len_collate(positives)][mask],
                    targets[len_collate(positives):]
                ])
                indexes = torch.cat([
                    indexes[:len_collate(positives)][mask],
                    indexes[len_collate(positives):]
                ])
                positives = index_collate(positives, mask)
            else:
                targets = torch.cat([
                    targets[:len_collate(positives)],
                    targets[len_collate(positives):][mask]
                ])
                indexes = torch.cat([
                    indexes[:len_collate(positives)],
                    indexes[len_collate(positives):][mask]
                ])
                negatives = index_collate(negatives, mask)

        return (user, positives, negatives), targets, indexes

    def _compute_under_sampling(self, positives, negatives):
        majority = len_collate(positives) > len_collate(negatives)
        if majority:
            n_majority = len_collate(positives)
            n_minority = len_collate(negatives)
        else:
            n_majority = len_collate(negatives)
            n_minority = len_collate(positives)

        if self._under_sample.max_imbalance_ratio is not None:
            max_samples_hint = int(1 / self._under_sample.max_imbalance_ratio * n_minority)
        else:
            max_samples_hint = n_majority

        if self._under_sample.max_samples is not None:
            max_samples = self._under_sample.max_samples
        else:
            max_samples = max_samples_hint

        max_samples = min(max_samples, max_samples_hint)

        indices = torch.randperm(n_majority, generator=self._generator)
        indices_to_keep = indices[:max_samples]
        sorted_to_keep, _ = torch.sort(indices_to_keep)

        return sorted_to_keep, majority


class PairwiseDataAugmentationPipeline(torch.utils.data.Sampler):

    def __init__(self,
                 ds: IssueLinkingDatasetSplit, *,
                 drop: list[Dropping] | None = None):
        super().__init__()
        self._ds = ds
        self._drop = drop

        if self._drop is not None:
            self._exclusion_epoch_mask = self._compute_drop_splits(self._ds, self._drop)
        else:
            self._exclusion_epoch_mask = [float('inf')] * ds.number_of_buckets

        self._epoch = 1

    def __len__(self):
        return sum(x > self._epoch for x in self._exclusion_epoch_mask)

    def __iter__(self):
        for b, th in enumerate(self._exclusion_epoch_mask):
            if th > self._epoch:
                yield b
        self._epoch += 1

    def _compute_drop_splits(self,
                             ds: IssueLinkingDatasetSplit,
                             drops: list[Dropping]):
        sizes = []
        total = 0
        for b in range(ds.number_of_buckets):
            (_, positives, negatives), _, _ = ds.get_bucket_collection(
                b, return_raw=True
            )
            total += len_collate(positives) * len_collate(negatives)
            sizes.append(total)

        fractions = [x / total for x in sizes]

        assert sorted(drops, key=lambda x: x.epochs) == drops
        assert sorted(drops, key=lambda x: x.fraction) == drops

        def _select(f):
            for d in drops:
                if f < d.fraction:
                    return d.epochs
            return float('inf')

        return [_select(f) for f in fractions]


class DataAugmentationPipeline(torch.utils.data.Sampler):

    def __init__(self,
                 ds: IssueLinkingDatasetSplit, *,
                 drop: list[Dropping] | None = None,
                 under_sample: UnderSampling | None = None,
                 over_sample: OverSampling | None = None,
                 generator=None):
        super().__init__()
        self._ds = ds
        self._drop = drop
        self._under_sample = under_sample
        self._over_sample = over_sample
        self._generator = generator

        labels = torch.tensor([self._ds.label_of(i)
                               for i in range(len(self._ds))])
        classes = labels.unique()
        assert len(classes) == 2
        self._minority_class = min(classes, key=lambda c: (labels == c).sum())  # type: ignore
        self._majority_class = list(set(classes) - {self._minority_class})[0]

        if self._drop is not None:
            self._splits = self._compute_drop_splits(self._ds, self._drop)
            self._split_epochs = [d.epochs for d in self._drop]
        else:
            self._splits = [torch.arange(len(self._ds))]
            self._split_epochs = [float('inf')]

        if self._under_sampling and not self._dynamic_under_sampling:
            self._under_sampling_masks = self._compute_under_sampling_masks(
                self._splits
            )
            indices = [
                bucket[mask]
                for bucket, mask in zip(self._splits, self._under_sampling_masks)
            ]
        else:
            self._under_sampling_masks = None
            indices = self._splits

        if self._over_sampling and not self._dynamic_over_sampling:
            self._over_sampling_masks = self._compute_over_sampling_masks(
               indices
            )
        else:
            self._over_sampling_masks = None

        self._epoch = 0
        self._split_index = 0

        self._imbalance_ratio = self._compute_imbalance_ratio(self._splits)

    def estimate_imbalance_ratio(self):
        return self._imbalance_ratio

    @property
    def _under_sampling(self) -> bool:
        return self._under_sample is not None

    @property
    def _dynamic_under_sampling(self) -> bool:
        return self._under_sampling and self._under_sample.dynamic

    @property
    def _over_sampling(self) -> bool:
        return self._over_sample is not None

    @property
    def _dynamic_over_sampling(self) -> bool:
        return self._over_sampling and self._over_sample.dynamic

    def _process_indices(self, indices):
        if self._under_sampling:
            if self._dynamic_under_sampling:
                masks = self._compute_under_sampling_masks(indices)

                # Used for length computation
                if self._under_sampling_masks is None:
                    self._under_sampling_masks = masks
            else:
                masks = self._under_sampling_masks[self._split_index:]
            indices = [bucket[mask] for bucket, mask in zip(indices, masks)]

        if self._over_sampling:
            if self._dynamic_over_sampling:
                masks = self._compute_over_sampling_masks(indices)

                # Used for length computation
                if self._over_sampling_masks is None:
                    self._over_sampling_masks = masks
            else:
                masks = self._over_sampling_masks[self._split_index:]
            indices = [bucket[mask] for bucket, mask in zip(indices, masks)]

        return indices

    def _compute_imbalance_ratio(self, indices):
        indices = self._process_indices(indices)
        n_minority = 0
        n_majority = 0
        for bucket in indices:
            minority, majority = self._get_class_info(bucket)
            n_minority += minority.sum().item()
            n_majority += majority.sum().item()
        return n_minority / n_majority

    def __iter__(self):
        self._epoch += 1
        if self._increase_drop():
            self._split_index += 1
        indices = self._splits[self._split_index:]
        indices = self._process_indices(indices)
        for bucket in indices:
            yield from bucket

    def __len__(self):
        return self._len_at_epoch(self._epoch + 1)

    def _len_at_epoch(self, e: int) -> int:
        if self._over_sampling and not self._dynamic_over_sampling:
            sizes = [len(mask) for mask in self._over_sampling_masks]
        elif self._under_sampling and not self._dynamic_under_sampling:
            sizes = [len(mask) for mask in self._under_sampling_masks]
        else:
            sizes = [len(s) for s in self._splits]

        size = sum(sizes)
        for i, threshold in enumerate(self._split_epochs):
            if e > threshold:
                size -= sizes[i]

        return size

    def _increase_drop(self):
        return (
                self._split_index < len(self._split_epochs)
                and self._epoch > self._split_epochs[self._split_index]
        )

    @staticmethod
    def _compute_drop_splits(ds: IssueLinkingDatasetSplit,
                             drops: list[Dropping]) -> list[torch.Tensor]:
        # Verify that fractions and epochs are increasing
        for i in range(len(drops) - 1):
            assert drops[i].fraction < drops[i + 1].fraction
            assert drops[i].epochs < drops[i + 1].epochs
        # Verify numerical bounds
        for d in drops:
            assert 0 < d.fraction < 1
            assert 0 < d.epochs

        # Compute actual splits
        ds_splits = []
        remaining_fraction = 1.0
        current = ds
        for d in drops:
            r = (d.fraction + remaining_fraction - 1) / remaining_fraction
            remaining_fraction = 1 - d.fraction
            result = current.split(r)
            ds_splits.append(result.first)
            current = result.second
        ds_splits.append(current)

        # Convert splits to indices
        splits = []
        offset = 0
        for s in ds_splits:
            splits.append(torch.arange(offset, offset + len(s)))
            offset += len(s)
        return splits

    def _compute_under_sampling_masks(self, indices):
        return [
            self._compute_under_sampling_mask(bucket)[0]
            for bucket in indices
        ]

    def _compute_under_sampling_mask(self, indices):
        assert self._under_sample is not None
        minority, majority = self._get_class_info(indices)
        n_minority = minority.sum().item()

        if self._under_sample.max_imbalance_ratio is not None:
            max_samples_hint = int(1/self._under_sample.max_imbalance_ratio * n_minority)
        else:
            max_samples_hint = len(indices)

        if self._under_sample.max_samples is not None:
            max_samples = self._under_sample.max_samples
        else:
            max_samples = max_samples_hint

        max_samples = min(max_samples, max_samples_hint)

        minority_indices, = torch.where(minority)
        majority_indices, = torch.where(majority)
        indices = torch.randperm(len(majority_indices),
                                 generator=self._generator)
        indices_to_keep = indices[:max_samples]

        ds_index, _ = torch.sort(
            torch.cat([minority_indices, majority_indices[indices_to_keep]])
        )
        return ds_index, n_minority / max_samples

    def _compute_over_sampling_masks(self, indices):
        return [
            self._compute_over_sampling_mask(bucket)[0]
            for bucket in indices
        ]

    def _compute_over_sampling_mask(self, indices):
        assert self._over_sample is not None
        minority, majority = self._get_class_info(indices)
        n_minority = minority.sum().item()
        n_majority = majority.sum().item()

        if self._over_sample.max_imbalance_ratio is not None:
            min_samples = int(self._over_sample.max_imbalance_ratio * n_majority)
        else:
            min_samples = 0

        if self._over_sample.min_samples is not None:
            min_samples = max(min_samples, self._over_sample.min_samples)

        to_add = max(0, min_samples - n_minority)
        minority_indices, = torch.where(minority)
        majority_indices, = torch.where(majority)
        mask = torch.randint(0, len(minority_indices),
                             size=(to_add,), generator=self._generator)

        ds_index = torch.cat([minority_indices,
                              minority_indices[mask],
                              majority_indices])
        shuffle = torch.randperm(len(ds_index), generator=self._generator)
        ds_index = ds_index[shuffle]

        return ds_index, min_samples / n_majority

    def _get_class_info(self, indices):
        labels = torch.tensor([self._ds.label_of(i) for i in indices])
        minority = labels == self._minority_class
        majority = labels == self._majority_class
        return minority, majority
