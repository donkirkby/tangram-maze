from datetime import timedelta
from random import uniform
from textwrap import dedent

import pytest

from evo import Individual, IndividualGenerator, Population


class MutatingIndividual(Individual):
    def __init__(self, height: float):
        super().__init__()
        self.height = height

    def mutate(self) -> MutatingIndividual:
        min_change = -0.1
        max_change = 0.2
        return MutatingIndividual(self.height + uniform(min_change, max_change))


class MutatingGenerator(IndividualGenerator[MutatingIndividual]):
    def __init__(self, min_height: float = 0.0, max_height: float = 2.0):
        self.min_height = min_height
        self.max_height = max_height

    def generate_random(self) -> MutatingIndividual:
        return MutatingIndividual(height=uniform(self.min_height,
                                                 self.max_height))

    def calculate_score(self, individual: MutatingIndividual) -> float:
        return round(individual.height, 3)


class MatingIndividual(Individual):
    def __init__(self, height: float):
        super().__init__()
        self.height = height

    def mate(self, other: MatingIndividual) -> MatingIndividual:
        return MatingIndividual((self.height + other.height)/2)


class MatingGenerator(IndividualGenerator[MatingIndividual]):
    def __init__(self, min_height: float = 0.0, max_height: float = 2.0):
        self.min_height = min_height
        self.max_height = max_height

    def generate_random(self) -> MatingIndividual:
        return MatingIndividual(height=uniform(self.min_height,
                                               self.max_height))

    def calculate_score(self, individual: MatingIndividual) -> float:
        return round(individual.height, 3)



def test_init():
    min_height = 0.5
    max_height = 1.0
    generator = MutatingGenerator(min_height, max_height)
    population = Population(generator)

    top_individual = population.top_individual

    assert population.top_score == round(top_individual.height, 3)
    assert min_height <= top_individual.height <= max_height


def test_fill_pools():
    min_height = 0.5
    max_height = 1.0
    generator = MutatingGenerator(min_height, max_height)
    population = Population(
        generator,
        individual_count=103,
        pool_count=5)

    assert [len(pool) for pool in population.pools] == [2]

    population.fill_pools()

    assert [len(pool) for pool in population.pools] == [21, 20, 21, 20, 21]


@pytest.mark.parametrize(
    'params,expected_message_match',
    (pytest.param(dict(individual_count=0),
                  'Must have individual_count above zero.',
                  id='zero_individuals'),
     pytest.param(dict(pool_count=0),
                  'Must have pool_count above zero.',
                  id='zero_pools'),
     pytest.param(dict(mating_rate=1.1),
                  'Must have mating_rate between 0 and 1.',
                  id='high_mating'),
     pytest.param(dict(mating_rate=-0.1),
                  'Must have mating_rate between 0 and 1.',
                  id='low_mating'),
     pytest.param(dict(mutation_rate=1.1),
                  'Must have mutation_rate between 0 and 1.',
                  id='high_mutation'),
     pytest.param(dict(mutation_rate=-0.1),
                  'Must have mutation_rate between 0 and 1.',
                  id='low_mutation'),
     pytest.param(dict(mutation_rate=0, mating_rate=0),
                  'Must have mutation_rate or mating_rate '
                  'above zero.',
                  id='zero_rates'),
     pytest.param(dict(individual_count=0),
                  'Must have individual_count above zero.',
                  id='zero_individuals'),
     ))
def test_bad_init(params: dict, expected_message_match: str):
    generator = MutatingGenerator()
    with pytest.raises(ValueError, match=expected_message_match):
        Population(generator, **params)


def test_unsupported_mating():
    generator = MutatingGenerator()
    with pytest.raises(ValueError,
                       match='Individual could not mate, but mating_rate is '
                             'not zero.'):
        Population(generator, mating_rate=0.1)


def test_unsupported_mutating():
    generator = MatingGenerator()
    with pytest.raises(ValueError,
                       match='Individual could not mutate, but mutation_rate '
                             'is not zero.'):
        Population(generator, mutation_rate=0.1)


