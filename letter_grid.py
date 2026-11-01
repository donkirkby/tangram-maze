import math
import typing
from collections import defaultdict
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from random import seed, shuffle
from textwrap import dedent

import svgwrite
from reportlab.lib import pagesizes
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, SimpleDocTemplate, Paragraph, Table, PageBreak, Spacer
from svglib.svglib import svg2rlg
from svgwrite import Drawing

from font_set import register_fonts
from hint_display import HintDisplay
from live_pdf import LivePdf
from maze import layout_empty, layout_fat_axe, layout_saw, layout_thin_axe, \
    layout_tug, layout_ship, layout_top
from tangram import Tangram


@dataclass
class DirectionSet:
    table_rows: list[list[Paragraph]]
    directions: dict[str, list[int]]


class LetterGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scale_factor = 1.0
        self.labels: list[str] = []
        self.layout_functions: list[typing.Callable[[Tangram], None]] = []

    def scale(self, scale):
        self.scale_factor = scale

    def add(self, label: str, layout_function: typing.Callable[[Tangram], None]):
        self.labels.append(label)
        self.layout_functions.append(layout_function)

    def draw(self, drawing: Drawing):
        stroke_width = self.scale_factor / 25
        x0 = drawing['width']//2
        y0 = drawing['height']//2

        for x in range(self.width):
            for y in range(self.height):
                scaled_x = (2 * x + 1) * self.scale_factor
                scaled_y = (2 * y + 1) * self.scale_factor
                for x2 in range(max(x, 0), min(x+2, self.width)):
                    for y2 in range(max(y-1, 0), min(y+2, self.height)):
                        if x2 <= x and y2 <= y:
                            continue
                        drawing.add(drawing.line((scaled_x, scaled_y),
                                                 ((2*x2+1)*self.scale_factor,
                                                  (2*y2+1)*self.scale_factor),
                                                 stroke='black',
                                                 stroke_width=stroke_width))
                drawing.add(drawing.circle((scaled_x, scaled_y),
                                           self.scale_factor / 2,
                                           stroke='black',
                                           stroke_width=stroke_width,
                                           fill='white'))
                cell_index = y*self.width + x
                if cell_index >= len(self.labels):
                    continue
                label = self.labels[cell_index]
                if len(label) > 1:
                    font_size = round(0.2*self.scale_factor)
                else:
                    font_size = round(0.3*self.scale_factor)
                drawing.add(drawing.text(label,
                                         (scaled_x,
                                          round(scaled_y-0.2*self.scale_factor)),
                                         font_family='FredokaOne',
                                         font_size=font_size,
                                         text_anchor='middle'))
                layout_function = self.layout_functions[cell_index]
                tangram = Tangram()
                tangram.scale(0.3*self.scale_factor)
                layout_function(tangram)
                tangram.centre_on(round(scaled_x - x0),
                                  round(y0 - scaled_y - 0.12*self.scale_factor))
                tangram.draw(drawing)


def layout_square(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(45)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(135)
    tangram.add(tangram.p)
    tangram.p.anchor(tangram.t4b, 2, 3)
    tangram.p.rotate(45)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(-135)
    tangram.add(tangram.s)
    tangram.s.rotate(-45)
    tangram.add(tangram.t1b)
    tangram.t1b.anchor(tangram.t4a, 1, 2)
    tangram.t1b.rotate(-45)
    tangram.add(tangram.t2)
    tangram.t2.anchor(tangram.t1b, 1, 1)
    tangram.t2.rotate(90)


def layout_llama(tangram: Tangram):
    tangram.add(tangram.p)
    tangram.p.rotate(90)
    tangram.add(tangram.s)
    tangram.s.rotate(45)
    tangram.s.anchor(tangram.p, 0, 2)
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-135)
    tangram.t4a.anchor(tangram.s, 1)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(180)
    tangram.t4b.anchor(tangram.t4a, 2, 1)
    l = 0.38*tangram.t4a.width
    tangram.t4b.translate(-l, l)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(180)
    tangram.t1a.anchor(tangram.t4a, 1)
    l = 0.85*tangram.t4a.width
    tangram.t1a.translate(l, 0)
    tangram.add(tangram.t2)
    tangram.t2.rotate(135)
    tangram.t2.anchor(tangram.t4b, 2, 2)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(-100)
    tangram.t1b.anchor(tangram.t4b, 0, 1)


