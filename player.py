import pygame
from circleshape import CircleShape
from shot import Shot
from constants import (
    PLAYER_ACCELERATION,
    PLAYER_DRAG,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
)

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
        self.invulnerable_timer = 0
    
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

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.shot_cooldown -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
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
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            self.shot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
    
    def respawn(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.invulnerable_timer = 2.0