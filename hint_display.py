from svgwrite import Drawing
from svgwrite.container import Group

from tangram import Tangram


class HintDisplay:
    def __init__(self,
                 tangram: Tangram,
                 hint1: int,
                 hint2: int,
                 solution: int,
                 scale: float = 372):
        self.tangram = tangram
        self.scale = scale
        self.hint1 = hint1
        self.hint2 = hint2
        self.solution = solution

        tangram.scale(scale)
        self.font_size = round(scale*0.1)
        self.height = round(tangram.height + 4*self.font_size)
        self.width = round(tangram.width)
        left, bottom, right, top = tangram.bounds
        target_x = -tangram.width / 2
        target_y = -tangram.height / 2
        tangram.translate(round(target_x - left), round(target_y - bottom))
        self.is_landscape = self.height < self.width
        if self.is_landscape:
            tangram.translate(0, 0)
            self.width, self.height = self.height, self.width

    def draw(self, drawing: Drawing) -> None:
        g = Group()
        if self.is_landscape:
            width, height = self.height, self.width
            drawing['width'], drawing['height'] = (drawing['height'],
                                                   drawing['width'])
            g['transform'] = f'translate({height}, 0) rotate(90)'
        else:
            width, height = self.width, self.height

        self.tangram.draw(drawing)
        g.add(drawing.elements.pop())
        drawing.add(g)


        g.add(drawing.text(f'^N',
                           (width, self.font_size),
                           font_family='Raleway',
                           font_size=self.font_size,
                           text_anchor='end'))
        g.add(drawing.text(f'This Solution: {self.solution},  '
                           f'Next Hints: {self.hint1}, {self.hint2}',
                           (0, height),
                           font_family='Raleway',
                           font_size=self.font_size))

        if self.is_landscape:
            drawing['width'], drawing['height'] = (drawing['height'],
                                                   drawing['width'])