def layout_long_jump(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-90)
    tangram.add(tangram.s)
    tangram.s.rotate(50)
    tangram.s.translate(0.5*tangram.t4a.width, 0)
    tangram.add(tangram.p)
    tangram.p.rotate(90)
    tangram.p.anchor(tangram.t4a, 0, 1)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(90)
    tangram.t4b.anchor(tangram.t4a, 1, 2)
    l = 0.35 * tangram.t4a.width
    tangram.t4b.translate(-l, -l)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(-90)
    tangram.t1a.anchor(tangram.t4a, 1, 2)
    l = 0.3 * tangram.t1a.width
    tangram.t1a.translate(-l, -l)
    tangram.add(tangram.t2)
    tangram.t2.rotate(135)
    tangram.t2.anchor(tangram.t4b, 0, 1)
    tangram.t2.translate(0, 0.4*tangram.t2.height)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(-45)
    tangram.t1b.anchor(tangram.t2, 2, 2)
    tangram.t1b.translate(0, 0.4*tangram.t1b.height)


def layout_laundry(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(180)
    tangram.t4b.anchor(tangram.t4a, 1, 2)
    tangram.add(tangram.p)
    tangram.p.anchor(tangram.t4b)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t4b, 0, 3)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(180)
    tangram.t1a.anchor(tangram.s, 1)
    tangram.add(tangram.t2)
    tangram.t2.rotate(135)
    tangram.t2.anchor(tangram.t1a, 2)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(90)
    tangram.t1b.anchor(tangram.t2, 2)


def layout_giraffe(tangram: Tangram):
    tangram.add(tangram.t2)
    tangram.add(tangram.p)
    tangram.p.rotate(135)
    tangram.p.flip()
    tangram.p.translate(0, -0.2*tangram.p.height)
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-45)
    tangram.t4a.anchor(tangram.p, 0, 2)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(-45)
    tangram.t4b.anchor(tangram.t4a, 0, 2)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(135)
    tangram.t1a.anchor(tangram.t4a, 0, 1)
    tangram.add(tangram.s)
    tangram.s.rotate(45)
    tangram.s.anchor(tangram.t1a, 2, 3)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(-45)
    tangram.t1b.anchor(tangram.s)


def layout_vulture(tangram: Tangram):
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(-135)
    tangram.add(tangram.s)
    tangram.s.rotate(45)
    tangram.s.anchor(tangram.t1a, 1)
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-135)
    tangram.t4a.anchor(tangram.t1a, 1, 2)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(-90)
    tangram.t4b.anchor(tangram.t4a, 1)
    tangram.add(tangram.t2)
    tangram.t2.rotate(90)
    tangram.t2.anchor(tangram.t4b, 0, 1)
    tangram.add(tangram.p)
    tangram.p.flip()
    tangram.p.anchor(tangram.t2, 0, 1)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(-135)
    tangram.t1b.anchor(tangram.t4b, 1)
    tangram.flip()
    tangram.rotate(180)


def layout_kangaroo(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(90)
    tangram.t1a.translate(0, 1.5*tangram.t1a.height)
    tangram.add(tangram.t1b)
    tangram.t1b.anchor(tangram.t4a, 0, 1)
    tangram.t1b.rotate(-45)
    tangram.t1b.translate(0, -0.5*tangram.t1b.height)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(180)
    tangram.t4b.anchor(tangram.t4a, 1)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t4b, 2, 2)
    tangram.s.rotate(45)
    l = 0.7*tangram.s.height
    tangram.s.translate(-l, l)
    tangram.add(tangram.t2)
    tangram.t2.rotate(-135)
    tangram.t2.anchor(tangram.s, 1)
    tangram.add(tangram.p)
    tangram.p.flip()
    tangram.p.anchor(tangram.t2, 2, 2)
    tangram.p.rotate(-45)


