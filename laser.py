import pygame
from circleshape import CircleShape
from constants import LINE_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT


class Laser(CircleShape):
    """Persistent laser beam that damages everything in its path."""
    
    def __init__(self, x: float, y: float, rotation: float, stats: dict, ship_velocity: pygame.Vector2):
        # Use a small radius for collision purposes
        super().__init__(x, y, 2)
        self.rotation = rotation
        self.timer = stats["extra"]["duration"]
        self.width = stats["extra"]["width"]
        self.damage = stats["damage"]
        self.color = (255, 50, 50)  # Red laser
        self.beam_speed = stats["speed"]
        
        # Track with ship's velocity
        self.velocity = ship_velocity.copy()
        
        # Calculate end point
        forward = pygame.Vector2(0, 1).rotate(rotation)
        self.end_pos = self.position + forward * self.beam_speed * self.timer
        
        # Add to containers
        if hasattr(Laser, 'containers'):
            for container in Laser.containers:
                container.add(self)

    def update(self, dt: float, asteroids=None) -> None:
        self.timer -= dt
        
        # Handle hit flash timer
        if hasattr(self, 'kill_timer') and self.kill_timer > 0:
            self.kill_timer -= dt
            if self.kill_timer <= 0:
                self.kill()
                return
        
        if self.timer <= 0:
            self.kill()
            return
        
        # Move with ship velocity
        self.position += self.velocity * dt
        
        # Recalculate end point based on current position
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.end_pos = self.position + forward * self.beam_speed * self.timer
        
        # Check collision with asteroids along the beam
        if asteroids:
            self.check_collision(asteroids)

    def check_collision(self, asteroids):
        """Check if any asteroid intersects the laser beam."""
        for asteroid in asteroids:
            if self._line_circle_collision(self.position, self.end_pos, asteroid.position, asteroid.radius):
                # Return the hit asteroid so caller can handle score/explosion
                hit_asteroid = asteroid
                asteroid.split()
                # Don't kill instantly - add a hit flash timer
                self.hit_flash = 0.05  # 50ms flash
                self.kill_timer = self.hit_flash
                return hit_asteroid
        return None

    def _line_circle_collision(self, p1, p2, center, radius):
        """Check if line segment p1-p2 intersects circle at center with radius."""
        # Vector from p1 to p2
        line_vec = p2 - p1
        line_len = line_vec.length()
        if line_len == 0:
            return center.distance_to(p1) <= radius
        
        line_dir = line_vec / line_len
        
        # Vector from p1 to circle center
        to_center = center - p1
        
        # Project to_center onto line
        projection = to_center.dot(line_dir)
        
        # Clamp to segment
        projection = max(0, min(line_len, projection))
        
        # Closest point on segment
        closest = p1 + line_dir * projection
        
        return closest.distance_to(center) <= radius

    def draw(self, screen: pygame.Surface) -> None:
        # Fade out as timer decreases
        alpha = int(255 * (self.timer / 0.2))
        
        # Hit flash - bright white/yellow when hitting
        if hasattr(self, 'kill_timer') and self.kill_timer > 0:
            flash_alpha = int(255 * (self.kill_timer / 0.05))
            flash_color = (255, 255, 100, flash_alpha)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(flash_surface, flash_color, self.position, self.end_pos, self.width + 6)
            screen.blit(flash_surface, (0, 0))
            # Also draw core flash
            pygame.draw.line(screen, (255, 255, 200), self.position, self.end_pos, self.width + 2)
        
        # Draw glow layers
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for w in range(self.width + 2, self.width + 6, 2):
            glow_alpha = max(50, alpha // (w - self.width + 1))
            glow_color = (*self.color[:3], glow_alpha)
            pygame.draw.line(glow_surface, glow_color, self.position, self.end_pos, w)
        screen.blit(glow_surface, (0, 0))
        
        # Draw core beam
        pygame.draw.line(screen, self.color, self.position, self.end_pos, self.width)