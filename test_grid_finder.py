from textwrap import dedent

from grid_finder import WordGridGenerator, WordGrid


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


def test_count_words():
    grid = WordGrid(dedent("""\
        Bs
        AD
        Nf
        """))
    generator = WordGridGenerator(2,
                                  3,
                                  (1, 0),
                                  (1, 2),
                                  'BAN',
                                  [
                                      ('A', 1),
                                      ('BA', 1),
                                      ('BAD', 1),
                                      ('BAN', 1),
                                      ('BAND', 1),
                                      ('AD', 1),
                                      ('AND', 1),
                                      ('WAX', 1),
                                      ('BANANA', 1)
                                   ])

    found_words = generator.find_words(grid)
    stripped_words = {word for word, weight, path in found_words}
    assert stripped_words == {'A', 'BA', 'BAD', 'BAN', 'BAND', 'AD', 'AND'}

    score = generator.calculate_score(grid)
    assert score == (10_000 +  # solution found
                     7*100 +  # common prefix lengths
                     7)  # sum of weights
