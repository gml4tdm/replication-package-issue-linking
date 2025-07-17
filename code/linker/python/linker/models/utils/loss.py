import typing

import torch
from torch.nn import BCELoss, BCEWithLogitsLoss

__all__ = [
    'BCELoss',
    'BCEWithLogitsLoss',

    'BinaryFocalLoss',
    'BinaryFocalWithLogitsLoss',

    'DiceLoss',
    'DiceWithLogitsLoss',

    'ClassWeightedLoss',

    'CombinedLoss',

    'BayesianPersonalisedRankingLoss',
    'CustomMarginRankingLoss'
]


def _reduce(loss, reduction):
    if reduction == 'none':
        return loss
    elif reduction == 'mean':
        return loss.mean()
    elif reduction == 'sum':
        return loss.sum()
    else:
        raise ValueError(f'Unknown reduction {reduction}')


class CombinedLoss(torch.nn.Module):

    def __init__(self,
                 *losses: tuple[float, torch.nn.Module],
                 reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__()
        self._losses = losses
        self._reduction = reduction

    def forward(self, outputs, targets):
        raw = sum(
            (w * loss(outputs, targets) for w, loss in self._losses),
            start=torch.tensor(0.0)
        )
        return _reduce(raw, self._reduction)


class ClassWeightedLoss(torch.nn.Module):

    def __init__(self,
                 loss,
                 weights: dict[float | int | bool, float], *,
                 reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__()
        self._loss = loss
        self._weights = weights
        self._reduction = reduction

    def forward(self, outputs, targets):
        loss = self._loss(outputs, targets)
        if loss.shape != targets.shape:
            raise ValueError(
                f'Wrapped loss for {self.__class__.__name__} should not use any reduction'
            )
        for c, w in self._weights.items():
            loss[targets == c] *= w
        return _reduce(loss, self._reduction)


class _FocalLoss(torch.nn.Module):

    def __init__(self,
                 bce, gamma: float, *,
                 reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__()
        self._bce = bce
        self._gamma = gamma
        self._reduction = reduction

    def forward(self, outputs, targets):
        bce = self._bce(outputs, targets)
        if bce.shape != targets.shape:
            raise ValueError(
                f'Wrapped loss for {self.__class__.__name__} should not use any reduction'
            )
        pos = targets == 1
        neg = targets == 0
        # y = 1 --> pt = p --> Use 1 - pt
        bce[pos] *= (1 - outputs[pos])**self._gamma
        # y = 0 --> pt = 1 - p --> Use pt
        bce[neg] *= outputs[neg]**self._gamma
        return _reduce(bce, self._reduction)


class BinaryFocalLoss(_FocalLoss):

    def __init__(self, gamma: float, *,
                 reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__(
            torch.nn.BCELoss(reduction='none'),
            gamma,
            reduction=reduction
        )


class BinaryFocalWithLogitsLoss(_FocalLoss):

    def __init__(self, gamma: float, *,
                 reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__(
            torch.nn.BCEWithLogitsLoss(reduction='none'),
            gamma,
            reduction=reduction
        )


class DiceLoss(torch.nn.Module):

    def __init__(self, *, reduction: typing.Literal['none', 'mean', 'sum'] = 'none'):
        super().__init__()
        self._reduction = reduction

    def forward(self, outputs, targets):
        dice = 1 - (2*outputs*targets + 1) / (outputs + targets + 1)
        return _reduce(dice, self._reduction)


class DiceWithLogitsLoss(DiceLoss):

    def forward(self, outputs, targets):
        transformed = torch.nn.functional.sigmoid(outputs)
        return super().forward(transformed, targets)


class BayesianPersonalisedRankingLoss(torch.nn.Module):

    def __init__(self, reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__()
        self._reduction = reduction

    def forward(self, outputs, mask):
        diff = outputs[mask[:, 0]] - outputs[mask[:, 1]]
        logs_diffs = -torch.nn.functional.logsigmoid(diff)
        return _reduce(logs_diffs, self._reduction)


class CustomMarginRankingLoss(torch.nn.Module):

    def __init__(self, margin, reduction: typing.Literal['none', 'mean', 'sum'] = 'mean'):
        super().__init__()
        self._reduction = reduction
        self._margin = margin

    def forward(self, outputs, mask):
        diff = outputs[mask[:, 0]] - outputs[mask[:, 1]]
        n = len(diff)
        per_pair = torch.max(torch.zeros(n), torch.ones(n)*self._margin - diff)
        return _reduce(per_pair, self._reduction)
