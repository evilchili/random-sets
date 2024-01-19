import random
import yaml

from typing import IO


class UnknownFrequencyError(Exception):
    """
    Thrown when attempting to set a datasource's fequency without a frequency table in the metadat.
    """


class DataSource:
    """
    Represents a yaml data source used to generate roll tables.

    Attributes:

        source      - the IO source to parse
        frequency   - the frequency distribution to apply
        headers     - an array of header strings
        data        - The parsed YAML data

    Methods:

        load_source - Read and parse the source, populating the attributes

    """
    def __init__(self, source: IO, frequency: str = 'default') -> None:
        """
        Initialize a DataSource instance.

        Args:
            source      - an IO object to read source from
            frequency   - the name of the frequency distribution to use; must
                          be defined in the source file's metadata.
        """
        self.source = source
        self.frequency = frequency
        self.headers = []
        self.frequencies = None
        self.data = None
        self.metadata = None
        self.load_source()

    def load_source(self) -> None:
        """
        Cache the yaml source and the parsed or generated metadata.
        """
        if self.data:
            return
        self.read_source()
        self.init_headers()
        self.init_frequencies()

    def read_source(self) -> None:
        self.data = yaml.safe_load(self.source)
        self.metadata = self.data.pop('metadata', {})

    def init_headers(self) -> None:
        if 'headers' in self.metadata:
            self.headers = self.metadata['headers']

    def init_frequencies(self) -> None:
        num_keys = len(self.data.keys())
        default_freq = num_keys / 100

        frequencies = {
            'default': dict([(k, default_freq) for k in self.data.keys()])
        }
        if 'frequencies' in self.metadata:
            frequencies.update(**self.metadata['frequencies'])
        self.frequencies = frequencies[self.frequency]

    def set_frequency(self, frequency: str) -> None:
        """
        Select a new frequency distribution from the data source metadata.
        """
        if 'frequencies' not in self.metadata:
            raise UnknownFrequencyError(
                "Cannnot set a new frequency because there is no frequency table in the metadata."
            )
        if frequency not in self.metadata['frequencies']:
            raise UnknownFrequencyError(f"{frequency} is not present in the frequency table.")
        self.frequency = frequency
        self.init_frequencies()

    def random_frequencies(self, count: int = 1) -> list:
        """
        Choose random option names from the frequency table.
        """
        weights = []
        options = []
        for (option, weight) in self.frequencies.items():
            weights.append(weight)
            options.append(option)
        return random.choices(options, weights=weights, k=count)

    def random_values(self, count: int = 1) -> list:
        """
        Return a list of random values from the data set, as a list of lists.
        """
        return [
            self.get_entries(option, rand=True) for option in self.random_frequencies(count)
        ]

    def as_dict(self) -> dict:
        """
        Return the contents of the data source as a dict.
        """
        data = dict()
        for name in self.data.keys():
            entries = self.get_entries(name, rand=False)
            items = {(k, v) for k, v in zip(self.headers, entries)}
            data[name] = dict(items)
        return data

    def get_entries(self, option, rand: bool = False) -> list:
        """
        For a random item or each item in the specified option in the data source,
        return a flattened list of the option, the select item, and the item's value (if any).
        """

        # If there is no data for the specified option, stop now.
        flattened = [option]
        if not self.data[option]:
            flattened

        if hasattr(self.data[option], 'keys'):
            # if the option is a dict, we assume the values are lists; we select a random item
            # and prepend the key to the value list as our random selection. For example, given:
            #
            #  >>> self.data[option] == {'One': ['bar', 'baz'], 'Two': ['qaz', 'qux']}
            #
            # choices might then be: ['One', 'bar', 'baz']
            #
            if rand:
                k, v = random.choice(list(self.data[option].items()))
                choices = [[k] + v]
            else:
                choices = [
                    [k] + v for k, v in list(self.data[option].items())
                ]
        else:
            # If the option is either a list or a string, just select it.
            choices = self.data[option]

        for choice in choices:
            # If the randomly-selected choice is a dict, choose a random item and return a list consisting
            # of the option name, the key, and the value, flattening the # value if it is also a list.
            if hasattr(choice, 'keys'):
                for (k, v) in choice.items():
                    if type(v) is list:
                        flattened.append([option, k, *v])
                    else:
                        flattened.append([option, k, v])
                continue

            # if the member is a list, return the flattened list
            elif type(choice) is list:
                flattened.extend(choice)
                continue

            # otherwise, return a list consisting of option and choice
            flattened.append(choice)

        # Return all randomized values or just 1.
        if rand:
            return random.choice(flattened)
        return flattened
