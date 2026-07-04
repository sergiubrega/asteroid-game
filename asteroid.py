import random
import math
import pygame
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from logger import log_event


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        # Generate lumpy shape vertices (cached for consistent appearance)
        self.vertices = self._generate_vertices(radius)
    
    def _generate_vertices(self, radius: float) -> list[pygame.Vector2]:
        """Generate irregular polygon vertices around a circle."""
        # Number of vertices - more for larger asteroids
        num_vertices = random.randint(8, 14)
        vertices = []
        
        for i in range(num_vertices):
            angle = (2 * math.pi * i) / num_vertices
            # Vary radius by 20-40% for lumpy look
            variance = random.uniform(0.6, 1.0)
            r = radius * variance
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            vertices.append(pygame.Vector2(x, y))
        
        return vertices
    
    def draw(self, screen: pygame.Surface) -> None:
        # Transform local vertices to world position
        world_vertices = [self.position + v for v in self.vertices]
        pygame.draw.polygon(screen, "white", world_vertices, LINE_WIDTH)

    def update(self, dt: float, asteroids=None) -> None:
        super().update(dt)

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            random_angle = random.uniform(20, 50)
            new_vector_1 = self.velocity.rotate(random_angle)
            new_vector_2 = self.velocity.rotate(-random_angle)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            new_asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
            new_asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)
            new_asteroid_1.velocity = new_vector_1 * 1.2
            new_asteroid_2.velocity = new_vector_2 * 1.2