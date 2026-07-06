import sys
import random
import json
import os
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_MIN_RADIUS, 
    SHIELD_SPAWN_CHANCE, SPEED_BOOST_SPAWN_CHANCE, BOMB_SPAWN_CHANCE,
    BOMB_EXPLOSION_RADIUS
)
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from laser import Laser
from particle import Particle, spawn_explosion
from background import Background
from powerup import ShieldPowerUp, SpeedPowerUp, BombPowerUp
from sounds import get_sound_manager

# High score file
HIGHSCORE_FILE = "highscores.json"

# Game states
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

def load_highscores() -> list:
    """Load high scores from file."""
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_highscores(scores: list) -> None:
    """Save high scores to file."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(scores, f)
    except IOError:
        pass

def add_highscore(score: int) -> None:
    """Add a new score to the high scores list and save."""
    scores = load_highscores()
    scores.append(score)
    scores.sort(reverse=True)
    # Keep only top 10
    scores = scores[:10]
    save_highscores(scores)

def draw_menu(screen: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font, highscores: list) -> None:
    """Draw the main menu screen."""
    # Title
    title = title_font.render("ASTEROIDS", True, (255, 200, 50))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
    screen.blit(title, title_rect)
    
    # Menu options
    options = [
        ("START GAME", (255, 255, 255)),
        ("HIGH SCORES", (255, 255, 255)),
        ("QUIT", (255, 255, 255)),
    ]
    
    for i, (text, color) in enumerate(options):
        option_text = font.render(text, True, color)
        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 60))
        screen.blit(option_text, option_rect)
    
    # High scores preview
    hs_font = pygame.font.Font(None, 28)
    hs_title = hs_font.render("TOP SCORES", True, (255, 215, 0))
    hs_title_rect = hs_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))
    screen.blit(hs_title, hs_title_rect)
    
    for i, hs in enumerate(highscores[:5]):
        hs_text = hs_font.render(f"{i+1}. {hs}", True, (200, 200, 200))
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200 + i * 25))
        screen.blit(hs_text, hs_rect)
    
    # Controls hint
    hint_font = pygame.font.Font(None, 24)
    hint = hint_font.render("WASD to move, SPACE to shoot, Q/E to cycle weapons, SHIFT to drop bomb", True, (100, 100, 100))
    hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
    screen.blit(hint, hint_rect)

def draw_pause_menu(screen: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font) -> None:
    """Draw the pause menu overlay."""
    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Title
    title = title_font.render("PAUSED", True, (255, 215, 0))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(title, title_rect)
    
    # Options
    options = [
        ("RESUME (P)", (255, 255, 255)),
        ("RESTART (R)", (255, 255, 255)),
        ("QUIT TO MENU (Q)", (255, 255, 255)),
    ]
    
    for i, (text, color) in enumerate(options):
        option_text = font.render(text, True, color)
        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 50))
        screen.blit(option_text, option_rect)

def draw_game_over(screen: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font, score: int, highscores: list) -> None:
    """Draw the game over screen."""
    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Game Over title
    title = title_font.render("GAME OVER", True, (255, 50, 50))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
    screen.blit(title, title_rect)
    
    # Final score
    score_font = pygame.font.Font(None, 48)
    final_score = score_font.render(f"Final Score: {score}", True, "white")
    score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(final_score, score_rect)
    
    # High scores
    hs_font = pygame.font.Font(None, 36)
    hs_title = hs_font.render("HIGH SCORES", True, (255, 215, 0))
    hs_title_rect = hs_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(hs_title, hs_title_rect)
    
    for i, hs in enumerate(highscores[:10]):
        hs_text = hs_font.render(f"{i+1}. {hs}", True, "white")
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60 + i * 30))
        screen.blit(hs_text, hs_rect)
    
    # Options
    options_font = pygame.font.Font(None, 36)
    options = [
        ("RESTART (R)", (255, 255, 255)),
        ("MAIN MENU (M)", (255, 255, 255)),
        ("QUIT (Q)", (255, 255, 255)),
    ]
    
    for i, (text, color) in enumerate(options):
        option_text = options_font.render(text, True, color)
        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120 + i * 45))
        screen.blit(option_text, option_rect)

def reset_game():
    """Reset all game state for a new game."""
    # This will be filled in main() with local variables
    pass

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
    powerups = pygame.sprite.Group()
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    Shot.containers = (shots, updatable, drawable)
    Laser.containers = (updatable, drawable)
    Particle.containers = (updatable, drawable)
    ShieldPowerUp.containers = (powerups, updatable, drawable)
    SpeedPowerUp.containers = (powerups, updatable, drawable)
    BombPowerUp.containers = (powerups, updatable, drawable)
    asteroid_field = AsteroidField()
    player = Player(x, y)
    background = Background()
    sound_manager = get_sound_manager()
    score = 0
    lives = 3
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 72)
    # Screen shake
    shake_timer = 0.0
    shake_intensity = 0
    # Offscreen surface for screen shake
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Game state
    game_state = GameState.MENU
    highscores = load_highscores()
    # Track thrust key state
    was_thrusting = False
    # Menu selection
    menu_selection = 0
    # Pause menu selection
    pause_selection = 0
    # Game over selection
    game_over_selection = 0
    # Play time for difficulty scaling
    play_time = 0.0

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if game_state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        menu_selection = (menu_selection - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        menu_selection = (menu_selection + 1) % 3
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if menu_selection == 0:  # START GAME
                            # Reset game state
                            for group in [updatable, drawable, asteroids, shots, powerups]:
                                group.empty()
                            asteroid_field = AsteroidField()
                            player = Player(x, y)
                            score = 0
                            lives = 3
                            game_state = GameState.PLAYING
                            play_time = 0.0  # reset play time
                        elif menu_selection == 1:  # HIGH SCORES
                            # Just show high scores - we'll handle this in the menu drawing
                            pass
                        elif menu_selection == 2:  # QUIT
                            return
                elif game_state == GameState.PLAYING:
                    if event.key == pygame.K_q:
                        player.cycle_weapon(-1)
                    elif event.key == pygame.K_e:
                        player.cycle_weapon(1)
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        if player.drop_bomb():
                            log_event("bomb_dropped")
                            get_sound_manager().play_bomb()
                            # Destroy asteroids within blast radius
                            destroyed_count = 0
                            for asteroid in list(asteroids):
                                if player.position.distance_to(asteroid.position) <= BOMB_EXPLOSION_RADIUS:
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
                                    shake_intensity = 6  # Stronger shake for bomb
                                    asteroid.split()
                                    destroyed_count += 1
                            if destroyed_count > 0:
                                print(f"Bomb destroyed {destroyed_count} asteroids!")
                    elif event.key == pygame.K_p:
                        game_state = GameState.PAUSED
                elif game_state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        game_state = GameState.PLAYING
                    elif event.key == pygame.K_r:
                        # Restart game
                        for group in [updatable, drawable, asteroids, shots, powerups]:
                            group.empty()
                        asteroid_field = AsteroidField()
                        player = Player(x, y)
                        score = 0
                        lives = 3
                        game_state = GameState.PLAYING
                        play_time = 0.0  # reset play time
                    elif event.key == pygame.K_q:
                        # Quit to menu
                        game_state = GameState.MENU
                elif game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        # Restart game
                        for group in [updatable, drawable, asteroids, shots, powerups]:
                            group.empty()
                        asteroid_field = AsteroidField()
                        player = Player(x, y)
                        score = 0
                        lives = 3
                        game_state = GameState.PLAYING
                        play_time = 0.0  # reset play time
                    elif event.key == pygame.K_m:
                        # Main menu
                        game_state = GameState.MENU
                    elif event.key == pygame.K_q:
                        # Quit
                        return

        # Game logic based on state
        if game_state == GameState.PLAYING:
            # Update play time for difficulty scaling
            play_time += dt
            # Calculate difficulty: every 30 seconds of play time increases difficulty by 1
            difficulty = 1 + int(play_time // 30)
            # Update asteroid field parameters based on difficulty
            # Spawn rate decreases (so faster spawns) as difficulty increases, but not below 0.5 seconds
            asteroid_field.base_spawn_rate = max(0.5, 1.5 - 0.2 * difficulty)
            # Speed range increases with difficulty
            asteroid_field.base_speed_min = 40 + difficulty * 2
            asteroid_field.base_speed_max = 100 + difficulty * 2

            updatable.update(dt, asteroids)
            background.update(dt, player.velocity)
            
            # Check collisions
            for thing in asteroids:
                if player.collides_with(thing):
                    # Check if shield is active - if so, destroy asteroid but no damage
                    if player.shield_active:
                        log_event("shield_blocked")
                        get_sound_manager().play_explosion()
                        if thing.radius == ASTEROID_MIN_RADIUS * 3:
                            score += 1
                            spawn_explosion(thing.position.x, thing.position.y, (255, 100, 50), 16)
                        elif thing.radius == ASTEROID_MIN_RADIUS * 2:
                            score += 2
                            spawn_explosion(thing.position.x, thing.position.y, (255, 150, 50), 12)
                        else:
                            score += 3
                            spawn_explosion(thing.position.x, thing.position.y, (255, 200, 100), 8)
                        # Screen shake
                        shake_timer = 0.1
                        shake_intensity = 4
                        thing.split()
                        # Chance to spawn shield power-up
                        if random.random() < SHIELD_SPAWN_CHANCE:
                            ShieldPowerUp(thing.position.x, thing.position.y)
                        # Chance to spawn speed power-up
                        if random.random() < SPEED_BOOST_SPAWN_CHANCE:
                            SpeedPowerUp(thing.position.x, thing.position.y)
                        # Chance to spawn bomb power-up
                        if random.random() < BOMB_SPAWN_CHANCE:
                            BombPowerUp(thing.position.x, thing.position.y)
                    elif player.invulnerable_timer <= 0:
                        log_event("player_hit")
                        get_sound_manager().play_explosion()
                        lives -= 1
                        if lives > 0:
                            # respawn player at center
                            player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        else:
                            # Game over
                            game_state = GameState.GAME_OVER
                            add_highscore(score)
                            highscores = load_highscores()
                            log_event("game_over", score=score)
                            get_sound_manager().play_game_over()
            
            # Shot collision with asteroids
            for asteroid in asteroids:
                for shot in shots:
                    if shot.collides_with(asteroid):
                        log_event("asteroid_shot")
                        get_sound_manager().play_explosion()
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
                        # Chance to spawn shield power-up
                        if random.random() < SHIELD_SPAWN_CHANCE:
                            ShieldPowerUp(asteroid.position.x, asteroid.position.y)
                        # Chance to spawn speed power-up
                        if random.random() < SPEED_BOOST_SPAWN_CHANCE:
                            SpeedPowerUp(asteroid.position.x, asteroid.position.y)
                        # Chance to spawn bomb power-up
                        if random.random() < BOMB_SPAWN_CHANCE:
                            BombPowerUp(asteroid.position.x, asteroid.position.y)
            
            # Laser collision with asteroids
            for laser_obj in [obj for obj in updatable if isinstance(obj, Laser)]:
                hit_asteroid = laser_obj.check_collision(asteroids)
                if hit_asteroid:
                    log_event("asteroid_shot")
                    get_sound_manager().play_explosion()
                    if hit_asteroid.radius == ASTEROID_MIN_RADIUS * 3:
                        score += 1
                        spawn_explosion(hit_asteroid.position.x, hit_asteroid.position.y, (255, 100, 50), 16)
                    elif hit_asteroid.radius == ASTEROID_MIN_RADIUS * 2:
                        score += 2
                        spawn_explosion(hit_asteroid.position.x, hit_asteroid.position.y, (255, 150, 50), 12)
                    else:
                        score += 3
                        spawn_explosion(hit_asteroid.position.x, hit_asteroid.position.y, (255, 200, 100), 8)
                    # Screen shake
                    shake_timer = 0.1
                    shake_intensity = 4
                    # Chance to spawn shield power-up
                    if random.random() < SHIELD_SPAWN_CHANCE:
                        ShieldPowerUp(hit_asteroid.position.x, hit_asteroid.position.y)
                    # Chance to spawn speed power-up
                    if random.random() < SPEED_BOOST_SPAWN_CHANCE:
                        SpeedPowerUp(hit_asteroid.position.x, hit_asteroid.position.y)
                    # Chance to spawn bomb power-up
                    if random.random() < BOMB_SPAWN_CHANCE:
                        BombPowerUp(hit_asteroid.position.x, hit_asteroid.position.y)
            
            # Power-up collection
            for powerup in powerups:
                if player.collides_with(powerup):
                    powerup.apply_effect(player)
                    get_sound_manager().play_powerup()
                    powerup.kill()
        
        # Rendering based on state
        game_surface.fill("black")
        # Draw background first (only in playing state)
        if game_state == GameState.PLAYING:
            background.draw(game_surface)
        
        # Draw game objects (only in playing state)
        if game_state == GameState.PLAYING:
            for thing in drawable:
                thing.draw(game_surface)
            
            # Draw HUD on game surface (so it shakes with the world)
            score_text = font.render(f"Score: {score}", True, "white")
            lives_text = font.render(f"Lives: {lives}", True, "white")
            weapon_text = font.render(f"Weapon: {player.weapon_type.upper()}", True, "white")
            game_surface.blit(score_text, (10, 10))
            game_surface.blit(lives_text, (SCREEN_WIDTH - 120, 10))
            game_surface.blit(weapon_text, (10, 50))
            
            # Shield HUD
            if player.shield_active:
                shield_text = font.render(f"SHIELD: {player.shield_timer:.1f}s", True, (0, 200, 255))
                game_surface.blit(shield_text, (10, 90))
            
            # Speed Boost HUD
            if player.speed_boost_active:
                speed_text = font.render(f"SPEED BOOST: {player.speed_boost_timer:.1f}s", True, (255, 200, 0))
                game_surface.blit(speed_text, (10, 130))
            
            # Bomb HUD
            if player.bomb_count > 0:
                bomb_text = font.render(f"BOMBS: {player.bomb_count}", True, (255, 50, 50))
                game_surface.blit(bomb_text, (10, 170))
        
        # Draw menus/overlays
        if game_state == GameState.MENU:
            draw_menu(game_surface, font, title_font, highscores)
        elif game_state == GameState.PAUSED:
            # Draw the game underneath
            background.draw(game_surface)
            for thing in drawable:
                thing.draw(game_surface)
            # Draw pause menu overlay
            draw_pause_menu(game_surface, font, title_font)
        elif game_state == GameState.GAME_OVER:
            # Draw the game underneath (darkened)
            background.draw(game_surface)
            for thing in drawable:
                thing.draw(game_surface)
            # Draw game over screen
            draw_game_over(game_surface, font, title_font, score, highscores)
        
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