def test_sort_pools():
    min_height = 0.5
    max_height = 1.0
    generator = MutatingGenerator(min_height, max_height)
    population = Population(
        generator,
        pool_count=2)

    assert [len(pool) for pool in population.pools] == [2]

    population.fill_pools()
    population.sort_pools()

    first_pool_first_individual = population.pools[0][0]
    first_pool_last_individual = population.pools[0][-1]
    second_pool_first_individual = population.pools[1][0]

    assert first_pool_last_individual.score < first_pool_first_individual.score
    assert first_pool_last_individual.score < second_pool_first_individual.score

    assert population.top_score == max(first_pool_first_individual.score,
                                       second_pool_first_individual.score)
    assert population.top_individual in (first_pool_first_individual,
                                         second_pool_first_individual)


def test_mutate_pools():
    min_height = 0.5
    max_height = 1.0
    generator = MutatingGenerator(min_height, max_height)
    population = Population(
        generator,
        individual_count=100,
        pool_count=2,
        mutation_rate=0.7)

    assert [len(pool) for pool in population.pools] == [2]

    population.fill_pools()
    population.sort_pools()
    population.mutate_pools()

    pool_sizes = [len(pool) for pool in population.pools]
    assert pool_sizes == [85, 85]

    assert population.pools[0][-1].score is None


def test_mate_pools():
    min_height = 0.5
    max_height = 1.0
    generator = MatingGenerator(min_height, max_height)
    population = Population(
        generator,
        individual_count=100,
        pool_count=2,
        mutation_rate=0,
        mating_rate=0.7)

    assert [len(pool) for pool in population.pools] == [3]

    population.fill_pools()
    population.sort_pools()
    population.mate_pools()

    pool_sizes = [len(pool) for pool in population.pools]
    assert pool_sizes == [67, 67]

    assert population.pools[0][-1].score is None


def test_run_epoch():
    min_height = 0.5
    max_height = 1.0
    generator = MutatingGenerator(min_height, max_height)
    population = Population(
        generator,
        individual_count=100,
        pool_count=2,
        mutation_rate=0.7)

    assert [len(pool) for pool in population.pools] == [2]

    top_score1 = population.top_score
    population.run_epoch()

    top_score2 = population.top_score
    population.run_epoch()

    top_score3 = population.top_score

    assert [len(pool) for pool in population.pools] == [50, 50]

    assert top_score1 < top_score2 < top_score3


def test_run_epoch_limit():
    generator = MutatingGenerator()
    population = Population(
        generator,
        individual_count=100,
        mutation_rate=0.1,
        epoch_limit=10)

    top_score1 = population.top_score

    population.run_epochs()

    top_score2 = population.top_score
    assert top_score1 < top_score2


def test_run_time_limit():
    generator = MutatingGenerator()
    population = Population(
        generator,
        individual_count=100,
        mutation_rate=0.1,
        time_limit=timedelta(seconds=1))

    top_score1 = population.top_score

    population.run_epochs()

    top_score2 = population.top_score
    assert top_score1 < top_score2


def test_run_score_limit():
    generator = MutatingGenerator(min_height=0.5, max_height=1.0)
    score_limit = 1.5
    population = Population(
        generator,
        individual_count=100,
        mutation_rate=0.1,
        score_limit=score_limit)

    top_score1 = population.top_score

    population.run_epochs()

    top_score2 = population.top_score
    assert top_score1 < score_limit <= top_score2


def test_run_epoch_logging(capsys):
    generator = MatingGenerator(min_height=1.25, max_height=1.25)
    population = Population(
        generator,
        individual_count=100,
        pool_count=2,
        mutation_rate=0,
        mating_rate=0.1,
        epoch_limit=10,
        is_logging=True)

    population.run_epochs()

    expected_log = dedent("""\
        Pool scores after 1 epoch: 1.25, 1.25
        Pool scores after 2 epochs: 1.25, 1.25
        Pool scores after 3 epochs: 1.25, 1.25
        Pool scores after 4 epochs: 1.25, 1.25
        Pool scores after 5 epochs: 1.25, 1.25
        Pool scores after 6 epochs: 1.25, 1.25
        Pool scores after 7 epochs: 1.25, 1.25
        Pool scores after 8 epochs: 1.25, 1.25
        Pool scores after 9 epochs: 1.25, 1.25
        Pool scores after 10 epochs: 1.25, 1.25
        """)

    captured = capsys.readouterr()
    assert captured.out == expected_log
