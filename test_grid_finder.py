from textwrap import dedent

import pytest

from grid_finder import WordGridGenerator, WordGrid, FoundWord


def test_generate_random():
    generator = WordGridGenerator(5,
                                  5,
                                  (2, 1),
                                  (2, 3))
    for _ in range(100):
        grid = generator.generate_random()
        assert grid.rows[1][2] == WordGrid.START
        assert grid.rows[3][2] == WordGrid.FINISH


def test_mutate():
    generator = WordGridGenerator(5,
                                  5,
                                  (2, 1),
                                  (2, 3))
    grid = generator.generate_random()
    for _ in range(100):
        grid2 = grid.mutate()
        assert grid2.rows[1][2] == WordGrid.START
        assert grid2.rows[3][2] == WordGrid.FINISH


def test_repr():
    grid_text = 'AAAAA\nBBsBB\nCCCCC\nDDDfD\nEEEEE'
    grid = WordGrid(grid_text)

    assert grid.rows[0][0] == 'A'
    assert grid.rows[1][0] == 'B'
    assert grid.rows[1][2] == WordGrid.START
    assert grid.rows[3][3] == WordGrid.FINISH

    assert repr(grid) == r"WordGrid('AAAAA\nBBsBB\nCCCCC\nDDDfD\nEEEEE')"


def test_bad_solution():
    word_list = [FoundWord(word, len(word))
                 for word in 'A BA BAD BAN BAND AD AND WAX BANANA'.split()]
    with pytest.raises(ValueError, match=r"Solution 'BRN' not found in word_list\."):
        WordGridGenerator(2,
                          3,
                          (1, 0),
                          (1, 2),
                          'BRN',
                          word_list)


def test_count_words():
    grid = WordGrid(dedent("""\
        Bs
        AD
        Nf
        """))
    word_list = [FoundWord(word, len(word))
                 for word in 'A BA BAD BAN BAND AD AND WAX BANANA'.split()]
    generator = WordGridGenerator(2,
                                  3,
                                  (1, 0),
                                  (1, 2),
                                  'BAN',
                                  word_list)

    found_words = generator.find_words(grid)
    word_scores = {word.word: word.score for word in found_words}
    assert word_scores == {'A': 1,
                           'BA': 2 + 200,  # Common prefix
                           'BAD': 3 + 200,
                           'BAN': 3 + 10_000 + 40,  # Solution + used squares
                           'BAND': 4 + 300,
                           'AD': 2,
                           'AND': 3}

    score = generator.calculate_score(grid)
    assert score == sum(word_scores.values())


def test_partial_solution():
    grid = WordGrid(dedent("""\
        BsH
        AIN
        NfK
        """))
    word_list = [FoundWord(word, len(word)/10)
                 for word in 'A BA BAD BAN BAND BANK AD AN INK AND WAX BANANA'.split()]
    generator = WordGridGenerator(3,
                                  3,
                                  (1, 0),
                                  (1, 2),
                                  'BANK',
                                  word_list)

    found_words = generator.find_words(grid)
    word_scores = {word.word: word.score for word in found_words}
    assert word_scores == {'A': 0.1,
                           'AN': 0.2,
                           'BA': 2.2,
                           'BAN': 3.3,  # Common start
                           'INK': 2.3}  # Common end


def test_count_words_duplicates():
    grid = WordGrid(dedent("""\
        BsC
        ADB
        NfA
        """))
    word_list = [FoundWord(word, len(word))
                 for word in 'BA BAN'.split()]
    generator = WordGridGenerator(3,
                                  3,
                                  (1, 0),
                                  (1, 2),
                                  'BAN',
                                  word_list)

    found_words = generator.find_words(grid)
    word_list = sorted(word.word for word in found_words)
    assert word_list == ['BA', 'BAN']

    word_scores = {word.word: word.score for word in found_words}
    assert word_scores == {'BA': 2 + 200,  # Common prefix
                           'BAN': 3 + 10_000 + 50}  # Solution + used squares

    score = generator.calculate_score(grid)
    assert score == sum(word_scores.values())
