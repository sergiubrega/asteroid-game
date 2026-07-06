# AGENTS.md — Asteroids Game Project State

## Project Overview
Faithful Asteroids clone built with pygame as part of Boot.dev curriculum. Extended with modern features: scoring, lives, inertia movement, screen wrap, particle explosions, parallax starfield, lumpy asteroids, triangular ship hitbox.

## Workflow (UPDATED)
- Agent implements tasks from TODO.md directly
- User tests implementation and gives feedback
- Only after user green light does agent proceed to next task
- No guiding/hints — agent writes code directly

## Current Status (as of commit)
**All Core Gameplay tasks complete** ✓
- Scoring system (size-based points)
- Multiple lives (3) with respawn + 2s invulnerability blink
- Acceleration/drift physics (inertia + drag)
- Screen wrap for all entities

**All Visual & Juice tasks complete** ✓
- Particle explosions + screen shake on asteroid destruction
- 3-layer parallax starfield background
- Lumpy/irregular asteroid polygons (8-14 vertices, 60-100% radius variance)
- Triangular ship hitbox (triangle-vs-circle collision via barycentric test)

**Weapons & Power-ups** — 5/5 complete ✓
- [x] Different weapon types (spread, rapid, laser, homing)
- [x] Shield power-up (temporary invincibility)
- [x] Speed power-up (temporary boost)
- [x] Bombs (area clear)
- [x] High-score persistence (file-based)

**Polish** — 4/4 complete ✓
- [x] Sound effects (shoot, explode, thrust, power-up)
- [x] Main menu / pause / game-over screens
- [x] Game-over screen waits for key press
- [x] Difficulty scaling (faster spawns, more aggressive rocks over time)

## File Structure
```
asteroid-game/
├── main.py           # Game loop, collision, sprite groups, HUD, screen shake surface
├── constants.py      # All tunable constants
├── circleshape.py    # Base CircleShape: position, velocity, radius, collision, screen wrap
├── player.py         # Player: triangle draw, WASD+acceleration, shoot cooldown, triangular hitbox
├── shot.py           # Projectiles: die off-screen (no wrap), homing support
├── laser.py          # Laser beam: tracks ship velocity, hit flash
├── asteroid.py       # Asteroids: lumpy polygon draw, split physics, circular collision
├── asteroidfield.py  # Spawner: 4 edges, 1.5s interval, 3 size tiers
├── particle.py       # Particle class + spawn_explosion() helper
├── background.py     # 3-layer parallax starfield
├── sounds.py         # Procedural sound effects: shoot, explode, thrust, power-up
├── logger.py         # JSONL state/events logging
├── TODO.md           # Task tracker (gitignored)
├── README.md         # Project documentation
├── AGENTS.md         # This file
├── pyproject.toml    # pygame==2.6.1, Python>=3.13
└── .gitignore        # Ignores: __pycache__, .venv, *.jsonl, .DS_Store, TODO.md, hermes.md, AGENTS.md
```

## Key Mechanics Implemented

### Movement
- Player: acceleration-based inertia (PLAYER_ACCELERATION=100, PLAYER_DRAG=0.98, PLAYER_MAX_SPEED=400)
- All entities: screen wrap via CircleShape.update()

### Collision
- **Player vs Asteroid/Shot**: Triangle-vs-circle (Player.collides_with overrides base)
  - Barycentric point-in-triangle test
  - Closest-point-on-segment for edge distances
- **Shot vs Asteroid**: Circle-vs-circle (base CircleShape.collides_with)
- **Asteroid split**: 2 new asteroids at radius - MIN_RADIUS, 20-50° divergence, 1.2× speed

### Visual Effects
- **Particles**: 3 size-based explosion configs (large=16 orange, medium=12 orange-yellow, small=8 yellow)
- **Screen shake**: 0.1s, 4px intensity on offscreen surface (whole world shakes)
- **Background**: 3 parallax layers (far 80 stars @ 0.05x, mid 50 @ 0.15x, near 30 @ 0.35x player velocity)
- **Asteroids**: Irregular polygons, vertices cached at spawn

