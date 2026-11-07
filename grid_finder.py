import csv
import os.path
import re
import string
from dataclasses import dataclass, replace
from functools import cache
from operator import attrgetter, itemgetter
from os.path import commonprefix
from pathlib import Path
from random import choice, randrange

import math
from textwrap import dedent

from networkx import grid_2d_graph, all_simple_paths

from evo import Individual, IndividualGenerator, Population


@dataclass
class FoundWord:
    word: str
    score: float
    path: str | None = None


class WordGrid(Individual):
    START = 'start'
    FINISH = 'finish'

    word_list = list[str]()

    def __init__(self, rows: list[list[str]] | str):
        super().__init__()
        if isinstance(rows, str):
            replacements = {
                self.START[0]: self.START,
                self.FINISH[0]: self.FINISH
            }
            lines = rows.splitlines()
            self.rows = [[replacements.get(c, c) for c in line]
                         for line in lines]
        else:
            self.rows = rows

    def __repr__(self):
        return f'WordGrid({self.display() !r})'

    def display(self) -> str:
        return '\n'.join(''.join(c[0] for c in row)
                         for row in self.rows)

    def mutate(self) -> WordGrid:
        width = len(self.rows[0])
        height = len(self.rows)
        new_rows = [row[:] for row in self.rows]
        mutation_count = math.ceil(width * height * 0.04)
        while mutation_count:
            i = randrange(height)
            j = randrange(width)
            target = new_rows[i][j]
            if target != target.upper():
                continue

            new_rows[i][j] = choice(string.ascii_uppercase)
            mutation_count -= 1
        return WordGrid(new_rows)


