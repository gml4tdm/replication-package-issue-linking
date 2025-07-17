import warnings

import torch

from .abstract import PeekableDataset


# noinspection PyTypeChecker
class UnderSampler(torch.utils.data.Sampler[int]):

    def __init__(self,
                 dataset: PeekableDataset,
                 minority_class, *,
                 max_imbalance_ratio: float | None = None,
                 max_samples: int | None = None,
                 generator=None):
        super().__init__()

        with torch.no_grad():
            if max_imbalance_ratio is None and max_samples is None:
                warnings.warn('No under-sampling strategy specified')
            self.dataset = dataset

            labels = torch.tensor(
                [self.dataset.label_of(i) for i in range(len(self.dataset))]
            )
            minority = labels == minority_class

            n_minority = minority.sum()

            if max_imbalance_ratio is not None:
                max_samples_hint = int(1/max_imbalance_ratio * n_minority)
            else:
                max_samples_hint = len(self.dataset)

            if max_samples is None:
                max_samples = max_samples_hint

            max_samples = min(max_samples, max_samples_hint)

            minority_indices, = torch.where(labels == minority_class)
            majority_indices, = torch.where(labels != minority_class)
            indices = torch.randperm(len(majority_indices), generator=generator)
            majority_sample_indices = indices[:max_samples]
            self.indices = torch.cat([
                minority_indices, majority_indices[majority_sample_indices]
            ])
            self.imbalance_ratio = n_minority / max_samples

    def __len__(self):
        return len(self.indices)

    def __iter__(self):
        yield from self.indices
