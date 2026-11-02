import svgwrite
from space_tracer import LiveImageDiffer

from letter_grid import LetterGrid, layout_saw, layout_thin_axe, layout_empty
from tangram import Tangram
from test_tan import LiveSvg


# noinspection DuplicatedCode
def test_draw(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(300, 300))
    line_args = dict(stroke='black', stroke_width=2)
    expected.add(expected.line((50, 50), (150, 50), **line_args))
    expected.add(expected.line((50, 50), (150, 150), **line_args))
    expected.add(expected.line((50, 50), (50, 150), **line_args))
    expected.add(expected.line((150, 50), (150, 150), **line_args))
    expected.add(expected.line((150, 50), (50, 150), **line_args))
    expected.add(expected.line((50, 150), (150, 150), **line_args))

    expected.add(expected.line((150, 50), (250, 50), **line_args))
    expected.add(expected.line((150, 50), (250, 150), **line_args))
    expected.add(expected.line((250, 50), (250, 150), **line_args))
    expected.add(expected.line((250, 50), (150, 150), **line_args))
    expected.add(expected.line((150, 150), (250, 150), **line_args))

    expected.add(expected.line((50, 150), (150, 250), **line_args))
    expected.add(expected.line((50, 150), (50, 250), **line_args))
    expected.add(expected.line((150, 150), (150, 250), **line_args))
    expected.add(expected.line((150, 150), (50, 250), **line_args))
    expected.add(expected.line((50, 250), (150, 250), **line_args))

    expected.add(expected.line((150, 150), (250, 250), **line_args))
    expected.add(expected.line((250, 150), (250, 250), **line_args))
    expected.add(expected.line((250, 150), (150, 250), **line_args))
    expected.add(expected.line((150, 250), (250, 250), **line_args))

    circle_args = dict(stroke='black', fill='white', stroke_width=2)
    expected.add(expected.circle((50, 50), 30, **circle_args))
    expected.add(expected.circle((150, 50), 30, **circle_args))
    expected.add(expected.circle((250, 50), 30, **circle_args))
    expected.add(expected.circle((50, 150), 30, **circle_args))
    expected.add(expected.circle((150, 150), 30, **circle_args))
    expected.add(expected.circle((250, 150), 30, **circle_args))
    expected.add(expected.circle((50, 250), 30, **circle_args))
    expected.add(expected.circle((150, 250), 30, **circle_args))
    expected.add(expected.circle((250, 250), 30, **circle_args))

    actual = svgwrite.Drawing(size=(300, 300))

    g = LetterGrid(3, 3)
    g.scale(50)
    g.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)


# noinspection DuplicatedCode
def test_add(image_differ: LiveImageDiffer):
    expected = svgwrite.Drawing(size=(300, 300))
    empty_grid = LetterGrid(3, 3)
    empty_grid.scale(50)
    empty_grid.draw(expected)
    expected.add(expected.text('A',
                               (50, 35),
                               font_family='FredokaOne',
                               font_size=15,
                               text_anchor='middle',))
    expected.add(expected.text('start',
                               (150, 35),
                               font_family='FredokaOne',
                               font_size=10,
                               text_anchor='middle',))
    expected.add(expected.text('end',
                               (250, 35),
                               font_family='FredokaOne',
                               font_size=10,
                               text_anchor='middle',))
    tangram = Tangram(18.5)
    layout_saw(tangram)
    tangram.centre_on(-100, 94)
    tangram.draw(expected)

    tangram = Tangram(18.5)
    layout_thin_axe(tangram)
    tangram.centre_on(0, 94)
    tangram.draw(expected)

    actual = svgwrite.Drawing(size=(300, 300))

    g = LetterGrid(3, 3)
    g.scale(50)

    g.add('A', layout_saw)
    g.add('start', layout_thin_axe)
    g.add('end', layout_empty)

    g.draw(actual)

    svg1 = LiveSvg(actual.tostring())
    svg2 = LiveSvg(expected.tostring())
    image_differ.assert_equal(svg1, svg2)
