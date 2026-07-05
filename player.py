import pygame
from circleshape import CircleShape
from shot import Shot
from laser import Laser
from constants import (
    PLAYER_ACCELERATION,
    PLAYER_DRAG,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    WEAPON_TYPES,
    WEAPON_STATS,
    WEAPON_COUNT,
)

def _closest_point_on_segment(p: pygame.Vector2, a: pygame.Vector2, b: pygame.Vector2) -> pygame.Vector2:
    """Return the closest point on line segment AB to point P."""
    ab = b - a
    t = (p - a).dot(ab) / ab.dot(ab) if ab.dot(ab) > 0 else 0
    t = max(0.0, min(1.0, t))
    return a + ab * t

def _point_in_triangle(p: pygame.Vector2, a: pygame.Vector2, b: pygame.Vector2, c: pygame.Vector2) -> bool:
    """Check if point P is inside triangle ABC using barycentric technique."""
    v0 = c - a
    v1 = b - a
    v2 = p - a
    dot00 = v0.dot(v0)
    dot01 = v0.dot(v1)
    dot02 = v0.dot(v2)
    dot11 = v1.dot(v1)
    dot12 = v1.dot(v2)
    inv_denom = 1.0 / (dot00 * dot11 - dot01 * dot01) if (dot00 * dot11 - dot01 * dot01) != 0 else 0
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    return (u >= 0) and (v >= 0) and (u + v <= 1)

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
        self.invulnerable_timer = 0
        self.shield_timer = 0.0
        self.shield_active = False
        self.weapon_index = 0
        self.weapon_type = WEAPON_TYPES[self.weapon_index]
  
    # in the Player class
    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        if self.invulnerable_timer <= 0 or int(self.invulnerable_timer * 10) % 2 == 0:
            pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)
        
        # Draw shield effect when active
        if self.shield_active:
            # Pulsing shield ring
            pulse = abs(pygame.math.Vector2(1, 0).angle_to(
                pygame.Vector2(pygame.time.get_ticks() * 0.005, 0)
            )) / 180.0
            shield_radius = int(self.radius * 1.8 + pulse * 6)
            alpha = int(100 + pulse * 100)
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 200, 255, alpha), (shield_radius, shield_radius), shield_radius, 2)
            screen.blit(shield_surface, (self.position.x - shield_radius, self.position.y - shield_radius))

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt: float, asteroids=None) -> None:
        keys = pygame.key.get_pressed()
        if self.shot_cooldown > 0:
            self.shot_cooldown -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
                self.shield_timer = 0.0
        self.velocity *= PLAYER_DRAG
        super().update(dt)

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt, 1)
        if keys[pygame.K_s]:
            self.move(dt, -1)
        if keys[pygame.K_SPACE]:
            self.shoot()
    
    def move(self, dt, direction=1):  # 1=forward, -1=backward
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        acceleration = forward * PLAYER_ACCELERATION * direction * dt
        self.velocity += acceleration
        # optional speed cap
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

    def shoot(self):
        if not self.shot_cooldown > 0:
            stats = WEAPON_STATS[self.weapon_type]
            self.shot_cooldown = stats["cooldown"]
            
            if self.weapon_type == "single":
                self._shoot_single(stats)
            elif self.weapon_type == "spread":
                self._shoot_spread(stats)
            elif self.weapon_type == "homing":
                self._shoot_homing(stats)
            elif self.weapon_type == "laser":
                self._shoot_laser(stats)

    def _shoot_single(self, stats):
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * stats["speed"]
        shot.damage = stats["damage"]

    def _shoot_spread(self, stats):
        count = stats["extra"]["count"]
        angle = stats["extra"]["angle"]
        start_angle = self.rotation - (count - 1) * angle / 2
        for i in range(count):
            shot_angle = start_angle + i * angle
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(shot_angle) * stats["speed"]
            shot.damage = stats["damage"]

    def _shoot_homing(self, stats):
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * stats["speed"]
        shot.damage = stats["damage"]
        shot.turn_rate = stats["extra"]["turn_rate"]
        shot.is_homing = True

    def _shoot_laser(self, stats):
        # Laser starts from ship's triangle tip (forward point)
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        tip_pos = self.position + forward * self.radius
        laser = Laser(tip_pos.x, tip_pos.y, self.rotation, stats, self.velocity)
        
    def cycle_weapon(self, direction):
        self.weapon_index = (self.weapon_index + direction) % WEAPON_COUNT
        self.weapon_type = WEAPON_TYPES[self.weapon_index]

    def respawn(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.invulnerable_timer = 2.0
        self.shield_timer = 0.0
        self.shield_active = False
    
    def activate_shield(self, duration: float):
        """Activate the shield for the given duration."""
        self.shield_timer = duration
        self.shield_active = True
    
    def collides_with(self, other: "CircleShape") -> bool:
        """Triangle (player) vs Circle (asteroid/shot) collision."""
        tri = self.triangle()
        a, b, c = tri[0], tri[1], tri[2]
        center = other.position
        radius = other.radius
        
        # If circle center is inside triangle, collision
        if _point_in_triangle(center, a, b, c):
            return True
        
        # Check distance to each edge
        closest = _closest_point_on_segment(center, a, b)
        min_dist = center.distance_to(closest)
        
        closest = _closest_point_on_segment(center, b, c)
        min_dist = min(min_dist, center.distance_to(closest))
        
        closest = _closest_point_on_segment(center, c, a)
        min_dist = min(min_dist, center.distance_to(closest))
        
        return min_dist <= radius