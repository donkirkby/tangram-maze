from tan import Tan
from tan_group import TanGroup
from tangram import Tangram


class GridHint(Tangram):
    def __init__(self,
                 scale: float = 1,
                 gap: float = 0,
                 highlight: str = 't1a'):
        super().__init__(scale, gap)
        if highlight != 't2':
            subdisplay1 = Tan(copy=self.t1a.display)
            subdisplay1.rotate(-135)
            subdisplay1.anchor(self.t2.display, 1, 2)
            subdisplay2 = Tan(copy=self.t1a.display)
            subdisplay2.rotate(135)
            subdisplay2.anchor(self.t2.display, 2, 1)
            self.t2.display = TanGroup(tans=(subdisplay1, subdisplay2))
            self.t2.display.add(subdisplay1)
            self.t2.display.add(subdisplay2)

        if highlight != 't4a':
            subdisplay1 = Tan(copy=self.t1a.display)
            subdisplay1.anchor(self.t4a.display, 1, 1)
            subdisplay2 = Tan(copy=self.t1a.display)
            subdisplay2.anchor(self.t4a.display, 2, 2)
            subdisplay3 = Tan(copy=self.t1a.display)
            subdisplay3.rotate(90)
            subdisplay3.anchor(subdisplay1)
            subdisplay3.translate(-gap, 0)
            subdisplay4 = Tan(copy=self.t1a.display)
            subdisplay4.rotate(-90)
            subdisplay4.anchor(subdisplay2)
            subdisplay4.translate(0, -gap)
            self.t4a.display = TanGroup(tans=(subdisplay1,
                                              subdisplay2,
                                              subdisplay3,
                                              subdisplay4))
            self.t4a.display.add(subdisplay1)
            self.t4a.display.add(subdisplay2)
            self.t4a.display.add(subdisplay3)
            self.t4a.display.add(subdisplay4)

        if highlight != 't4b':
            subdisplay1 = Tan(copy=self.t1a.display)
            subdisplay1.anchor(self.t4b.display, 1, 1)
            subdisplay2 = Tan(copy=self.t1a.display)
            subdisplay2.anchor(self.t4b.display, 2, 2)
            subdisplay3 = Tan(copy=self.t1a.display)
            subdisplay3.rotate(90)
            subdisplay3.anchor(subdisplay1)
            subdisplay3.translate(-gap, 0)
            subdisplay4 = Tan(copy=self.t1a.display)
            subdisplay4.rotate(-90)
            subdisplay4.anchor(subdisplay2)
            subdisplay4.translate(0, -gap)
            self.t4b.display = TanGroup(tans=(subdisplay1,
                                              subdisplay2,
                                              subdisplay3,
                                              subdisplay4))
            self.t4b.display.add(subdisplay1)
            self.t4b.display.add(subdisplay2)
            self.t4b.display.add(subdisplay3)
            self.t4b.display.add(subdisplay4)

        if highlight != 'p':
            subdisplay1 = Tan(copy=self.t1a.display)
            subdisplay1.anchor(self.p.display, 1, 1)
            subdisplay2 = Tan(copy=self.t1a.display)
            subdisplay2.rotate(180)
            subdisplay2.anchor(self.p.display, 3, 1)
            self.p.display = TanGroup(tans=(subdisplay1, subdisplay2))
            self.p.display.add(subdisplay1)
            self.p.display.add(subdisplay2)

        if highlight != 's':
            subdisplay1 = Tan(copy=self.t1a.display)
            subdisplay1.rotate(90)
            subdisplay1.anchor(self.s.display, 1)
            subdisplay2 = Tan(copy=self.t1a.display)
            subdisplay2.rotate(-90)
            subdisplay2.anchor(self.s.display, 3)
            self.s.display = TanGroup(tans=(subdisplay1, subdisplay2))
            self.s.display.add(subdisplay1)
            self.s.display.add(subdisplay2)
