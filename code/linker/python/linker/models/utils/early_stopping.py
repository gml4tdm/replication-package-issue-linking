from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class EarlyStoppingConfig:
    patience: int
    min_delta: float = 0.0

class EarlyStopping:

    def __init__(self, config: EarlyStoppingConfig):
        self._min_delta = config.min_delta
        self._patience = config.patience
        self._best_loss = None
        self._counter = 0

    def early_stop(self, loss):
        if self._best_loss is None:
            self._best_loss = loss
            self._counter = 0
            return False

        if loss > self._best_loss or abs(loss - self._best_loss) < self._min_delta:
            self._counter += 1
            if self._counter >= self._patience:
                return True
        else:
            self._counter = 0
            self._best_loss = min(self._best_loss, loss)

        return False
