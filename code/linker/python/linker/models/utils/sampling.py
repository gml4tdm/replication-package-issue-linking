import dataclasses
import typing

import matplotlib.pyplot as pyplot
import torch
from linker.models.utils.collation import to_device_collate

from .collation import repeat_collate, len_collate, split_collate

T = typing.TypeVar('T')


class _Sampler(typing.Generic[T]):
    """Samples combinations of samples from a dataset for use in e.g.
    triplet loss or Bayesian personalised ranking loss.

    If warmup_epochs is an integer, the first number of
    rounds will not involve any sampling based on sample
    difficulty; all items in the batch are returned.

    If the margin is not given, only hard negatives will be
    sampled (after the warmup). If the margin is a positive
    float, semi-hard negatives will also be sampled.

    The sampling strategy is either batch-all or batch-hard.
    """

    def __init__(self,
                 direction: typing.Literal['p<n', 'n<p'],
                 max_batch_size: int,
                 warmup_epochs: int | None = None,
                 margin: float | None = None,
                 strategy: typing.Literal['batch-all', 'batch-hard'] = 'batch-all',
                 distance_batch_size=32):
        # Set direction to the desired value of sign(P - N)
        if direction == 'p<n':
            self._direction = -1
        else:
            self._direction = 1

        self._max_batch_size = max_batch_size
        self._warmup = warmup_epochs
        self._margin = margin
        self._strategy = strategy
        if self._strategy == 'batch-hard':
            raise NotImplementedError('Batch hard sampling is not implemented')
        self._epoch = 0
        self._batch_size = distance_batch_size

    def mark_epoch(self):
        self._epoch += 1

    # def sample_batch(self, metric: T, user, items, labels: torch.Tensor):
    #     with torch.no_grad():
    #         if self._warmup is not None and self._epoch < self._warmup:
    #             return self._sample_full(labels)
    #         else:
    #             distances = self._compute_distances(metric, user, items, labels)
    #             self._sample_difficulty(distances, labels)

    def sample_batch(self, metric: T, user, positives, negatives, *, device=None):
        n_positives = len_collate(positives)
        n_negatives = len_collate(negatives)
        with torch.no_grad():
            if self._warmup is not None and self._epoch <= self._warmup:
                out =self._sample_from_full_cartesian(
                    n_positives, n_negatives, self._max_batch_size
                )
                return out
            else:
                distances = self._compute_distances(
                    metric, user, positives, negatives, device=device
                )
                # fig, ax = pyplot.subplots()
                # ax.hist(distances.numpy(), bins=100)
                # pyplot.show()
                # pyplot.close(fig)
                return self._sample_difficulty(distances, n_positives, n_negatives)

    def _sample_difficulty(self, distances, n_positives, n_negatives):
        pairs = torch.cartesian_prod(
            torch.arange(0, n_positives),
            torch.arange(0, n_negatives)
        )
        # Distances: P - N
        # Recall, for hard samples, we have:
        # N < P  <->  N - P < 0  <->  P - N > 0
        #
        # For semi-hard samples, we have
        # 1) P < N  <->   N - P < 0
        # 2) N < P + m  <->  P - N > -m
        if self._margin is None:
            predicate = self._find_hard_samples
        else:
            predicate = self._find_semi_hard_samples
        selected = pairs[predicate(distances)]
        if len(selected) == 0:
            return torch.tensor([[0, 0]])
        elif len(selected) > self._max_batch_size:
            return selected[torch.randperm(len(selected))[:self._max_batch_size]]
        else:
            return selected

    def _find_hard_samples(self, distances):
        if self._direction == -1:
            return distances > 0
        else:
            return distances < 0

    def _find_semi_hard_samples(self, distances):
        if self._direction == -1:
            return distances > -self._margin
        else:
            return distances < self._margin

    def _compute_distances(self, metric: T, user, items, labels, *, device=None):
        raise NotImplementedError()

    def _scores_to_distances(self, scores: torch.Tensor, n_positives, n_negatives):
        assert len(scores) == n_positives + n_negatives
        matrix = torch.cartesian_prod(
            torch.arange(0, n_positives),
            torch.arange(n_positives, n_negatives + n_positives)
        )

        distances = scores[matrix[:, 0]] - scores[matrix[:, 1]]
        return distances

    def _sample_from_full_cartesian(self, lhs, rhs, max_count):
        # size = len(lhs) * len(rhs)
        # to_select = min(size, max_count)
        # indices = torch.randperm(size)[:to_select]
        # lhs_index = indices // len(rhs)
        # rhs_index = indices % len(rhs)
        # return torch.stack([lhs[lhs_index], rhs[rhs_index]]).swapaxes(0, 1)
        matrix = torch.cartesian_prod(
            torch.arange(lhs), torch.arange(rhs)
        )
        if len(matrix) <= max_count:
            return matrix
        else:
            return matrix[torch.randperm(len(matrix))[:max_count]]


@dataclasses.dataclass
class TripletMetric:
    user_embedder: typing.Callable
    item_embedder: typing.Callable
    distance: typing.Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


class TripletSampler(_Sampler[TripletMetric]):

    def _compute_distances(self, metric: TripletMetric, user, positives, negatives, *, device=None):
        if device is not None:
            user = to_device_collate(user, device)
        user_embedding = metric.user_embedder(user).to('cpu')
        scores = []
        for batch in [positives, negatives]:
            for i in split_collate(batch, self._batch_size):
                if device is not None:
                    i = to_device_collate(i, device)
                embeddings = metric.item_embedder(i).to('cpu')
                user_embeddings = user_embedding.repeat(len(i), 1)
                scores.append(metric.distance(user_embeddings, embeddings))
        return self._scores_to_distances(
            torch.cat(scores),
            len_collate(positives),
            len_collate(negatives)
        )



@dataclasses.dataclass
class PairwiseMetric:
    ranker: typing.Callable


class PairwiseSampler(_Sampler[PairwiseMetric]):

    def _compute_distances(self, metric: PairwiseMetric, user, positives, negatives, *, device=None):
        scores = []
        for batch in [positives, negatives]:
            for i in split_collate(batch, self._batch_size):
                #users = user.repeat(len(i), *((1,) * len(user.shape)))
                users = repeat_collate(user, len_collate(i))
                if device is not None:
                    users = to_device_collate(users, device)
                    i = to_device_collate(i, device)
                scores.append(metric.ranker(users, i).to('cpu'))
        return self._scores_to_distances(
            torch.cat(scores),
            len_collate(positives),
            len_collate(negatives)
        )