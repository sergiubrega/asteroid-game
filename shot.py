import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, LINE_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.damage = 1
        self.turn_rate = 0
        self.is_homing = False

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float, asteroids=None) -> None:
        # Homing behavior
        if self.is_homing and asteroids:
            target = self._find_nearest_asteroid(asteroids)
            if target:
                self._rotate_toward(target, dt)
        
        # Shots don't wrap - they die off-screen
        self.position += self.velocity * dt
        if (self.position.x < -self.radius or self.position.x > SCREEN_WIDTH + self.radius or
            self.position.y < -self.radius or self.position.y > SCREEN_HEIGHT + self.radius):
            self.kill()
    
    def _find_nearest_asteroid(self, asteroids):
        nearest = None
        min_dist = float('inf')
        for asteroid in asteroids:
            dist = self.position.distance_to(asteroid.position)
            if dist < min_dist:
                min_dist = dist
                nearest = asteroid
        return nearest
    
    def _rotate_toward(self, target, dt):
        # Calculate angle to target
        to_target = target.position - self.position
        if to_target.length() > 0:
            # Angle from forward (down) to target direction
            forward = pygame.Vector2(0, 1)
            target_angle = forward.angle_to(to_target)
            current_angle = forward.angle_to(self.velocity)
            # Find shortest rotation direction
            diff = (target_angle - current_angle + 180) % 360 - 180
            max_turn = self.turn_rate * dt
            if abs(diff) > max_turn:
                diff = max_turn if diff > 0 else -max_turn
            # Rotate velocity
            self.velocity = self.velocity.rotate(diff)