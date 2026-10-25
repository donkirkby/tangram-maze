import logging
import math
import random
from collections import defaultdict
from io import BytesIO
from itertools import count
from pathlib import Path
from typing import Any, Callable

import svgwrite
from networkx import Graph
from reportlab.lib import pagesizes
from reportlab.platypus import SimpleDocTemplate, Flowable, PageBreak
from svglib.svglib import svg2rlg
from svgwrite import Drawing

from single_hint import SingleHint
from tangram import Tangram
from test_tan import LiveSvg

logger = logging.getLogger(__name__)

class Maze:
    ARROW = '\u21E9'

    def __init__(self,
                 width: int = 0,
                 height: int = 0,
                 text: str|None = None):
        # graph has edge, if there is no wall between neighbouring nodes.
        self.graph = Graph()
        self.width = width
        self.height = height
        self.scale = 1.0
        self.offset_x = self.offset_y = 0

        # [ (x, y, group_name) ]
        self.chambers: list[tuple[float, float, str]] = []

        self.chamber_radius = math.sqrt(3*3 + 2*2)

        # { chamber_group_name: tangram }
        self.tangrams: dict[str, Tangram] = {}

        # { group_name: {(x, y)} }
        self.groups: dict[str, set[tuple[int, int]]] = defaultdict(set)

        # nodes from all groups in one set.
        self.all_groups: set[tuple[int, int]] = set()

        # { ((start_x, start_y), (end_x, end_y)) }  start < end
        self.forbidden_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()

        if text is None:
            lines: list[str] = []
        else:
            lines = text.splitlines()
            self.width = len(lines[0]) // 2
            self.height = len(lines) // 2
        for x in range(self.width):
            for y in range(self.height):
                self.graph.add_node((x, y))
                if text is not None:
                    wall_above = lines[y*2][x*2+1] != ' '
                    wall_to_left = lines[y*2+1][x*2] != ' '
                    if not wall_above:
                        self.graph.add_edge((x, y), (x, y-1))
                    if not wall_to_left:
                        self.graph.add_edge((x, y), (x-1, y))


    def display(self, show_groups: bool = False) -> str:
        lines = ['+-'*self.width + '+']
        for y in range(self.height):
            line = ['|']
            next_line = ['+']
            for x in range(self.width):
                node = (x, y)
                right_node = (x+1, y)
                has_wall_to_right = not self.graph.has_edge(node, right_node)
                below_node = (x, y + 1)
                has_wall_below = not self.graph.has_edge(node, below_node)
                if not show_groups:
                    line.append(' ')
                else:
                    for name, nodes in self.groups.items():
                        if node in nodes:
                            line.append(name[0])
                            break
                    else:
                        line.append(' ')
                if has_wall_below:
                    if self.is_forbidden_edge(node, below_node):
                        next_line.append('=')
                    else:
                        next_line.append('-')
                else:
                    next_line.append(' ')
                if has_wall_to_right:
                    if self.is_forbidden_edge(node, right_node):
                        line.append(':')
                    else:
                        line.append('|')
                else:
                    line.append(' ')
                next_line.append('+')
            lines.append(''.join(line))
            lines.append(''.join(next_line))
        return '\n'.join(lines)

    def add_to_group(self, x: int, y: int, group_name: str) -> None:
        node = (x, y)
        group_nodes = self.groups[group_name]
        group_nodes.add(node)
        self.all_groups.add(node)

    def get_group(self, group_name: str) -> set[tuple[int, int]]:
        return self.groups[group_name]

    def add_chamber(self, x: float, y: float, group_name: str) -> None:
        g = 1.665  # growth factor for radius to inner edge
        min_x = round(x - self.chamber_radius*g)
        max_x = round(x + self.chamber_radius*g)
        min_y = round(y - self.chamber_radius*g)
        max_y = round(y + self.chamber_radius*g)
        for x2 in range(min_x, max_x+1):
            for y2 in range(min_y, max_y+1):
                distance = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)
                if self.chamber_radius*g < distance:
                    # (x2, y2) is not inside the chamber.
                    continue
                self.add_to_group(x2, y2, group_name)
                if math.sqrt((x2+1-x)**2 + (y2-y)**2) < self.chamber_radius*g:
                    # right neighbour is also inside the chamber.
                    self.graph.add_edge((x2, y2), (x2+1, y2))
                if math.sqrt((x2-x)**2 + (y2+1-y)**2) < self.chamber_radius*g:
                    # lower neighbour is also inside the chamber.
                    self.graph.add_edge((x2, y2), (x2, y2+1))

        for x2, y2 in ((x-6, y-1), (x-6, y-2), (x-6, y-3), (x-4, y-5)):
            self.forbid_edge((round(x2), round(y2)),
                             (round(x2+1), round(y2)))
            self.forbid_edge((round(y2), round(x2)),
                             (round(y2), round(x2+1)))
            self.forbid_edge((round(2*x-x2), round(y2)),
                             (round(2*x-x2-1), round(y2)))
            self.forbid_edge((round(y2), round(2*x-x2)),
                             (round(y2), round(2*x-x2-1)))
            self.forbid_edge((round(x2), round(2*y-y2)),
                             (round(x2+1), round(2*y-y2)))
            self.forbid_edge((round(2*y-y2), round(x2)),
                             (round(2*y-y2), round(x2+1)))
            self.forbid_edge((round(2*x-x2), round(2*y-y2)),
                             (round(2*x-x2-1), round(2*y-y2)))
            self.forbid_edge((round(2*y-y2), round(2*x-x2)),
                             (round(2*y-y2), round(2*x-x2-1)))

        self.chambers.append((x, y, group_name))

    def draw(self, drawing: Drawing) -> None:
        scale = self.scale
        stroke_width = round(scale / 5)
        line_style = dict(stroke='black',
                          stroke_width=stroke_width,
                          stroke_linecap='round')
        drawing.add(drawing.line(
            (self.offset_x, self.offset_y),
            (self.offset_x + scale*2, self.offset_y),
            **line_style))
        drawing.add(drawing.line(
            (self.offset_x + scale*3, self.offset_y),
            (self.offset_x + scale*self.width, self.offset_y),
            **line_style))
        drawing.add(drawing.line(
            (self.offset_x + scale*self.width, self.offset_y),
            (self.offset_x + scale*self.width,
             self.offset_y + scale*self.height),
            **line_style))
        drawing.add(drawing.line(
            (self.offset_x + scale*self.width,
             self.offset_y + scale*self.height),
            (self.offset_x + scale*(self.width-2),
             self.offset_y + scale*self.height),
            **line_style))
        drawing.add(drawing.line(
            (self.offset_x + scale*(self.width-3),
             self.offset_y + scale*self.height),
            (self.offset_x, self.offset_y + scale*self.height),
            **line_style))
        drawing.add(drawing.line(
            (self.offset_x, self.offset_y + scale*self.height),
            (self.offset_x, self.offset_y),
            **line_style))
        drawing.add(drawing.text(Maze.ARROW,
                                 x=[self.offset_x +
                                    round(2.5*scale)],
                                 y=[self.offset_y - stroke_width +
                                    round(0.83*scale)],
                                 text_anchor='middle',
                                 font_family='Noto Sans Mono',
                                 font_size=self.scale))
        drawing.add(drawing.text(Maze.ARROW,
                                 x=[self.offset_x +
                                    round((self.width - 2.5)*scale)],
                                 y=[self.offset_y + stroke_width +
                                    round((self.height - 0.17)*scale)],
                                 text_anchor='middle',
                                 font_family='Noto Sans Mono',
                                 font_size=self.scale))

        for x in range(self.width):
            for y in range(self.height):
                if y < self.height - 1 and not self.graph.has_edge((x, y),
                                                                   (x, y+1)):
                    drawing.add(drawing.line((self.offset_x + scale * x,
                                              self.offset_y + scale * (y + 1)),
                                             (self.offset_x + scale * (x + 1),
                                              self.offset_y + scale * (y + 1)),
                                             **line_style))
                if x < self.width - 1 and not self.graph.has_edge((x, y),
                                                                  (x+1, y)):
                    drawing.add(drawing.line((self.offset_x + scale * (x + 1),
                                              self.offset_y + scale * y),
                                             (self.offset_x + scale * (x + 1),
                                              self.offset_y + scale * (y + 1)),
                                             **line_style))

        for x, y, group_name in self.chambers:
            drawing.add(drawing.text(group_name[0],
                                     x=[round((x+0.5)*scale+self.offset_x)],
                                     y=[round((y-2.5)*scale+self.offset_y)],
                                     text_anchor='middle',
                                     font_family='FredokaOne',
                                     font_size=2.5*scale))
            centre_x = round((x + 0.5) * scale + self.offset_x)
            centre_y = round((y + 0.5) * scale + self.offset_y)
            theta = 6
            draw_arcs((centre_x, centre_y),
                      round(self.chamber_radius*1.543*scale),
                      [
                          theta, 45-theta,
                          45+theta, 90-theta,
                          90+theta, 135-theta,
                          135+theta, 180-theta,
                          180+theta, 225-theta,
                          225+theta, 270-theta,
                          270+theta, 315-theta,
                          315+theta, 360-theta],
                      drawing,
                      fill='none',
                      **line_style)
            tangram = self.tangrams.get(group_name)
            if tangram is None:
                continue
            bounds = tangram.bounds
            tangram.translate(round(centre_x - drawing['width']//2 -
                                    bounds[0] - tangram.width/2),
                              round(-centre_y+drawing['height']*0.485 -
                                    bounds[1]-tangram.height/2))
            tangram.draw(drawing)

    def draw_header(self, drawing: Drawing) -> None:
        for x, y, line in ((self.offset_x + round(1.5*self.scale),
                            self.offset_y - round(3*self.scale),
                            'Use a'),
                           (self.offset_x + round(11.5*self.scale),
                            self.offset_y - round(3*self.scale),
                            'to guide you through this maze. What secret word does'),
                           (self.offset_x + round(11.5*self.scale),
                            self.offset_y - round(1.5*self.scale),
                            'the maze turn these letters into?')):
            drawing.add(drawing.text(line,
                                     x=[x],
                                     y=[y],
                                     font_family='FredokaOne',
                                     font_size=round(1.5*self.scale)))
        tangram = Tangram(round(self.scale*5), gap=5)
        tangram.add(tangram.t4a)
        tangram.t4a.rotate(45)
        tangram.add(tangram.t4b)
        tangram.t4b.rotate(135)
        tangram.add(tangram.p)
        tangram.p.flip()
        tangram.p.rotate(45)
        tangram.p.anchor(tangram.t4a, 1, 1)
        tangram.add(tangram.t1a)
        tangram.t1a.rotate(-45)
        tangram.add(tangram.t1b)
        tangram.t1b.rotate(-135)
        tangram.t1b.anchor(tangram.t4b, 2, 1)
        tangram.add(tangram.s)
        tangram.s.rotate(45)
        tangram.s.anchor(tangram.t4a, 0, 2)
        tangram.add(tangram.t2)
        tangram.t2.rotate(90)
        tangram.t2.anchor(tangram.t1b, 2, 2)
        tangram.scale(0.9)
        tangram.translate(-drawing['width']//2, drawing['height']//2)
        tangram.translate(round(self.scale*9),
                          round(self.scale*-4))

        tangram.draw(drawing)
        drawing.add(drawing.text('\u2198',
                                   x=[self.offset_x + round(self.scale*9.94)],
                                   y=[self.offset_y - round(self.scale*1.1)],
                                   fill='white',
                                   text_anchor='middle',
                                   font_family='Noto Sans Mono',
                                   font_size=14))

    def random_walk(self,
                    new_group: str,
                    start_group: str,
                    target_group: str|None = None,
                    retries: int = 0) -> list[tuple[int, int]]:
        if target_group is None:
            target_nodes = self.all_groups
        else:
            target_nodes = self.get_group(target_group)
        if start_group not in self.groups:
            group_names = sorted(self.groups)
            raise ValueError(f'No group {start_group!r} in {group_names}.')
        start_nodes = list(self.get_group(start_group))
        good_start_nodes = []
        for node in start_nodes:
            if self.find_available_neighbours(node, self.graph, target_nodes):
                good_start_nodes.append(node)
        for retry_count in count():
            location = random.choice(good_start_nodes)
            steps = [location]
            new_graph = self.graph.copy()
            new_nodes = []
            while True:
                neighbours = self.find_available_neighbours(location,
                                                            new_graph,
                                                            target_nodes)
                if not neighbours:
                    # Dead end, fail!
                    steps.clear()
                    break

                # choose a random step
                neighbour = random.choice(neighbours)
                if neighbour in steps:
                    # We retraced a step from the random walk, fail!
                    steps.clear()
                    break

                steps.append(neighbour)
                new_graph.add_edge(location, neighbour)

                if neighbour in target_nodes:
                    # Success!
                    break
                if neighbour in self.all_groups:
                    # Hit a different group, fail!
                    steps.clear()
                    break

                new_nodes.append(neighbour)
                location = neighbour

            if steps:
                # Success!
                logger.info('Found a random walk from %s to %s after %d '
                            'retries.',
                            start_group,
                            target_group,
                            retry_count)
                self.graph = new_graph
                for x, y in new_nodes:
                    self.add_to_group(x, y, new_group)
                return steps

            # Failed. Should we retry?
            if retry_count >= retries:
                # No, return failure.
                logger.info('No random walk found from %s to %s after %d '
                            'retries.',
                            start_group,
                            target_group,
                            retry_count)
                return steps
        assert False, 'Should never fall out of the loop above.'

    def add_step(self,
                 start: tuple[int, int],
                 end: tuple[int, int],
                 group_name: str) -> None:
        self.graph.add_edge(start, end)
        for node in (start, end):
            if node not in self.all_groups:
                self.add_to_group(node[0], node[1], group_name)

    def fill(self) -> None:
        all_nodes = {(x, y)
                     for x in range(self.width)
                     for y in range(self.height)}
        for path_num in count():
            available_nodes = all_nodes - self.all_groups
            if not available_nodes:
                break

            x, y = random.choice(list(available_nodes))
            start_name = f'start{path_num}'
            self.add_to_group(x, y, start_name)
            path_name = f'path{path_num}'
            steps = self.random_walk(path_name, start_name, retries=1000)
            if not steps:
                raise RuntimeError('Failed to fill maze.')

    def find_available_neighbours(self,
                                  node: tuple[int, int],
                                  graph: Graph,
                                  target_nodes: set[tuple[int, int]]) -> list[Any]:
        """ Find all available neighbours for a given node.

        They must not already have a connection to node, and the connection must
        not be forbidden.
        """
        x, y = node
        neighbours = []
        for dx, dy in ((1, 0), (0, -1), (-1, 0), (0, 1)):
            neighbour = (x + dx, y + dy)
            if (graph.has_node(neighbour) and
                    not graph.has_edge(node, neighbour) and
                    not self.is_forbidden_edge(node, neighbour) and
                    (neighbour in target_nodes or
                     neighbour not in self.all_groups)):
                neighbours.append(neighbour)
        return neighbours

    def forbid_edge(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        start2, end2 = sorted((start, end))
        self.forbidden_edges.add((start2, end2))

    def is_forbidden_edge(self,
                          start: tuple[int, int],
                          end: tuple[int, int]) -> bool:
        start2, end2 = sorted((start, end))
        return (start2, end2) in self.forbidden_edges

    def add_tangram(self, tangram: Tangram, group_name: str) -> None:
        self.tangrams[group_name] = tangram

    def link_random_walks(self, targets: list[tuple[int, int]]) -> str:
        directions = {(1, 0): 'r', (0, -1): 'u', (-1, 0): 'l', (0, 1): 'd'}

        steps = []
        for i, target in enumerate(targets):
            self.add_to_group(*target, f'target{i}')
            if i > 0:
                leg_steps = self.random_walk(f'leg{i}',
                                             f'target{i - 1}',
                                             f'target{i}',
                                          retries=100)
                if i > 1 and leg_steps:
                    leg_steps.pop(0)
                steps.extend(leg_steps)
        step_directions = []
        for start, end in zip(steps, steps[1:]):
            x1, y1 = start
            x2, y2 = end
            step_direction = directions[(x2-x1, y2-y1)]
            step_directions.append(step_direction)

        return ''.join(step_directions)

    def add_path(self, start: tuple[int, int], step_directions: str):
        (x, y) = node = start
        for heading in step_directions:
            if heading == 'l':
                x -= 1
            elif heading == 'r':
                x += 1
            elif heading == 'u':
                y -= 1
            elif heading == 'd':
                y += 1
            next_node = (x, y)
            self.add_step(node, next_node, 'leg')
            node = next_node


def draw_arcs(centre: tuple[float, float],
              r: float,
              angles: list[float],
              drawing: Drawing,
              **kwargs) -> None:
    x0, y0 = centre
    path_steps = []
    for i, (theta1, theta2) in enumerate(zip(
            angles,
            angles[1:])):
        x1 = x0 + math.cos(theta1 * math.pi / 180) * r
        y1 = y0 - math.sin(theta1 * math.pi / 180) * r
        x2 = x0 + math.cos(theta2 * math.pi / 180) * r
        y2 = y0 - math.sin(theta2 * math.pi / 180) * r
        if i == 0:
            path_steps.append(f'M {x1} {y1}')

        if i % 2 == 0:
            path_steps.append(f'a {r} {r} 0 0 0 {x2-x1} {y2-y1}')
        else:
            path_steps.append(f'm {x2-x1} {y2-y1}')

    drawing.add(drawing.path(' '.join(path_steps),
                             **kwargs))


def add_tangrams(maze: Maze):
    gap = 0
    tangram = Tangram(50, gap)
    maze.add_tangram(tangram, 'T')
    layout_ship(tangram)

    tangram = Tangram(50, gap)
    maze.add_tangram(tangram, 'R')
    layout_fat_axe(tangram)

    tangram = Tangram(50, gap)
    maze.add_tangram(tangram, 'S')
    layout_top(tangram)

    tangram = Tangram(50, gap)
    maze.add_tangram(tangram, 'C')
    layout_saw(tangram)

    tangram = Tangram(50, gap)
    maze.add_tangram(tangram, 'E')
    layout_thin_axe(tangram)

    tangram = Tangram(50, gap)
    maze.add_tangram(tangram, 'A')
    layout_tug(tangram)


def layout_empty(tangram: Tangram):
    tangram.translate(0, 0)


def layout_tug(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-90)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t4a, 1, 1)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(90)
    tangram.t4b.anchor(tangram.s)
    tangram.add(tangram.t2)
    tangram.t2.rotate(45)
    tangram.t2.anchor(tangram.t4b, 2)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(-90)
    tangram.t1a.anchor(tangram.t4b, 1, 2)
    tangram.add(tangram.p)
    tangram.p.rotate(45)
    tangram.p.anchor(tangram.t4b, 1)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(-135)
    tangram.t1b.anchor(tangram.p, 1)


def layout_thin_axe(tangram: Tangram):
    tangram.add(tangram.s)
    tangram.add(tangram.t1a)
    tangram.t1a.anchor(tangram.s, 3)
    tangram.add(tangram.p)
    tangram.p.flip()
    tangram.p.rotate(-90)
    tangram.p.anchor(tangram.t1a, 1, 1)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(180)
    tangram.t1b.anchor(tangram.p, 0, 2)
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-135)
    tangram.t4a.anchor(tangram.t1b, 1, 0)
    tangram.t4a.translate(0, tangram.t4a.height)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(45)
    tangram.t4b.anchor(tangram.t4a, 2)
    tangram.add(tangram.t2)
    tangram.t2.rotate(90)
    tangram.t2.anchor(tangram.t4b, 0, 2)
    tangram.flip()
    tangram.rotate(180)


