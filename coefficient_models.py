import torch
from torch.autograd import Variable
from torch.nn import Module, Linear
from torch.nn.functional import leaky_relu

from data import irrelevant_data_multiplier, seed_all
from utility import gpu

observation_count = 10


class Generator(Module):
    """The generator model."""

    def __init__(self):
        super().__init__()
        self.input_size = 10
        self.linear1 = Linear(self.input_size, 20)
        self.linear5 = Linear(20, 30)
        self.linear6 = Linear(30, observation_count * irrelevant_data_multiplier)

    def forward(self, x, add_noise=False):
        """The forward pass of the module."""
        x = leaky_relu(self.linear1(x))
        x = leaky_relu(self.linear5(x))
        x = self.linear6(x)
        return x


class MLP(Module):
    """The DNN MLP model."""

    def __init__(self):
        super().__init__()
        seed_all(0)
        self.linear1 = Linear(observation_count * irrelevant_data_multiplier, 16)
        self.linear3 = Linear(16, 4)
        self.linear4 = Linear(4, 1)
        self.feature_layer = None
        self.gradient_sum = gpu(Variable(torch.zeros(1)))

    def forward(self, x, add_noise=False):
        """The forward pass of the module."""
        x = leaky_relu(self.linear1(x))
        x = leaky_relu(self.linear3(x))
        self.feature_layer = x
        x = self.linear4(x)
        return x

    def register_gradient_sum_hooks(self):
        """A hook to remember the sum gradients of a backwards call."""

        def gradient_sum_hook(grad):
            """The hook callback."""
            nonlocal self
            self.gradient_sum += grad.abs().sum()
            return grad

        [parameter.register_hook(gradient_sum_hook) for parameter in self.parameters()]

    def zero_gradient_sum(self):
        """Zeros the sum gradients to allow for a new summing for logging."""
        self.gradient_sum = gpu(Variable(torch.zeros(1)))