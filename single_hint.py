from tangram import Tangram


class SingleHint(Tangram):
    def __init__(self,
                 scale: float = 1,
                 gap: float = 0,
                 highlight: str = 't1a'):
        super().__init__(scale, gap=0)
        highlighted_tangram = Tangram(scale, gap)
        old_tan = getattr(self, highlight)
        new_tan = getattr(highlighted_tangram, highlight)
        setattr(self, highlight, new_tan)
        self.all_tans = [tan
                         for tan in self.all_tans
                         if tan is not old_tan]
        self.all_tans.append(new_tan)
