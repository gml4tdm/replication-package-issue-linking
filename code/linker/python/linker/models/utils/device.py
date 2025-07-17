import torch


def compute_device():
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