class WordGridGenerator(IndividualGenerator[WordGrid]):
    def __init__(self,
                 width: int,
                 height: int,
                 start_pos: tuple[int, int],
                 finish_pos: tuple[int, int],
                 solution: str = '',
                 word_list: list[FoundWord] | None = None,
                 is_logging: bool = False):
        """ Initialize a WordGridGenerator object.

        :param width: The number of letters in each row.
        :param height: The number of rows in the grid.
        :param start_pos: The starting position in the grid (x, y) where top
        left is (0, 0).
        :param finish_pos: The finish position in the grid.
        :param solution: The solution word that must be in the grid. It will
        also increase scores for words that have a common prefix with the
        solution.
        :param word_list: The list of words to search for in the grid, as well
        as a weight for each word. More common words should have higher weight.
        If it's None, then you can't calculate scores.
        :param is_logging: True if it should log scoring details.
        """
        super().__init__()
        if not 0 < width <= 16:
            raise ValueError('width must be between 0 and 16')
        if not 0 < height <= 16:
            raise ValueError('height must be between 0 and 16')
        self.width = width
        self.height = height
        self.start_pos = start_pos
        self.finish_pos = finish_pos
        self.solution = solution
        if word_list is not None:
            self.word_map = {word.word: word for word in word_list}
            self.max_length = max(len(word.word) for word in word_list)
        else:
            self.word_map = {}
            self.max_length = 9
        self.is_logging = is_logging
        if solution and solution not in self.word_map:
            raise ValueError(f'Solution {solution!r} not found in word_list.')

    def generate_random(self) -> WordGrid:
        rows = [[choice(string.ascii_uppercase) for _ in range(self.width)]
                for _ in range(self.height)]
        rows[self.start_pos[1]][self.start_pos[0]] = WordGrid.START
        rows[self.finish_pos[1]][self.finish_pos[0]] = WordGrid.FINISH
        return WordGrid(rows)

    def calculate_score(self, individual: WordGrid) -> float:
        all_words = self.find_words(individual)
        return sum(word.score for word in all_words)

    def find_words(self, grid: WordGrid) -> list[FoundWord]:
        """ Search for words in the grid.

        :return: [(word, weight, path)] where the path is a string of positions,
        formatted as a hexadecimal string: xyxyxyxy
        """
        paths = find_all_paths(self.width,
                               self.height,
                               self.start_pos,
                               self.finish_pos,
                               self.max_length)
        found_words = list[FoundWord]()
        used_squares = set[str]()
        for path in paths:
            rows = grid.rows
            letters = [rows[y][x] for x, y in path]
            word = ''.join(letters)
            word_info: FoundWord | None = self.word_map.get(word)
            if word_info:
                word_squares = [f'{x:x}{y:x}' for x, y in path]
                used_squares.update(word_squares)
                path_text = ''.join(word_squares)
                new_info = replace(word_info, path=path_text)
                found_words.append(new_info)
        solution = self.solution
        found_solution: FoundWord | None = None
        for word in found_words:
            word_path = word.path
            assert word_path is not None
            if word.word == solution:
                found_solution = word
        if found_solution is not None:
            found_solution.score += 10_000 + 10 * len(used_squares)
            if self.is_logging:
                all_squares = {f'{x:x}{y:x}'
                               for x in range(self.width)
                               for y in range(self.height)}
                unused_squares = all_squares - used_squares
                unused_squares.discard(f'{self.start_pos[0]}{self.start_pos[1]}')
                unused_squares.discard(f'{self.finish_pos[0]}{self.finish_pos[1]}')
                print(f'Used squares: {len(used_squares)}')
                print(f'Unused squares: {sorted(unused_squares)}')

            solution_path = found_solution.path
            assert solution_path is not None
            for word in found_words:
                if word is found_solution:
                    continue
                word_path = word.path
                assert word_path is not None
                overlap = len(os.path.commonprefix((word_path,
                                                    solution_path))) // 2
                word.score += 100 * overlap
        else:
            for word in found_words:
                word_length = len(word.word)
                for i in range(word_length, word_length//2, -1):
                    word_start = word.word[:i]
                    if solution.startswith(word_start):
                        word.score += len(word_start)
                        break
                    word_end = word.word[-i:]
                    if solution.endswith(word_end):
                        word.score += len(word_end)
                        break
        word_infos = dict[str, FoundWord]()
        for word_info2 in found_words:
            duplicate = word_infos.get(word_info2.word)
            if duplicate is not None and duplicate.score >= word_info2.score:
                continue
            word_infos[word_info2.word] = word_info2

        result = list(word_infos.values())
        if self.is_logging:
            score = sum(word.score for word in result)
            print(f'Score: {score}')

        return result


@cache
def find_all_paths(width: int,
                   height: int,
                   start_pos: tuple[int, int],
                   finish_pos: tuple[int, int],
                   max_length: int = 9) -> list[list[tuple[int, int]]]:
    paths = []
    graph = grid_2d_graph(width, height)
    for x in range(width-1):
        for y in range(height-1):
            graph.add_edge((x, y), (x+1, y+1))
            graph.add_edge((x, y+1), (x+1, y))
    for nodes in all_simple_paths(graph, start_pos, finish_pos, max_length+2):
        letter_nodes = nodes[1:-1]
        paths.append(letter_nodes)

    return paths


def load_dictionary(dictionary_path: Path, max_length: int) -> list[FoundWord]:
    with dictionary_path.open() as f:
        all_words = (word.strip() for word in f)
        length_words = (word.upper()
                        for word in all_words
                        if len(word) <= max_length)
        plain_words = (word
                       for word in length_words
                       if re.match('^[A-Z]+$', word))
        word_list = [FoundWord(word, len(word)) for word in plain_words]
    return word_list


def load_ngrams(ngrams_path: Path, max_length: int) -> list[FoundWord]:
    with ngrams_path.open() as f:
        row_reader = csv.reader(f)
        next(row_reader)  # skip headers
        all_words = ((word.strip(), int(lower_count))
                     for word, lower_count, total_count in row_reader)
        length_words = ((word.upper(), lower_count)
                        for word, lower_count in all_words
                        if len(word) <= max_length)
        plain_words = [(word, lower_count)
                       for word, lower_count in length_words
                       if re.match('^[A-Z]+$', word)]
        total_count = sum(lower_count for word, lower_count in plain_words)
        weighted_words = (FoundWord(word, lower_count/total_count)
                          for word, lower_count in plain_words)
        common_words = [word
                        for word in weighted_words
                        if word.score > 0.000001]
    return common_words


def find_branches(test_solution: str, word_list: list[FoundWord]):
    # target = 0.000005
    # r = [word.word for word in word_list if target * 0.99 < word.score < target * 1.01]
    # n = len(r)
    min_length = len(test_solution) // 2
    branches = [(len(commonprefix((test_solution, word.word))), word)
                for word in word_list
                if len(commonprefix((test_solution, word.word))) >= min_length]
    branches.sort(key=itemgetter(0), reverse=True)
    branch_words = [word.word for length, word in branches]
    print(branch_words)
    exit(0)


def main():
    max_length = 9
    ngrams_path = Path(__file__).parent.parent / 'ludiverbia/src/rawWords.csv'
    dictionary_path = Path('/etc/dictionaries-common/words')
    if ngrams_path.exists():
        word_list = load_ngrams(ngrams_path, max_length)
    elif dictionary_path.exists():
        word_list = load_dictionary(dictionary_path, max_length)
    else:
        raise FileNotFoundError('No word files found.')

    # find_branches('ABCDE', word_list)

    generator = WordGridGenerator(5,
                                  5,
                                  start_pos=(2, 1),
                                  finish_pos=(2, 3),
                                  solution='START',
                                  word_list=word_list,
                                  is_logging=False)
    population = Population(generator,
                            individual_count=500,
                            epoch_limit=100,
                            mutation_rate=0.2,
                            is_logging=True)
    population.run_epochs()
    top_individual = population.top_individual
    # DAELA
    # EKsEK
    # RSTSI
    # TAfSH
    # GERTO

    print(top_individual.display())
    words = generator.find_words(top_individual)
    words.sort(key=attrgetter('score'), reverse=True)
    print([(word.word, word.score) for word in words])


if __name__ in ('__main__', '__live_coding__'):
    main()
