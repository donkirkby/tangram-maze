import typing
from pathlib import Path

from reportlab.lib import pagesizes
from reportlab.platypus import Flowable, SimpleDocTemplate
from svgwrite import Drawing

from maze import layout_empty, layout_fat_axe, layout_saw, layout_thin_axe, layout_tug, layout_ship, layout_top, \
    add_hint_set
from tangram import Tangram
from test_tan import LiveSvg


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


def write_hint_files():
    hint_folder = Path(__file__).with_name('hints')
    hint_folder.mkdir(exist_ok=True)
    pdf_path = hint_folder / 'hints.pdf'
    story: list[Flowable] = []
    doc = SimpleDocTemplate(str(pdf_path),
                            author='Don Kirkby',
                            pagesize=pagesizes.landscape(pagesizes.letter),
                            title='Tangram Hints')
    # add_hint_set(layout_goat, hint_folder, story, 'goat', 't4a')
    # add_hint_set(layout_long_jump, hint_folder, story, 'long_jump', 't4a')
    add_hint_set(layout_saw, hint_folder, story, 'saw')
    # add_hint_set(layout_llama, hint_folder, story, 'llama', 't4a')
    # add_hint_set(layout_thin_axe, hint_folder, story, 'thin_axe', 't4a')
    add_hint_set(layout_tug, hint_folder, story, 'tug', 't4a')
    # add_hint_set(layout_laundry, hint_folder, story, 'laundry')
    # add_hint_set(layout_giraffe, hint_folder, story, 'giraffe')
    add_hint_set(layout_vulture, hint_folder, story, 'vulture')
    # add_hint_set(layout_kangaroo, hint_folder, story, 'kangaroo', 't4a')

    doc.build(story)


def main():
    image_path = Path(__file__).with_name('letter_grid.svg')
    write_hint_files()
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
        LiveSvg(drawing.tostring()).display((-width*0.35, height*0.4))
    else:
        image_path.write_text(drawing.tostring())

if __name__ in ('__main__', '__live_coding__'):
    main()
