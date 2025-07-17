import sys

import scipy
import torch


def scipy_to_torch_coo(x: scipy.sparse.coo_matrix):
    return torch.sparse_coo_tensor(
        torch.vstack([
            torch.from_numpy(x.row),
            torch.from_numpy(x.col),
        ]),
        torch.from_numpy(x.data),
        x.shape
    )


def cosine_similarity(x, y):
    return dot(x, y) / (norm(x) * norm(y))


def norm(x):
    return dot(x, x).sqrt().to_dense()


def dot(x, y):
    return (x * y).sum(dim=1).to_dense()


def ax_slice_coo(x: torch.Tensor,
             start: int | None,
             stop: int | None,
             axis: int):
    assert axis in (0, 1)
    if start is None:
        start = 0
    if stop is None:
        stop = x.shape[axis]
    x = x.coalesce()
    indices = x.indices()
    mask = (start <= indices[axis]) & (indices[axis] < stop)
    if axis == 0:
        new_shape = (stop - start, x.shape[1])
    else:
        new_shape = (x.shape[0], stop - start)
    return torch.sparse_coo_tensor(
        torch.vstack([
            indices[0, mask] - (axis == 0)*start,
            indices[1, mask] - (axis == 1)*start,
        ]),
        x.values()[mask],
        new_shape
    )


def guess_size_bytes(x):
    base = sys.getsizeof(x)
    base += _np_size(x.row)
    base += _np_size(x.col)
    base += _np_size(x.data)
    return base


def _np_size(x):
    if x.base is not None:
        return _np_size(x.base)
    return sys.getsizeof(x)
