import torch


class FixedBatchSampler(torch.utils.data.Sampler):

    def __init__(self, dataset, batches):
        super().__init__(dataset)
        self._ds = dataset
        self._batches = batches

    def __len__(self):
        return len(self._batches)

    def __iter__(self):
        current = 0
        for size in self._batches:
            yield self._ds[current:current + size]
            current += size
