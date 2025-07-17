import torch


def index_collate(x, idx):
    if isinstance(x, dict):
        return {k: v[idx] for k, v in x.items()}
    elif isinstance(x, tuple):
        return tuple(v[idx] for v in x)
    elif isinstance(x, list):
        return [v[idx] for v in x]
    elif isinstance(x, torch.Tensor):
        return x[idx]
    else:
        raise NotImplementedError(
            f'Unknown type {type(x)} for index_collate'
        )


def len_collate(x):
    if isinstance(x, dict):
        key = next(iter(x))
        return len(x[key])
    elif isinstance(x, tuple):
        return len(x[0])
    elif isinstance(x, list):
        return len(x[0])
    elif isinstance(x, torch.Tensor):
        return x.shape[0]
    elif isinstance(x, torch.nn.utils.rnn.PackedSequence):
        return x.batch_sizes[0].item()
    else:
        raise NotImplementedError(
            f'Unknown type {type(x)} for len_collate'
        )


def to_device_collate(x, device):
    if isinstance(x, dict):
        return {k: v.to(device) for k, v in x.items()}
    elif isinstance(x, tuple):
        return tuple(v.to(device) for v in x)
    elif isinstance(x, list):
        return [v.to(device) for v in x]
    elif isinstance(x, torch.Tensor):
        return x.to(device)
    elif isinstance(x, torch.nn.utils.rnn.PackedSequence):
        return x.to(device)
    else:
        raise NotImplementedError(
            f'Unknown type {type(x)} for to_device_collate'
        )


def cat_collate(a, b):
    if isinstance(a, dict):
        assert isinstance(b, dict)
        assert a.keys() == b.keys()
        return {k: torch.cat([a[k], b[k]]) for k in a}
    elif isinstance(a, tuple):
        assert isinstance(b, tuple)
        assert len(a) == len(b)
        return tuple(torch.cat([a[i], b[i]]) for i in range(len(a)))
    elif isinstance(a, list):
        assert isinstance(b, list)
        assert len(a) == len(b)
        return [torch.cat([a[i], b[i]]) for i in range(len(a))]
    elif isinstance(a, torch.Tensor):
        assert isinstance(b, torch.Tensor)
        return torch.cat([a, b])
    else:
        raise NotImplementedError(
            f'Unknown type {type(a)} for cat_collate'
        )


def repeat_collate(x, n):
    if isinstance(x, dict):
        return {k: v.repeat(n, *([1] * len(v.shape))) for k, v in x.items()}
    elif isinstance(x, tuple):
        return tuple(v.repeat(n, *([1] * len(v.shape))) for v in x)
    elif isinstance(x, list):
        return [v.repeat(n, *([1] * len(v.shape))) for v in x]
    elif isinstance(x, torch.Tensor):
        return x.repeat(n, *([1] * len(x.shape)))
    else:
        raise NotImplementedError(
            f'Unknown type {type(x)} for repeat_collate'
        )


def split_collate(x, n):
    if isinstance(x, dict):
        splits = {k: torch.split(v, n) for k, v in x.items()}
        for i in range(len(splits[next(iter(splits))])):
            yield {k: v[i] for k, v in splits.items()}
    elif isinstance(x, tuple):
        splits = [torch.split(v, n) for v in x]
        for i in range(len(splits[0])):
            yield tuple(v[i] for v in splits)
    elif isinstance(x, list):
        splits = [torch.split(v, n) for v in x]
        for i in range(len(splits[0])):
            yield [v[i] for v in splits]
    elif isinstance(x, torch.Tensor):
        yield from torch.split(x, n)
    else:
        raise NotImplementedError(
            f'Unknown type {type(x)} for split_collate'
        )


def index_collate(x, idx):
    if isinstance(x, dict):
        return {k: v[idx] for k, v in x.items()}
    elif isinstance(x, tuple):
        return tuple(v[idx] for v in x)
    elif isinstance(x, list):
        return [v[idx] for v in x]
    elif isinstance(x, torch.Tensor):
        return x[idx]
    else:
        raise NotImplementedError(
            f'Unknown type {type(x)} for index_collate'
        )

def none_aware_collate(x):
    if isinstance(x, list):
        z = [y for y in x if y is not None]
        if not z:
            return []
        return torch.utils.data.dataloader.default_collate(z)
    else:
        return torch.utils.data.dataloader.default_collate(x)