### Game Loop
- 60 FPS fixed timestep
- Sprite groups: `updatable`, `drawable`, `asteroids`, `shots`
- Class-level `containers` pattern for auto-registration
- Logging: game_state.jsonl (1/sec), game_events.jsonl (discrete)

## Constants (constants.py)
```
SCREEN_WIDTH=1280, SCREEN_HEIGHT=720
PLAYER_RADIUS=20, LINE_WIDTH=2
PLAYER_TURN_SPEED=300, PLAYER_SPEED=200 (legacy, unused)
ASTEROID_MIN_RADIUS=20, ASTEROID_KINDS=3, ASTEROID_SPAWN_RATE_SECONDS=1.5
SHOT_RADIUS=5, PLAYER_SHOOT_SPEED=500, PLAYER_SHOOT_COOLDOWN_SECONDS=0.3
PLAYER_ACCELERATION=100, PLAYER_DRAG=0.98, PLAYER_MAX_SPEED=400
```

## How to Run
```bash
uv sync
python main.py
```

## Controls
||| Key | Action |||
|||-----|--------|||
||| W | Thrust forward |||
||| S | Thrust backward |||
||| A | Rotate left |||
||| D | Rotate right |||
||| SPACE | Fire |||
||| Q / E | Cycle weapon backward / forward |||
||| Shift (L/R) | Drop bomb (clears asteroids in radius) |||
||| Window close | Quit |||
||| Any key (Game Over) | Exit game |||

## Testing Checklist
- [ ] Ship accelerates, drifts, wraps screen edges
- [ ] Asteroids spawn, wrap, split correctly (3→2→1 sizes)
- [ ] Shots die off-screen (no wrap)
- [ ] Score increments per size (large=1, medium=2, small=3)
- [ ] Lives decrement on hit, respawn center, 2s blink invulnerability
- [ ] Particles spawn on destruction, fade/shrink, auto-cleanup
- [ ] Screen shake on asteroid hit (whole world)
- [ ] Parallax starfield shifts with player velocity
- [ ] Asteroids look lumpy/irregular
- [ ] Ship hitbox matches triangle sprite (fair collisions)
- [ ] Weapon cycling (Q/E) shows in HUD
- [ ] Single shot: straight, 0.3s cooldown
- [ ] Spread: 3 shots ±15°, 0.5s cooldown
- [ ] Homing: tracks nearest asteroid, 180°/sec turn rate
- [ ] Laser: from ship tip, tracks ship movement, 0.2s duration, hit flash

## Pending Tasks (from TODO.md)
### Weapons & Power-ups
- [x] Different weapon types (spread, rapid, laser, homing)
- [x] Shield power-up (temporary invincibility)
- [x] Speed power-up (temporary boost)
- [x] Bombs (area clear)
- [x] High-score persistence (file-based)

### Polish
- [ ] Sound effects (shoot, explode, thrust, power-up)
- [ ] Main menu / pause / game-over screens
- [ ] Game-over screen waits for key press
- [ ] Difficulty scaling (faster spawns over time)

## Notes for Future Agents
1. **Collision asymmetry**: Player uses triangle-vs-circle; asteroids/shots use circle-vs-circle. Call `player.collides_with(asteroid)` not `asteroid.collides_with(player)`.
2. **Screen shake**: Uses offscreen `game_surface` — draw everything there, then blit with offset.
3. **Particle system**: `spawn_explosion(x, y, color, count)` creates Particles auto-registered via `Particle.containers = (updatable, drawable)`.
4. **Background**: `background.update(dt, player.velocity)` must be called each frame for parallax.
5. **Asteroid vertices**: Generated once in `__init__`, stored in `self.vertices` for consistent appearance.
6. **Invulnerability**: Handled via `player.invulnerable_timer` (blinks at 5Hz in `draw()`).
7. **No wrap for shots**: `Shot.update()` kills when position exceeds screen bounds + radius.
8. **Weapon system**: `Player.weapon_type` cycles via Q/E (KEYDOWN in main loop). `WEAPON_STATS` in constants.py defines all stats. Laser passes ship velocity to track movement.
9. **Laser hit flash**: On collision, sets `kill_timer=0.05` for brief white flash before kill.