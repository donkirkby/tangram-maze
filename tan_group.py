import math
import typing
from collections import defaultdict

import shapely
from shapely import Point, Geometry

from tan import Tan


class TanGroup(Tan):
    def __init__(self,
                 scale: float = 1,
                 tans: typing.Sequence[Tan] = ()) -> None:
        super().__init__()
        self.visible_tans: typing.List[Tan] = []
        self.all_tans = tans
        for tan in self.all_tans:
            tan.scale(scale)

    def add(self, tan):
        self.visible_tans.append(tan)

    def remove(self, tan):
        self.visible_tans.remove(tan)

    def scale(self, scale):
        for tan in self.all_tans:
            tan.scale(scale)

    def flip(self):
        for tan in self.all_tans:
            tan.flip()

    def rotate(self,
               angle,
               anchor_point: None | tuple[float, float] = None):
        if anchor_point is None:
            anchor_point = self.visible_tans[0].anchor_point
        for tan in self.all_tans:
            tan.rotate(angle, anchor_point)

    def draw(self, drawing):
        if not self.visible_tans:
            return

        fill = self.visible_tans[0].fill
        combined = self.create_polygon(drawing)
        components = getattr(combined, 'geoms', None)
        if components is None:
            components = [combined]
        for component in components:
            vertex_rings: dict[int, list] = defaultdict(list)
            exterior_points = [Point(c) for c in component.exterior.coords]
            for ring in component.interiors:
                start = Point(ring.coords[0])
                closest_index = 0
                min_distance = start.distance(exterior_points[0])
                for i, point in enumerate(exterior_points[1:], 1):
                    new_distance = start.distance(point)
                    if new_distance < min_distance:
                        min_distance = new_distance
                        closest_index = i
                vertex_rings[closest_index].append(ring)
            steps = ['M']
            for i, point in enumerate(exterior_points):
                steps.append(f'{point.x} {point.y}')
                for ring in vertex_rings[i]:
                    for x2, y2, in ring.coords:
                        steps.append(f'{x2} {y2}')
                    steps.append(f'{point.x} {point.y}')
            drawing.add(drawing.path(' '.join(steps),
                                        fill=fill,
                                        fill_rule='evenodd'))

    def create_polygon(self,
                       drawing) -> list[tuple[float, float]] | Geometry:
        polygons = [tan.create_polygon(drawing)
                    for tan in self.visible_tans]
        # if not polygons:
        #     return

        polygon_shapes: list[Geometry] = []
        for polygon in polygons:
            if isinstance(polygon, Geometry):
                polygon_shapes.append(polygon)
            else:
                polygon_shapes.append(shapely.Polygon(polygon))

        tangram_magnitude = math.log10(max(self.width, self.height))
        grid_magnitude = math.floor(tangram_magnitude - 3)
        grid_size = math.pow(10, grid_magnitude)
        combined = shapely.union_all(polygon_shapes, grid_size=grid_size)
        return combined

    def translate(self, dx, dy):
        for tan in self.all_tans:
            tan.translate(dx, dy)

    @property
    def width(self):
        left, bottom, right, top = self.bounds
        return right - left

    @property
    def height(self):
        left, bottom, right, top = self.bounds
        return top - bottom

    @property
    def bounds(self) -> typing.Tuple[float, float, float, float]:
        """ Bounding box for all visible tans.

        :return: (left, bottom, right, top)
        """
        points_source = self.visible_tans or self.all_tans
        points = [point
                  for tan in points_source
                  for point in tan.points]
        left = min(x for x, y in points)
        right = max(x for x, y in points)
        top = max(y for x, y in points)
        bottom = min(y for x, y in points)
        return left, bottom, right, top
