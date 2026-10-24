import svgwrite
from space_tracer import LiveImageDiffer

from single_hint import SingleHint
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
    expected = svgwrite.Drawing(size=(200, 200))
    tangram1 = Tangram(scale=100, gap=0)
    tangram2 = Tangram(scale=100, gap=3)
    create_square(tangram1)
    tangram2.add(tangram2.t4a)
    tangram1.remove(tangram1.t4a)

    tangram1.draw(expected)
    tangram2.draw(expected)

    actual = svgwrite.Drawing(size=(200, 200))
    tangram3 = SingleHint(scale=100, gap=3, highlight='t4a')
    create_square(tangram3)
    tangram3.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)

# noinspection DuplicatedCode
def test_translate(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    tangram1 = Tangram(scale=100, gap=0)
    tangram2 = Tangram(scale=100, gap=3)
    create_square(tangram1)
    tangram2.add(tangram2.t4a)
    tangram1.remove(tangram1.t4a)
    tangram1.translate(10, 20)
    tangram2.translate(10, 20)

    tangram1.draw(expected)
    tangram2.draw(expected)

    actual = svgwrite.Drawing(size=(200, 200))
    tangram3 = SingleHint(scale=100, gap=3, highlight='t4a')
    create_square(tangram3)
    tangram3.translate(10, 20)
    tangram3.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)