def layout_goat(tangram: Tangram):
    tangram.add(tangram.p)
    tangram.p.flip()
    tangram.add(tangram.t2)
    tangram.t2.rotate(-90)
    tangram.t2.anchor(tangram.p, 3)
    tangram.add(tangram.s)
    tangram.s.rotate(45)
    tangram.s.anchor(tangram.t2, 2, 2)
    l = 0.25*tangram.s.height
    tangram.s.translate(-l, -l)
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-135)
    tangram.t4a.anchor(tangram.s, 1)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(-90)
    tangram.t1a.anchor(tangram.t4a, 1)
    tangram.t1a.translate(tangram.t1a.width, 0)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(180)
    tangram.t4b.anchor(tangram.t4a, 0, 1)
    l = 0.18*tangram.t4b.height
    tangram.t4b.translate(l, -l)
    tangram.add(tangram.t1b)
    tangram.t1b.anchor(tangram.t4b, 0, 2)
    tangram.t1b.rotate(135)
    tangram.t1b.translate(0, -0.5*tangram.t1b.height)


def build_direction_data(paragraph_style) -> DirectionSet:
    label_style = ParagraphStyle('Label',
                                 parent=paragraph_style,
                                 alignment=TA_RIGHT)
    rows: list[list[Paragraph]] = []
    direction_nums: dict[str, list] = defaultdict(list)

    labels = {0: 'E',
              45: 'NE',
              90: 'N',
              135: 'NW',
              180: 'W',
              225: 'SW',
              270: 'S',
              315: 'SE'}

    direction_count = 217
    column_count = 7
    row_count = math.ceil(direction_count / column_count)
    directions: list[int] = []
    for i in range(direction_count):
        direction = i * 45 % 360
        directions.append(direction)

    seed(0)
    shuffle(directions)

    if __name__ != '__live_coding__':
        seed()

    for i in range(row_count):
        row: list[Paragraph] = []
        for j in range(column_count):
            direction_index = j*row_count + i
            if direction_index >= direction_count:
                break
            direction = directions[direction_index]
            direction_label = direction_index + 1
            direction_text = labels[direction]
            direction_nums[direction_text].append(direction_label)
            row.append(Paragraph(f'{direction_label}:', style=label_style))
            row.append(Paragraph(direction_text, style=paragraph_style))
        rows.append(row)

    for direction, numbers in direction_nums.items():
        shuffle(numbers)

    return DirectionSet(rows, direction_nums)


def add_hint_display(layout_function: typing.Callable[..., None],
                     story: list[Flowable],
                     hint1: int = 0,
                     hint2: int = 0,
                     solution: int = 0) -> None:
    if story:
        story.append(PageBreak())

    scale = 372
    # scale = 17
    tangram = Tangram(1)
    layout_function(tangram)

    display = HintDisplay(tangram, hint1, hint2, solution, scale=scale)

    add_hint(display, story)


def add_hint(display: HintDisplay, story: list[Flowable]):
    drawing = svgwrite.Drawing(size=(display.width, display.height))
    display.draw(drawing)
    svg_text = drawing.tostring()

    svg_bytes = svg_text.encode()
    pdf_drawing = svg2rlg(BytesIO(svg_bytes))
    assert pdf_drawing is not None

    story.append(pdf_drawing)


def add_tangram(hint: Tangram, story: list[Flowable]) -> None:
    left, bottom, right, top = hint.bounds
    hint.translate(-left - (right-left)/2, -bottom - (top-bottom)/2)
    size = (right-left, top-bottom)

    drawing = svgwrite.Drawing(size=size)
    hint.draw(drawing)
    svg_text = drawing.tostring()

    svg_bytes = svg_text.encode()
    pdf_drawing = svg2rlg(BytesIO(svg_bytes))
    assert pdf_drawing is not None

    story.append(pdf_drawing)


