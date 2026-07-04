import sys
import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_MIN_RADIUS
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from particle import Particle, spawn_explosion
from background import Background

def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0.0
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    Shot.containers = (shots, updatable, drawable)
    Particle.containers = (updatable, drawable)
    asteroid_field = AsteroidField()
    player = Player(x, y)
    background = Background()
    score = 0
    lives = 3
    font = pygame.font.Font(None, 36)
    # Screen shake
    shake_timer = 0.0
    shake_intensity = 0
    # Offscreen surface for screen shake
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)
        background.update(dt, player.velocity)
        for thing in asteroids:
            if thing.collides_with(player) and player.invulnerable_timer <= 0:
                log_event("player_hit")
                lives -= 1
                if lives > 0:
                    # respawn player at center
                    player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                else:
                    print("Game over! Final score:", score)
                    sys.exit()

        for asteroid in asteroids:
            for shot in shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    if asteroid.radius == ASTEROID_MIN_RADIUS * 3:
                        score += 1
                        spawn_explosion(asteroid.position.x, asteroid.position.y, (255, 100, 50), 16)
                    elif asteroid.radius == ASTEROID_MIN_RADIUS * 2:
                        score += 2
                        spawn_explosion(asteroid.position.x, asteroid.position.y, (255, 150, 50), 12)
                    else:
                        score += 3
                        spawn_explosion(asteroid.position.x, asteroid.position.y, (255, 200, 100), 8)
                    # Screen shake
                    shake_timer = 0.1
                    shake_intensity = 4
                    asteroid.split()
                    shot.kill()

        # Render game to offscreen surface
        game_surface.fill("black")
        # Draw background first
        background.draw(game_surface)

        for thing in drawable:
            thing.draw(game_surface)

        # Draw HUD on game surface (so it shakes with the world)
        score_text = font.render(f"Score: {score}", True, "white")
        lives_text = font.render(f"Lives: {lives}", True, "white")
        game_surface.blit(score_text, (10, 10))
        game_surface.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        # Screen shake offset
        shake_offset = pygame.Vector2(0, 0)
        if shake_timer > 0:
            shake_timer -= dt
            shake_offset = pygame.Vector2(
                random.uniform(-shake_intensity, shake_intensity),
                random.uniform(-shake_intensity, shake_intensity)
            )

        # Blit game surface to screen with shake offset
        screen.fill("black")
        screen.blit(game_surface, shake_offset)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()