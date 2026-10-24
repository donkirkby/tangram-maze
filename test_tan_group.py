import svgwrite
from space_tracer import LiveImageDiffer

from tan import Tan
from tan_group import TanGroup
from test_tan import LiveSvg


# noinspection DuplicatedCode
def test_draw(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t2 = Tan(copy=t1)
    t2.translate(-75, -50)

    t1.draw(expected)
    t2.draw(expected)

    actual = svgwrite.Drawing(size=(200, 200))

    group = TanGroup(tans=(t1, t2))
    group.add(t1)
    group.add(t2)
    group.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


# noinspection DuplicatedCode
def test_translate(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t2 = Tan(copy=t1)
    t2.translate(-75, -50)

    t3 = Tan(copy=t1)
    t4 = Tan(copy=t2)

    t1.translate(-10, 0)
    t2.translate(-10, 0)
    t1.draw(expected)
    t2.draw(expected)

    actual = svgwrite.Drawing(size=(200, 200))

    group = TanGroup(tans=(t3, t4))
    group.add(t3)
    group.add(t4)
    group.translate(-10, 0)
    group.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


# noinspection DuplicatedCode
def test_flip(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t2 = Tan(copy=t1)
    t2.translate(-75, -50)

    t3 = Tan(copy=t1)
    t4 = Tan(copy=t2)

    t1.flip()
    t2.flip()
    t1.draw(expected)
    t2.draw(expected)

    actual = svgwrite.Drawing(size=(200, 200))

    group = TanGroup(tans=(t3, t4))
    group.add(t3)
    group.add(t4)
    group.flip()
    group.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)
