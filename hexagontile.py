import pygame
import math
import random
from typing import List
from typing import Tuple

def get_random_colour(min_=150, max_=255) -> Tuple[int, ...]:
    return tuple(random.choices(list(range(min_, max_)), k=3))

class HexagonTile:
    
    def __init__(self, position, radius, number):
        self.radius = radius
        self.number = number
        #self.radius = 50
        self.position = position
        self.colour = get_random_colour()
        self.vertices = self.compute_vertices()
        self.max_highlight_ticks = 15
        self.highlight_tick = 0
        self.highlight_offset = 3


    
    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        # pylint: disable=invalid-name
        x, y = self.position
        half_radius = self.radius / 2
        minimal_radius = self.minimal_radius
        return [
            (x, y),
            (x - minimal_radius, y + half_radius),
            (x - minimal_radius, y + 3 * half_radius),
            (x, y + 2 * self.radius),
            (x + minimal_radius, y + 3 * half_radius),
            (x + minimal_radius, y + half_radius),
        ]
    
    def compute_neighbours(self, hexagons):
        """Returns hexagons whose centres are two minimal radiuses away from self.centre"""
        # could cache results for performance
        return [hexagon for hexagon in hexagons if self.is_neighbour(hexagon)]
    
    def hide_tiles(hexagons):
        """
        Mark all tiles as a hidden tile
        """
        for hexagon in hexagons:
            hexagon.number = 7
        return hexagons

    def collide_with_point(self, point: Tuple[float, float]) -> bool:
        """Returns True if distance from centre to point is less than horizontal_length"""
        return math.dist(point, self.centre) < self.minimal_radius

    def is_neighbour(self, hexagon) -> bool:
        """Returns True if hexagon centre is approximately
        2 minimal radiuses away from own centre
        """
        distance = math.dist(hexagon.centre, self.centre)
        return math.isclose(distance, 2 * self.minimal_radius, rel_tol=0.05)
    
    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""
        pygame.draw.polygon(screen, self.highlight_colour, self.vertices)

    @property
    def centre(self) -> Tuple[float, float]:
        """Centre of the hexagon"""
        x, y = self.position 
        return (x, y + self.radius)

    @property
    def minimal_radius(self) -> float:
        """Horizontal length of the hexagon"""
        return self.radius * math.cos(math.radians(30))
    