def layout_saw(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(90)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(90)
    tangram.t4b.anchor(tangram.t4a, 0, 1)
    tangram.add(tangram.p)
    tangram.p.flip()
    tangram.p.anchor(tangram.t4a, 0, 1)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t4b, 0, 2)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(90)
    tangram.t1a.anchor(tangram.s)
    tangram.add(tangram.t2)
    tangram.t2.rotate(-135)
    tangram.t2.anchor(tangram.s)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(180)
    tangram.t1b.anchor(tangram.s, 1)
    tangram.rotate(270)


def layout_top(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-90)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(180)
    tangram.add(tangram.p)
    tangram.p.anchor(tangram.t4a, 2, 1)
    tangram.add(tangram.t2)
    tangram.t2.rotate(-135)
    tangram.t2.anchor(tangram.p, 3, 0)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(90)
    tangram.t1a.anchor(tangram.t2, 1)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(-90)
    tangram.t1b.anchor(tangram.t2, 0, 2)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t1b, 0, 0)
    tangram.s.translate(tangram.s.width / 2, 0)


def layout_fat_axe(tangram: Tangram):
    tangram.add(tangram.t4a)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(180)
    tangram.t4b.anchor(tangram.t4a, 2, 1)
    tangram.add(tangram.p)
    tangram.p.rotate(90)
    tangram.p.anchor(tangram.t4a, 2, 1)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(90)
    tangram.t1a.anchor(tangram.p, 2, 1)
    tangram.add(tangram.t2)
    tangram.t2.rotate(-45)
    tangram.t2.anchor(tangram.p, 3, 0)
    tangram.add(tangram.t1b)
    tangram.t1b.anchor(tangram.t2, 0, 2)
    tangram.add(tangram.s)
    tangram.s.anchor(tangram.t1b, 0, 3)
    tangram.flip()
    tangram.rotate(180)


