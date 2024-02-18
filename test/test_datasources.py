from io import StringIO

from random_sets import datasources

fixture_metadata = """
metadata:
  headers:
    - Header 1
    - Header 2
    - Header 3
  die: 10
  frequencies:
    default:
      Option 1: 0.3
      Option 2: 0.5
      Option 3: 0.2
    nondefault:
      Option 1: 0.0
      Option 2: 0.1
      Option 3: 0.9
"""

fixture_source = """
Option 1:
    - choice 1: description 1
    - choice 2: description 2
    - choice 3: description 3
Option 2:
    - choice 1: description 4
    - choice 2: description 5
    - choice 3: description 6
Option 3:
    - choice 1: description 7
    - choice 2: description 8
    - choice 3: description 9
"""


def test_datasource_random_values():
    fixture = StringIO(fixture_metadata + fixture_source)
    ds = datasources.DataSource(fixture)
    randvals = ds.random_values(count=2)

    # we asked for two random values
    assert len(randvals) == 2

    # each value has an "Option", a "choice", and a "description"
    assert len(randvals[0]) == 3


def test_zero_frequency():
    fixture = StringIO(fixture_metadata + fixture_source)
    ds = datasources.DataSource(fixture)
    ds.set_frequency('nondefault')
    for val in ds.random_values(count=100):
        assert 'Option 1' not in val


def test_distribution_accuracy_to_one_decimal_place():
    fixture = StringIO(fixture_metadata + fixture_source)
    ds = datasources.DataSource(fixture)
    ds.set_frequency('nondefault')
    counts = {
        'Option 1': 0,
        'Option 2': 0,
        'Option 3': 0,
    }

    population = 10000

    for val in ds.random_values(count=population):
        counts[val[0]] += 1

    for (option, count) in counts.items():
        observed = count/population
        assert round(observed, 1) == round(ds.frequencies[option], 1)
