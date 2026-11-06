import typing
from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from itertools import batched
from operator import attrgetter
from random import shuffle

T = typing.TypeVar('T', bound='Individual')


class Individual:
    """ Base class for individuals in an evolutionary search population.

    The only common feature is a score: highest scores survive.
    """
    def __init__(self):
        self.score: float | None = None

    def __repr__(self):
        return f'{type(self).__name__}({self.score})'

    def mutate(self: T) -> T | None:
        """ Make small changes to the attributes.

        :return: A new individual with mutated attributes. If mutation is not
        supported, return None. However, make sure that the population uses a
        mutation rate of zero in that case.
        """

    def mate(self, other: T) -> T | None:
        """ Mix attributes with another individual.

        :return: A new individual with mixed attributes. If mating is not
        supported, return None. However, make sure that the population uses
        a mating rate of zero in that case."""


class IndividualGenerator(typing.Generic[T], ABC):
    @abstractmethod
    def generate_random(self) -> T:
        """ Create an individual with random values. """

    @abstractmethod
    def calculate_score(self, individual: T) -> float:
        """ Calculate the score, based on attributes. """


class Population(typing.Generic[T]):
    def __init__(self,
                 individual_generator: IndividualGenerator[T],
                 individual_count: int = 1000,
                 pool_count: int = 1,
                 mutation_rate: float = 1.0,
                 mating_rate: float = 0.0,
                 epoch_limit: int | None = None,
                 time_limit: timedelta | None = None,
                 score_limit: float | None = None,
                 is_logging: bool = False) -> None:
        """ Initialize the population and set end conditions.

        :param individual_generator: Generates random individuals for new pools.
        :param individual_count: The total number of individuals across all
        pools.
        :param pool_count: The number of pools. Score comparison and mating only
        happen within a pool. When pools stop improving, the one with the lowest
        top score gets reset.
        :param mutation_rate: The portion of the population that gets mutated
        during each epoch. The top-scoring portion of the population will be
        mutated.
        :param mating_rate: The portion of the population that gets mated during
        each epoch. The top-scoring portion of the population will be selected,
        then shuffled and paired off.
        :param epoch_limit: If not None, then the run will stop after this many
        epochs.
        :param time_limit: If not None, then the run will stop after this much
        time.
        :param score_limit: If not None, then the run will stop when the top
        score is equal to or higher than this.
        :param is_logging: True, if it should print a score summary after each
        epoch."""
        self.individual_generator = individual_generator
        if individual_count <= 0:
            raise ValueError('Must have individual_count above zero.')
        if pool_count <= 0:
            raise ValueError('Must have pool_count above zero.')

        self.individual_count = individual_count
        self.pool_count = pool_count

        if not 0.0 <= mutation_rate <= 1.0:
            raise ValueError('Must have mutation_rate between 0 and 1.')
        if not 0.0 <= mating_rate <= 1.0:
            raise ValueError('Must have mating_rate between 0 and 1.')
        if mutation_rate + mating_rate == 0.0:
            raise ValueError('Must have mutation_rate or mating_rate above zero.')

        self.mutation_rate = mutation_rate
        self.mating_rate = mating_rate
        self.epochs_limit = epoch_limit
        self.time_limit = time_limit
        if time_limit is not None:
            self.end_time = datetime.now() + time_limit
        else:
            self.end_time = None
        self.score_limit = score_limit
        self.is_logging = is_logging

        individual1 = self.individual_generator.generate_random()
        self.top_individual = individual1
        self.top_score = individual_generator.calculate_score(individual1)
        self.pools = [[individual1]]
        if mutation_rate > 0.0:
            individual2 = individual1.mutate()
            if individual2 is None:
                raise ValueError('Individual could not mutate, but '
                                 'mutation_rate is not zero.')

            self.pools[0].append(individual2)

        if mating_rate > 0.0:
            individual3 = self.individual_generator.generate_random()
            individual4 = individual1.mate(individual3)
            if individual4 is None:
                raise ValueError('Individual could not mate, but mating_rate '
                                 'is not zero.')

            self.pools[0].append(individual3)
            self.pools[0].append(individual4)

        remaining_individuals = individual_count
        remaining_pools = pool_count
        self.pool_sizes: list[int] = []
        while remaining_pools:
            pool_size = round(remaining_individuals / remaining_pools)
            self.pool_sizes.append(pool_size)
            remaining_individuals -= pool_size
            remaining_pools -= 1

    def fill_pools(self) -> None:
        while len(self.pools) < self.pool_count:
            self.pools.append([self.individual_generator.generate_random()])
        for pool, pool_size in zip(self.pools, self.pool_sizes):
            while len(pool) < pool_size:
                pool.append(self.individual_generator.generate_random())

    def sort_pools(self) -> None:
        unscored = (individual
                    for pool in self.pools
                    for individual in pool
                    if individual.score is None)
        generator = self.individual_generator
        for individual in unscored:
            individual.score = generator.calculate_score(individual)
        for pool in self.pools:
            pool.sort(key=attrgetter('score'), reverse=True)
            pool_top = pool[0]
            if self.top_score < pool_top.score:
                self.top_individual = pool_top
                self.top_score = pool_top.score

    def mutate_pools(self) -> None:
        for pool in self.pools:
            mutation_count = round(self.mutation_rate * len(pool))
            for old_individual in pool[:mutation_count]:
                new_individual = old_individual.mutate()
                assert new_individual is not None
                pool.append(new_individual)

    def mate_pools(self) -> None:
        for pool in self.pools:
            mating_count = round(self.mating_rate * len(pool))
            mating_count -= mating_count % 2  # Force even number.
            parents = pool[:mating_count]
            shuffle(parents)
            for parent1, parent2 in batched(parents, 2):
                child = parent1.mate(parent2)
                assert child is not None
                pool.append(child)

    def cull_pools(self) -> None:
        for i, (pool, pool_size) in enumerate(
                zip(self.pools, self.pool_sizes)):
            pool = pool[:pool_size]
            self.pools[i] = pool

    def run_epoch(self):
        """ Run one epoch. """
        self.fill_pools()
        self.sort_pools()
        self.mate_pools()
        self.sort_pools()
        self.mutate_pools()
        self.sort_pools()
        self.cull_pools()

    def run_epochs(self) -> None:
        epoch_count = 0
        end_epoch = self.epochs_limit
        if self.time_limit is not None:
            end_time = datetime.now() + self.time_limit
        else:
            end_time = None
        end_score = self.score_limit

        while True:
            self.run_epoch()

            epoch_count += 1
            if self.is_logging:
                pool_scores = [str(pool[0].score) for pool in self.pools]
                plural = 's' if epoch_count > 1 else ''
                print(f'Pool scores after {epoch_count} epoch{plural}: '
                      f'{", ".join(pool_scores)}')
            if end_epoch is not None and end_epoch <= epoch_count:
                break
            if end_time is not None and end_time < datetime.now():
                break
            if end_score is not None and end_score <= self.top_score:
                break
