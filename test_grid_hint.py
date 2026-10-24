import svgwrite
from space_tracer import LiveImageDiffer

from grid_hint import GridHint
from tan import Tan
from tangram import Tangram
from test_single_hint import create_square
from test_tan import LiveSvg


# noinspection DuplicatedCode
def test_draw(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    tangram1 = Tangram(scale=100, gap=3)
    tangram2 = Tangram(scale=100, gap=3)
    create_square(tangram2)

    tangram1.t4a.draw(expected)
    tangram2.t1a.draw(expected)
    tangram2.t1b.draw(expected)

    display = Tan(copy=tangram1.t1a.display)
    display.rotate(90)
    display.anchor(tangram2.p.display, 1, 1)
    display.draw(expected)
    display.rotate(180)
    display.anchor(tangram2.p.display, 3, 1)
    display.draw(expected)
    tangram1.t1a.rotate(90)
    tangram1.t1a.anchor(tangram1.t4a, 2, 1)

    tangram1.t1b.rotate(-90)
    tangram1.t1b.anchor(tangram1.t1a, 2, 0)
    # tangram1.t1b.draw(expected)
    # tangram1.t1a.draw(expected)

    tangram1.t1a.anchor(tangram1.t1b, 1, 0)
    tangram1.t1a.draw(expected)

    tangram1.t1a.rotate(90)
    tangram1.t1a.draw(expected)

    tangram1.t1a.rotate(90)
    tangram1.t1a.draw(expected)

    tangram1.t1b.rotate(180)
    tangram1.t1b.anchor(tangram1.t1a, 2, 1)
    tangram1.t1b.draw(expected)

    tangram1.t1a.rotate(-90)
    tangram1.t1a.anchor(tangram1.t1b)
    # tangram1.t1a.draw(expected)

    tangram1.t1a.rotate(90)
    tangram1.t1a.draw(expected)

    tangram1.t1b.rotate(-90)
    tangram1.t1b.anchor(tangram1.t1a)
    tangram1.t1b.draw(expected)

    tangram1.t1b.rotate(180)
    tangram1.t1b.anchor(tangram1.t1a, 2, 2)
    tangram1.t1b.draw(expected)

    tangram1.t1b.rotate(90)
    tangram1.t1b.anchor(tangram1.t1a, 2, 1)
    tangram1.t1b.draw(expected)

    actual = svgwrite.Drawing(size=(200, 200))
    tangram3 = GridHint(scale=100, gap=3, highlight='t4a')
    create_square(tangram3)
    # tangram3.remove(tangram3.p)
    tangram3.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)
