import torch

class DummyLayer(torch.nn.Module):

    def forward(self, x):
        return x