def layout_ship(tangram: Tangram):
    tangram.add(tangram.t2)
    tangram.t2.rotate(-45)
    tangram.add(tangram.t4a)
    tangram.t4a.rotate(-225)
    tangram.t4a.anchor(tangram.t2, 0, 1)
    tangram.add(tangram.t4b)
    tangram.t4b.rotate(90)
    tangram.t4b.anchor(tangram.t4a, 2, 0)
    tangram.add(tangram.s)
    tangram.s.rotate(45)
    tangram.s.anchor(tangram.t4a, 0, 2)
    tangram.add(tangram.t1a)
    tangram.t1a.rotate(-135)
    tangram.t1a.anchor(tangram.t4b, 0, 1)
    tangram.add(tangram.p)
    tangram.p.rotate(45)
    tangram.p.anchor(tangram.s, 0, 0)
    tangram.p.translate(0, -tangram.p.height)
    tangram.add(tangram.t1b)
    tangram.t1b.rotate(45)
    tangram.t1b.anchor(tangram.p, 2, 1)


def write_hint_files():
    hint_folder = Path(__file__).with_name('hints')
    hint_folder.mkdir(exist_ok=True)
    pdf_path = hint_folder / 'hints.pdf'
    story: list[Flowable] = []
    doc = SimpleDocTemplate(str(pdf_path),
                            author='Don Kirkby',
                            pagesize=pagesizes.landscape(pagesizes.letter),
                            title='Tangram Hints')
    add_hint_set(layout_fat_axe, hint_folder, story, 'fat_axe')
    add_hint_set(layout_thin_axe, hint_folder, story, 'thin_axe', 't4a')
    add_hint_set(layout_saw, hint_folder, story, 'saw')
    add_hint_set(layout_tug, hint_folder, story, 'tug', 't4a')
    add_hint_set(layout_top, hint_folder, story, 'top')
    add_hint_set(layout_ship, hint_folder, story, 'ship')
    doc.build(story)


