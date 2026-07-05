import random
import pygame
from circleshape import CircleShape
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SHIELD_RADIUS, SHIELD_COLOR, 
    SHIELD_GLOW_COLOR, SHIELD_DURATION,
    SPEED_BOOST_RADIUS, SPEED_BOOST_COLOR, SPEED_BOOST_GLOW_COLOR, SPEED_BOOST_DURATION,
    SPEED_MULTIPLIER
)


class PowerUp(CircleShape):
    """Base power-up class. Falls slowly and can be collected by player."""
    
    def __init__(self, x: float, y: float, radius: float, color: tuple, powerup_type: str) -> None:
        super().__init__(x, y, radius)
        self.color = color
        self.powerup_type = powerup_type
        self.velocity = pygame.Vector2(0, random.uniform(30, 60))  # slow downward drift
        self.rotation = 0
        self.rotation_speed = random.uniform(30, 60)
        self.pulse_timer = 0
        
    def draw(self, screen: pygame.Surface) -> None:
        # Pulsing glow effect
        pulse = abs(pygame.math.Vector2(1, 0).angle_to(
            pygame.Vector2(pygame.time.get_ticks() * 0.003, 0)
        )) / 180.0
        glow_size = int(self.radius + 4 + pulse * 4)
        
        # Draw glow
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, SHIELD_GLOW_COLOR, (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (self.position.x - glow_size, self.position.y - glow_size))
        
        # Draw core circle
        pygame.draw.circle(screen, self.color, self.position, self.radius, 2)
        
        # Draw inner symbol based on type
        if self.powerup_type == "shield":
            # Shield icon - two arcs
            inner_radius = self.radius - 3
            pygame.draw.arc(screen, self.color, 
                          (self.position.x - inner_radius, self.position.y - inner_radius,
                           inner_radius * 2, inner_radius * 2),
                          0.5, 2.6, 2)
            pygame.draw.arc(screen, self.color,
                          (self.position.x - inner_radius, self.position.y - inner_radius,
                           inner_radius * 2, inner_radius * 2),
                          3.7, 5.8, 2)
    
    def update(self, dt: float, asteroids=None) -> None:
        super().update(dt)
        self.rotation += self.rotation_speed * dt
        
        # Kill if off screen (below)
        if self.position.y > SCREEN_HEIGHT + self.radius:
            self.kill()
    
    def apply_effect(self, player) -> None:
        """Override in subclasses to apply the power-up effect."""
        pass


class ShieldPowerUp(PowerUp):
    """Temporary invincibility shield for the player."""
    
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHIELD_RADIUS, SHIELD_COLOR, "shield")
    
    def apply_effect(self, player) -> None:
        player.activate_shield(SHIELD_DURATION)


class SpeedPowerUp(PowerUp):
    """Temporary speed boost for the player."""
    
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SPEED_BOOST_RADIUS, SPEED_BOOST_COLOR, "speed")
    
    def apply_effect(self, player) -> None:
        player.activate_speed_boost(SPEED_BOOST_DURATION)
    
    def draw(self, screen: pygame.Surface) -> None:
        # Pulsing glow effect
        pulse = abs(pygame.math.Vector2(1, 0).angle_to(
            pygame.Vector2(pygame.time.get_ticks() * 0.003, 0)
        )) / 180.0
        glow_size = int(self.radius + 4 + pulse * 4)
        
        # Draw glow
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, SPEED_BOOST_GLOW_COLOR, (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (self.position.x - glow_size, self.position.y - glow_size))
        
        # Draw core circle
        pygame.draw.circle(screen, self.color, self.position, self.radius, 2)
        
        # Draw inner symbol - lightning bolt
        inner_radius = self.radius - 3
        # Draw a simple lightning bolt
        center_x, center_y = self.position.x, self.position.y
        points = [
            (center_x, center_y - inner_radius),
            (center_x - 3, center_y - 2),
            (center_x + 2, center_y - 2),
            (center_x - 1, center_y + inner_radius - 2),
            (center_x + 3, center_y + 2),
            (center_x - 2, center_y + 2),
        ]
        pygame.draw.polygon(screen, self.color, points)