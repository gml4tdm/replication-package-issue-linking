import torch


class ListDataset(torch.utils.data.Dataset):

    def __init__(self, data, transform):
        self._data = data
        self._transform = transform

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._transform(self._data[index])

    def __iter__(self):
        yield from self._data
