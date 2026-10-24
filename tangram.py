import math

from tan import Tan
from tan_group import TanGroup


class Tangram(TanGroup):
    ROOT2 = math.sqrt(2)

    def __init__(self, scale: float = 1, gap: float = 0):
        root2 = self.ROOT2
        gap /= scale
        if gap == 0:
            display = None
        else:
            display = Tan((root2/4-gap/2*(2+root2), 0),
                          (0, root2/4-gap/2*(2+root2)))
            display.translate(gap/2, gap/2)
        self.t1a = Tan((root2/4, 0), (0, root2/4), display=display)
        self.t1b = Tan(copy=self.t1a)

        if gap != 0:
            display = Tan((1/2-gap/2*(2+root2), 0), (0, 1/2-gap/2*(2+root2)))
            display.translate(gap/2, gap/2)
        self.t2 = Tan((1/2, 0), (0, 1/2), display=display)

        if gap != 0:
            display = Tan((root2/2-gap/2*(2+root2), 0),
                          (0, root2/2-gap/2*(2+root2)))
            display.translate(gap/2, gap/2)
        self.t4a = Tan((root2/2, 0), (0, root2/2), display=display)
        self.t4b = Tan(copy=self.t4a)

        if gap != 0:
            x_shift = -0.25*gap
            display = Tan((root2/4-2*gap-2*x_shift, 0),
                          (-gap-2*x_shift, root2/4-gap),
                          (-root2/4+gap, root2/4-gap))
            display.translate(gap/2+x_shift, gap/2)
        self.p = Tan((root2/4, 0),
                     (0, root2/4),
                     (-root2/4, root2/4),
                     display=display)

        if gap != 0:
            display = Tan((root2/4-gap, 0),
                          (root2/4-gap, root2/4-gap),
                          (0, root2/4-gap))
            display.translate(gap/2, gap/2)
        self.s = Tan((root2/4, 0), (root2/4, root2/4), (0, root2/4),
                     display=display)

        tans = (self.t1a, self.t1b, self.t2, self.t4a, self.t4b, self.s, self.p)
        super().__init__(scale, tans)
