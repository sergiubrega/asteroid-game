import random
import pygame
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Particle(CircleShape):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float, color: tuple[int, int, int], velocity: pygame.Vector2, life: float = 0.5) -> None:
        super().__init__(x, y, radius)
        self.velocity = velocity
        self.color = color
        self.life = life
        self.max_life = life
        self.alpha = 255

    def draw(self, screen: pygame.Surface) -> None:
        # Fade out over life
        self.alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, self.alpha)
        # Create a surface for alpha blending
        particle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.radius, self.radius), self.radius)
        screen.blit(particle_surface, (self.position.x - self.radius, self.position.y - self.radius))

    def update(self, dt: float) -> None:
        super().update(dt)
        self.life -= dt
        # Shrink as life decreases
        self.radius = max(0.5, self.radius * (self.life / self.max_life))
        if self.life <= 0:
            self.kill()


def spawn_explosion(x: float, y: float, color: tuple[int, int, int] = (255, 165, 0), count: int = 12) -> None:
    """Spawn explosion particles at position."""
    for _ in range(count):
        angle = random.uniform(0, 360)
        speed = random.uniform(50, 200)
        velocity = pygame.Vector2(0, 1).rotate(angle) * speed
        radius = random.uniform(2, 5)
        life = random.uniform(0.3, 0.8)
        # Color variation
        r = min(255, color[0] + random.randint(-30, 30))
        g = min(255, color[1] + random.randint(-30, 30))
        b = min(255, color[2] + random.randint(-30, 30))
        Particle(x, y, radius, (r, g, b), velocity, life)