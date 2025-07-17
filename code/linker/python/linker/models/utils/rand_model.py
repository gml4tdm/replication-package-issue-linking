import torch


class RandomModel:

    def __init__(self, p: float):
        assert 0 <= p <= 1
        self._p = p

    def predict(self, n_samples: int):
        r = torch.rand(n_samples)
        q = 1 - self._p
        # Negative samples -- [0, 1 - p) -> [0, 0.5)
        r[r < q] *= 0.5 / q
        # Positive samples -- [1 - p, 1) -> [0.5, 1)
        r[r >= q] = (r[r >= q] - q) * 0.5 / self._p + 0.5
        return r