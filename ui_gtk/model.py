class PlotData:
    def __init__(self):
        self._x = []
        self._y = []

    def add_point(self, x, y):
        self._x.append(x)
        self._y.append(y)

    def __iter__(self):
        return iter([self._x, self._y])