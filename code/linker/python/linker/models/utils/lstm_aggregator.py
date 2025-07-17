import torch


class BidirectionalLSTMAggregator(torch.nn.Module):

    def __init__(self, *,
                 input_size: int,
                 hidden_size: int):
        super().__init__()
        self.lstm = torch.nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=1,
            bidirectional=True,
            batch_first=True
        )
        self.hidden_size = hidden_size
        self.input_size = input_size
        self.output_size = hidden_size * 2

    def forward(self, x):
        output, (hidden, cell) = self.lstm(x)
        forward = hidden[0, :, :]
        backward = hidden[1, :, :]
        return torch.cat([forward, backward], dim=1)

    @staticmethod
    def prepare_sequence(x):
        # List of length batch size, with entries L x H
        padded = torch.nn.utils.rnn.pad_sequence(
            x, batch_first=True, padding_value=0.0, padding_side='right'
        )
        packed = torch.nn.utils.rnn.pack_padded_sequence(
            padded, [len(y) for y in x], batch_first=True, enforce_sorted=True
        )
        return packed
