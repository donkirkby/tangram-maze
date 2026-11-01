from io import StringIO

import svgwrite
from reportlab.graphics import renderPM
from space_tracer import LiveImageDiffer, LiveImage, LivePainter
from svglib.svglib import svg2rlg

from tan import Tan


# noinspection DuplicatedCode
def test_width():
    t1 = Tan((100, 10), (20, 50))

    assert t1.width == 100  # implicit start point is (0, 0)


# noinspection DuplicatedCode
def test_height():
    t1 = Tan((100, 10), (20, 50))

    assert t1.height == 50  # implicit start point is (0, 0)


# noinspection DuplicatedCode
def test_draw(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 100), (200, 100), (100, 0)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


def test_translate(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(50, 0), (150, 100), (50, 100)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t1.translate(-50, 0)
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


def test_rotate(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(0, 100), (100, 100), (100, 0)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100), direction=-135)

    assert t1.direction == 225

    t1.rotate(90)
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)

    assert t1.direction == 315


def test_rotate_anchor_point(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 200), (200, 200), (200, 100)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t1.rotate(90, anchor_point=(100, 0))
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


def test_scale(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 100), (150, 100), (100, 50)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t1.scale(0.5)
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


def test_flip(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 100), (200, 100), (100, 200), (0, 200)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100), (-100, 100))
    t1.flip()
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


def test_flip_direction(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 200), (100, 100), (200, 100)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100), direction=-135)

    t1.flip()
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)

    assert t1.direction == 135


# noinspection DuplicatedCode
def test_copy(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 100), (200, 100), (100, 0)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t2 = Tan(copy=t1)
    t2.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


def test_display(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(4, 103), (47, 103), (47, 146)],
                                  fill='black'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((86, 0), (0, 86))
    t1.translate(6, 6)
    t2 = Tan((100, 0), (0, 100), display=t1)
    t2.rotate(90)
    t2.scale(0.5)
    t2.translate(-50, 0)
    t2.flip()
    t2.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


class LiveSvg(LiveImage):
    def __init__(self, svg: str):
        self.svg = svg

    def convert_to_png(self) -> bytes:
        rlg = svg2rlg(StringIO(self.svg))
        return renderPM.drawToString(rlg, fmt="PNG")

    # This override can be removed after bug is fixed:
    # https://github.com/donkirkby/live-py-plugin/issues/360
    def convert_to_painter(self) -> LivePainter:
        painter = super().convert_to_painter()
        # noinspection PyUnresolvedReferences
        image = painter.image
        if 'A' not in image.getbands():
            image.putalpha(120)
        return painter


# noinspection DuplicatedCode
def test_fill(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(200, 200))
    expected.add(expected.polygon([(100, 100), (200, 100), (100, 0)],
                                  fill='blue'))

    actual = svgwrite.Drawing(size=(200, 200))

    t1 = Tan((100, 0), (0, 100))
    t1.fill = 'blue'
    t1.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)