def write_hint_files():
    hint_folder = Path(__file__).with_name('hints')
    hint_folder.mkdir(exist_ok=True)
    pdf_path = hint_folder / 'hints.pdf'
    story: list[Flowable] = []
    doc = SimpleDocTemplate(str(pdf_path),
                            author='Don Kirkby',
                            pagesize=pagesizes.letter,
                            title='Tangram Hints',
                            leftMargin=0.5*inch,
                            topMargin=0.5*inch,
                            rightMargin=0.5*inch,
                            bottomMargin=0.5*inch)
    register_fonts()
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        if hasattr(style, 'fontSize'):
            if style.name.startswith('Heading'):
                scale = 5
                style.fontName = 'Heading'
            else:
                scale = 1.37
                style.fontName = 'Body'
            style.fontSize *= scale
            style.leading *= scale

    heading_style = styles['Heading1']
    paragraph_style = styles['Normal']

    story.append(Paragraph('Hints', style=heading_style))
    hint_texts = dedent('''\
        Before you get too frustrated with a tangram, this booklet will give you
        some hints. There are three hints for each tangram and a solution. The
        first two hints for each tangram tell you the direction that the right
        angle corner of the two largest triangles point. Look at the number for
        a hint, then look up that number in the big table on the next page to
        see which direction the triangle points.
        
        If you've looked up the hints for both large triangles and you still
        can't solve the tangram, you can turn to the next page. It has a
        full-size outline of the tangram that you can place the pieces on while
        you solve.
        
        If you're still stuck, there's a solution number that works the same way
        as the first two hints, but tells you the direction of the medium
        triangle. Once you've looked that up, you can try to solve the tangram,
        or just follow the line in that direction to the next letter.
        
        For example, if the diagram below were the solution, then the hint
        directions would be E and S, and the solution direction would be SE.
        ''').split('\n\n')
    for hint_text in hint_texts:
        story.append(Paragraph(hint_text, style=paragraph_style))

    story.append(Spacer(1, 0.5*inch))
    square = Tangram(scale=372, gap=3)
    layout_square(square)
    add_tangram(square, story)

    direction_set = build_direction_data(paragraph_style)
    story.append(PageBreak())
    story.append(Table(direction_set.table_rows))

    add_hint_display(layout_goat, story)
    add_hint_display(layout_long_jump, story)
    add_hint_display(layout_saw, story)
    add_hint_display(layout_llama, story)
    add_hint_display(layout_thin_axe, story)
    add_hint_display(layout_tug, story)
    add_hint_display(layout_laundry, story)
    add_hint_display(layout_giraffe, story)
    add_hint_display(layout_vulture, story)
    add_hint_display(layout_kangaroo, story)

    doc.build(story)


def main():
    image_path = Path(__file__).with_name('letter_grid.svg')
    write_hint_files()

    if __name__ == '__live_coding__':
        live_pdf = LivePdf(image_path.with_name('hints') / 'hints.pdf', 2)
        live_pdf.display((0, 150))
        live_pdf = LivePdf(image_path.with_name('hints') / 'hints.pdf', 3)
        live_pdf.display((0, -100))
        return

    letter_grid = LetterGrid(5, 5)
    letter_grid.scale(100)

    letter_grid.add('A', layout_ship)
    letter_grid.add('P', layout_long_jump)
    letter_grid.add('R', layout_saw)
    letter_grid.add('E', layout_llama)
    letter_grid.add('D', layout_thin_axe)

    letter_grid.add('S', layout_top)
    letter_grid.add('I', layout_giraffe)
    letter_grid.add('start', layout_goat)
    letter_grid.add('A', layout_tug)
    letter_grid.add('E', layout_vulture)

    letter_grid.add('M', layout_kangaroo)
    letter_grid.add('N', layout_llama)
    letter_grid.add('O', layout_long_jump)
    letter_grid.add('T', layout_laundry)
    letter_grid.add('I', layout_giraffe)

    letter_grid.add('I', layout_vulture)
    letter_grid.add('R', layout_top)
    letter_grid.add('end', layout_empty)
    letter_grid.add('O', layout_vulture)
    letter_grid.add('Y', layout_thin_axe)

    letter_grid.add('W', layout_ship)
    letter_grid.add('C', layout_fat_axe)
    letter_grid.add('N', layout_kangaroo)
    letter_grid.add('R', layout_ship)
    letter_grid.add('S', layout_top)

    width = 1000
    height = 1000
    drawing = Drawing(size=(width, height))
    letter_grid.draw(drawing)
    if __name__ == '__live_coding__':
        # LiveSvg(drawing.tostring()).display((-width*0.35, height*0.4))
        pass
    else:
        image_path.write_text(drawing.tostring())

if __name__ in ('__main__', '__live_coding__'):
    main()
