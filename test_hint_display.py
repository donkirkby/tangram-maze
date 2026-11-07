import svgwrite
from space_tracer import LiveImageDiffer
from svgwrite.container import Group

from hint_display import HintDisplay
from tangram import Tangram
from test_tan import LiveSvg


def create_square(tangram: Tangram) -> None:
    tangram.add(tangram.t4a)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(-90)
    tangram.add(tangram.p)
    tangram.p.rotate(90)
    tangram.p.anchor(tangram.t4a, 2, 1)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t4a, 0, 2)
    tangram.add(tangram.t2)
    tangram.t2.rotate(-45)
    tangram.t2.anchor(tangram.p, 2, 2)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(90)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(180)
    tangram.t1b.anchor(tangram.s, 1)

# noinspection DuplicatedCode
def test_draw(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(141, 171))
    tangram1 = Tangram(scale=100, gap=0)
    create_square(tangram1)

    tangram1.draw(expected)
    expected_font_size = 10
    expected.add(expected.text(f'^N',
                               (141, 10),
                               font_family='Raleway',
                               font_size=expected_font_size,
                               text_anchor='end'))
    expected.add(expected.text(f'This Solution: 99, Next Hints: 108, 12',
                               (0, 171),
                               font_family='Raleway',
                               font_size=expected_font_size))

    tangram2 = Tangram(scale=1)
    create_square(tangram2)
    tangram2.translate(10, 20)  # Force it to centre on the page.
    display = HintDisplay(tangram2, solution=99, hint1=108, hint2=12, scale=100)
    actual = svgwrite.Drawing(size=(display.width, display.height))
    display.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)

# noinspection DuplicatedCode
def test_landscape(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(171, 283))
    tangram1 = Tangram(scale=100)
    create_square(tangram1)
    tangram1.t4a.translate(tangram1.width, 0)
    tangram1.translate(-15, 56)

    g = Group()
    expected.add(g)
    tangram1.draw(expected)
    g.add(expected.elements.pop())
    g['transform'] = 'translate(171, 0) rotate(90)'
    expected_font_size = 10
    g.add(expected.text(f'^N',
                        (283, 10),
                        font_family='Raleway',
                        font_size=expected_font_size,
                        text_anchor='end'))
    g.add(expected.text(f'This Solution: 99, Next Hints: 108, 12',
                        (0, 171),
                        font_family='Raleway',
                        font_size=expected_font_size))

    tangram2 = Tangram(scale=1)
    create_square(tangram2)
    tangram2.t4a.translate(tangram2.width, 0)
    tangram2.translate(-30, -20)  # Force it to centre on the page.
    display = HintDisplay(tangram2, solution=99, hint1=108, hint2=12, scale=100)
    actual = svgwrite.Drawing(size=(display.width, display.height))
    display.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)