def add_hint_set(layout_function: Callable[..., None],
                 hint_folder: Path,
                 story: list[Flowable],
                 set_name: str,
                 highlight: str='t4b'):
    scale = 372
    gap = scale * 0.03
    hint1 = Tangram(scale)
    layout_function(hint1)
    add_hint(hint1, hint_folder / f'{set_name}_hint1.svg', story)

    hint2: Tangram = SingleHint(scale, gap, highlight)
    layout_function(hint2)
    add_hint(hint2, hint_folder / f'{set_name}_hint2.svg', story)

    hint3 = Tangram(scale, gap)
    layout_function(hint3)
    add_hint(hint3, hint_folder / f'{set_name}_hint3.svg', story)


def add_hint(hint: Tangram, hint_path: Path, story: list[Flowable]):
    left, bottom, right, top = hint.bounds
    hint.translate(-left - (right-left)/2, -bottom - (top-bottom)/2)
    # if (right - left) > pagesizes.letter[1]:
    #     raise RuntimeError(
    #         f'Hint is wider than US letter landscape: {hint_path.name}')

    drawing = svgwrite.Drawing(size=(right-left, top-bottom))
    hint.draw(drawing)
    svg_text = drawing.tostring()
    hint_path.write_text(svg_text)

    svg_bytes = svg_text.encode()
    pdf_drawing = svg2rlg(BytesIO(svg_bytes))
    assert pdf_drawing is not None
    if story:
        story.append(PageBreak())
    story.append(pdf_drawing)


