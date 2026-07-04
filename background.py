import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Background:
    """Parallax starfield background."""
    
    def __init__(self) -> None:
        # Three layers of stars for parallax effect
        # Far layer - slow, dim, small
        self.far_stars = self._generate_stars(80, 1, 50, (130, 130, 160))
        # Mid layer - medium speed, brightness, size
        self.mid_stars = self._generate_stars(50, 2, 80, (180, 180, 200))
        # Near layer - fast, bright, large
        self.near_stars = self._generate_stars(30, 4, 120, (230, 230, 255))
        
        # Layer speeds (pixels per second) - negative = moves opposite to player
        self.far_speed = 10
        self.mid_speed = 25
        self.near_speed = 50
        
        # Offsets for scrolling
        self.far_offset = pygame.Vector2(0, 0)
        self.mid_offset = pygame.Vector2(0, 0)
        self.near_offset = pygame.Vector2(0, 0)
    
    def _generate_stars(self, count: int, size: int, speed_factor: int, color: tuple) -> list:
        """Generate star positions and properties."""
        stars = []
        for _ in range(count):
            stars.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "size": random.uniform(0.5, size / 10.0),
                "brightness": random.uniform(0.3, 1.0),
                "twinkle_speed": random.uniform(0.5, 2.0),
                "twinkle_phase": random.uniform(0, 6.28),
                "color": color,
            })
        return stars
    
    def _update_layer(self, stars: list, offset: pygame.Vector2, speed: float, dt: float, player_vel: pygame.Vector2) -> None:
        """Update star positions for one layer."""
        # Move opposite to player velocity for parallax
        if player_vel.length() > 0:
            # Normalize player velocity and apply layer speed
            move_dir = player_vel.normalize() * speed * dt
            offset -= move_dir
        
        # Wrap offset
        offset.x %= SCREEN_WIDTH
        offset.y %= SCREEN_HEIGHT
    
    def update(self, dt: float, player_velocity: pygame.Vector2) -> None:
        """Update all star layers."""
        self._update_layer(self.far_stars, self.far_offset, self.far_speed, dt, player_velocity)
        self._update_layer(self.mid_stars, self.mid_offset, self.mid_speed, dt, player_velocity)
        self._update_layer(self.near_stars, self.near_offset, self.near_speed, dt, player_velocity)
    
    def _draw_layer(self, surface: pygame.Surface, stars: list, offset: pygame.Vector2, base_color: tuple) -> None:
        """Draw one layer of stars with wrapping."""
        for star in stars:
            # Calculate wrapped position
            x = (star["x"] + offset.x) % SCREEN_WIDTH
            y = (star["y"] + offset.y) % SCREEN_HEIGHT
            
            # Twinkle effect
            twinkle = 0.5 + 0.5 * abs(pygame.math.Vector2(1, 0).angle_to(pygame.Vector2(
                pygame.time.get_ticks() * 0.001 * star["twinkle_speed"] + star["twinkle_phase"], 0
            )) / 180.0)
            
            brightness = star["brightness"] * twinkle
            color = tuple(int(c * brightness) for c in star["color"])
            size = max(1, int(star["size"] * brightness))
            
            pygame.draw.circle(surface, color, (int(x), int(y)), size)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all star layers (far to near)."""
        self._draw_layer(surface, self.far_stars, self.far_offset, (100, 100, 120))
        self._draw_layer(surface, self.mid_stars, self.mid_offset, (150, 150, 170))
        self._draw_layer(surface, self.near_stars, self.near_offset, (200, 200, 220))