import random

from pathlib import Path

from random_sets.datasources import DataSource


class WeightedSet:
    """
    A set in which members each have a weight, used for selecting at random.

    Usage:
        >>> ws = WeightedSet(('foo', 1.0), ('bar', 0.5))
        >>> ws.random()
        ('foo', 1.0)
    """

    def __init__(self, *weighted_members: tuple):
        self.members = []
        self.weights = []
        if weighted_members:
            self.members, self.weights = list(zip(*weighted_members))

    def random(self) -> str:
        return random.choices(self.members, self.weights)[0]

    def __add__(self, obj):
        ws = WeightedSet()
        ws.members = self.members + obj.members
        ws.weights = self.weights + obj.weights
        return ws

    def __str__(self):
        return f"{self.members}\n{self.weights}"


class DataSourceSet(WeightedSet):

    def __init__(self, source: Path):
        self.source = DataSource(source.read_text())
        self._populate()

    def _populate(self):
        super().__init__(*[(key, value) for key, value in self.source.frequencies.items()])

    def set_frequency(self, frequency: str):
        self.source.set_frequency(frequency)
        self._populate()

    def random(self):
        random_key = super().random()
        return self.source.as_dict()[random_key]


def equal_weights(terms: list, weight: float = 1.0, blank: bool = True) -> WeightedSet:
    ws = WeightedSet(*[(term, weight) for term in terms])
    if blank:
        ws = WeightedSet(("", 1.0)) + ws
    return ws