def main() -> None:
    random.seed(0)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    logger.info('Starting.')
    write_hint_files()
    maze = Maze(width=77, height=55)
    maze.scale = 15
    maze.offset_x = 10
    maze.offset_y = 100
    group_names = ('TRA', 'CES')
    for y, line in enumerate(group_names):
        for x, group_name in enumerate(line):
            maze.add_chamber(22*x+16, 22*y+16, group_name)
    text_legs = {
        # start - R
        (2, 0): 'ddrrururddlddrruuuurdrddrdrrruluuurrrdrdrrrrdddrdrurdruurrdrd'
                 'ddddrrurrrrrddldr',
        # R - E
        (44, 16): 'drdlddldddrddrdldddruurdrdrdllllddllllll',
        # E - C
        (34, 42): 'llluuluulurrurullllulddlllluulll',
        # C - A
        (22, 38): 'drdldrdruurrdrdddddrrurrrururdrdddrrrdldrruurururrrruuluuuu'
                  'rruruluururrrurrulluuruuuuuruuluuuulurrrdrdrr',
        # A - S
        (60, 22): 'rdrrurrrrdldlldrdldrdddrdllddd',
        # S - T
        (60, 32): 'luldlllddllldrdrdllldrdrdrddllluldldrddddllllluldldddlluldl'
                  'llluldlullddlullllluulldluldldllllluuullluulululuulldluurru'
                  'lluurulurruruluuuluuurrurulluluuruurrr',
        # T - end
        (10, 16): 'uluruulldlldrddddlddldlldrrrdrdddllllddrrrdrdddluldllllddrdl'
                  'ldrdrrdldddrdrrdrrdrdddrrdldrddrdrdldrrrrulurrrddrruruurdrur'
                  'rdrdldrruuurrrrdrdlldrrrrrururrrurrrdlldrrdrurdrruurdruurrdr'
                  'ddrrurrrrrdrrululluluuruurrrdrrdddddrrrdrrururrurrrdlldrrdrr',

        # red herrings
        # E - A
        (42, 34): 'rruruurrrruuruluuuruluuurululuulurrurdrrrr',
        # E - T
        (34, 34): 'llllluluuluululluruuldluuldlluluuruu',
        # T - C
        (16, 22): 'dldldldddrdlldldrrdrurrd',
        # A - end
        (64, 20): 'rdrrruuurdrdrdddluuldldrdddlddrrddldrrdrddrdrdlddrrrddddlldr'
                  'rdlddrdllldrdrrdddlddl',
        # S - end
        (60, 44): 'ddrdrrdruurrdrddddruurrrrrddrddd',

        # doorways
        # T NW
        (12, 12): 'uuldlllldluuluuldlu',
        # T N
        (16, 10): 'lllullldllluuulu',
        # T NE
        (20, 12): 'rururrdrrrrdrdrdrdldrr',
        # T E
        (22, 16): 'drrurddrurrdrrurrddldldrrrur',
        # R N
        (38, 10): 'llluullluldluuuluuuu',
        # R NE
        (42, 12): 'urrdrrrdrurdrdrdrruruurr',
        # R S
        (38, 22): 'llddllllldrdrurrdldddru',
        # R SE
        (42, 20): 'ddlddldrdldrdddllu',
        # A N
        (60, 10): 'ululuuullllu',
        # A NE
        (64, 12): 'rruulluldlluuruuldlluuur',
        # A E
        (66, 16): 'uurururuluururrdrdldrruuurdrruuullldrr',
        # C NW
        (12, 34): 'luuluuururuuuuuluu',
        # C W
        (10, 38): 'luruu',
        # C SW
        (12, 42): 'd',
        # C S
        (16, 44): 'drdrurrdlddd',
        # C SE
        (20, 42): 'drdrurrddddrur',
        # E W
        (32, 38): 'ldrdd',
        # E S
        (38, 44): 'llddru',
        # E SE
        (42, 42): 'drdllldldlu',
        # E E
        (44, 38): 'uuurururrurd',
        # S E
        (66, 38): 'uuruuluururuluuuuurul',
        # S NW
        (56, 34): 'u',
        # S W
        (54, 38): 'd',
        # S SW
        (56, 42): 'dddldldddldlldlululdlldlldluld',
        # S SE
        (64, 42): 'dddrururuluururrdrdldrruuur',
    }
    for start, leg_text in text_legs.items():
        maze.add_path(start, leg_text)

    # try:
    #     logger.info(maze.link_random_walks([(58, 58), (64, 58)]))
    # except IndexError:
    #     logger.error('Dead end in random walk.')

    maze.fill()
    add_tangrams(maze)
    image_path = Path(__file__).with_name(
        f'maze.svg')
    width = 1180
    height = 950
    drawing = Drawing(size=(width, height))
    maze.draw(drawing)
    # maze.draw_header(drawing)
    if __name__ == '__live_coding__':
        LiveSvg(drawing.tostring()).display((-width*0.375, height*0.4))
    else:
        image_path.write_text(drawing.tostring())


if __name__ in ('__main__', '__live_coding__'):
    main()
