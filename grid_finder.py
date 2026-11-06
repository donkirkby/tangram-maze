import os.path
import re
import string
from functools import cache
from pathlib import Path
from random import choice, randrange

import math

from networkx import grid_2d_graph, all_simple_paths

from evo import Individual, IndividualGenerator, Population


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
                 word_list: list[tuple[str, int]] | None = None):
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
            self.word_weights = {word: weight
                                 for word, weight in word_list}
            self.max_length = max(len(word)
                                  for word, weight in self.word_weights.items())
        else:
            self.word_weights = {}
            self.max_length = 9

    def generate_random(self) -> WordGrid:
        rows = [[choice(string.ascii_uppercase) for _ in range(self.width)]
                for _ in range(self.height)]
        rows[self.start_pos[1]][self.start_pos[0]] = WordGrid.START
        rows[self.finish_pos[1]][self.finish_pos[0]] = WordGrid.FINISH
        return WordGrid(rows)

    def calculate_score(self, individual: WordGrid) -> float:
        all_words = self.find_words(individual)
        word_paths = list[str]()
        solution_path = ''
        score = 0
        for word, weight, path in all_words:
            score += weight
            if word == self.solution:
                score += 10_000
                solution_path = path
            else:
                word_paths.append(path)
        if solution_path:
            for word_path in word_paths:
                overlap = len(os.path.commonprefix((word_path,
                                                    solution_path))) // 2
                score += 100 * overlap
        return score

    def find_words(self, grid: WordGrid) -> set[tuple[str, int, str]]:
        """ Search for words in the grid.

        :return: [(word, weight, path)] where the path is a string of positions,
        formatted as a hexadecimal string: xyxyxyxy
        """
        paths = find_all_paths(self.width,
                               self.height,
                               self.start_pos,
                               self.finish_pos,
                               self.max_length)
        found_words = set[tuple[str, int, str]]()
        for path in paths:
            rows = grid.rows
            letters = [rows[y][x] for x, y in path]
            word = ''.join(letters)
            word_weight = self.word_weights.get(word)
            if word_weight:
                path_text = ''.join(f'{x:x}{y:x}' for x, y in path)
                found_words.add((word, word_weight, path_text))
        return found_words


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


def main():
    max_length = 9
    path = Path('/etc/dictionaries-common/words')
    with path.open() as f:
        all_words = (word.strip() for word in f)
        length_words = (word.upper()
                        for word in all_words
                        if len(word) <= max_length)
        plain_words = (word
                       for word in length_words
                       if re.match('^[A-Z]+$', word))
        word_list = [(word, len(word)) for word in plain_words]
    generator = WordGridGenerator(5,
                                  5,
                                  start_pos=(2, 1),
                                  finish_pos=(2, 3),
                                  solution='START',
                                  word_list=word_list)
    population = Population(generator,
                            individual_count=100,
                            epoch_limit=100,
                            mutation_rate=0.2,
                            is_logging=True)
    population.run_epochs()
    print(population.top_individual.display())
    print(generator.find_words(population.top_individual))


if __name__ in ('__main__', '__live_coding__'):
    main()
