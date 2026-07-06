# 🚀 Asteroids — Boot.dev Edition

A faithful, no-nonsense clone of the 1979 arcade classic, built from scratch with **pygame** as part of the [Boot.dev](https://boot.dev) backend curriculum.

![Gameplay](https://img.shields.io/badge/genre-arcade%20shooter-red)
![Python](https://img.shields.io/badge/python-3.13+-blue)
![pygame](https://img.shields.io/badge/pygame-2.6.1-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 🎮 Play

```bash
# Install deps (uv recommended)
uv sync

# Launch
python main.py
```

**Controls**

|| Key | Action ||
||-----|--------||
|| `W` | Thrust forward ||
|| `S` | Thrust backward ||
|| `A` | Rotate left ||
|| `D` | Rotate right ||
|| `SPACE` | Fire ||
|| `Q` / `E` | Cycle weapon backward / forward ||
|| `SHIFT` | Drop bomb (clear asteroids in radius)||
|| `P` | Pause game ||
|| `R` | Restart (when paused or game over)||
|| `M` | Return to main menu (when game over)||
|| `↑` / `↓` | Navigate menu (main menu)||
|| `ENTER` / `SPACE` | Select menu option (main menu)||
|| `✕` (window close) | Quit ||
|| Any key (Game Over) | Exit game ||

---

## 🧱 Architecture

```
main.py           → game loop, collision, sprite groups
constants.py      → every tunable number in one place
circleshape.py    → base class: position, velocity, radius, collision
player.py         → ship: triangle draw, WASD movement, shoot cooldown
shot.py           → projectiles: simple circle, linear motion (dies off-screen)
asteroid.py       → rocks: draw, drift, split into 2 smaller + faster
asteroidfield.py  → spawner: 4 screen edges, 1.5s interval, 3 size tiers
particle.py       → explosion particles: fade, shrink, auto-cleanup
background.py     → parallax starfield: 3 layers, depth perception
sounds.py         → procedural sound effects: shoot, explode, thrust, power-up
logger.py         → JSONL state/events (game_state.jsonl, game_events.jsonl)
```

**Inheritance**: `CircleShape(pygame.sprite.Sprite)` → `Player`, `Asteroid`, `Shot`, `Particle`  
**Groups**: `updatable`, `drawable`, `asteroids`, `shots` — all via class-level `containers`

---

## 💥 Mechanics

- **Asteroids** come in 3 sizes (radius 20, 40, 60). Large → medium → small → *poof*
- **Irregular shape**: each asteroid is a unique lumpy polygon (8-14 vertices, 60-100% radius variance)
- **Split physics**: 20–50° divergence, 1.2× speed boost — classic "ricochet" feel
- **Shoot cooldown**: 0.3s — spam prevented, rhythm rewarded
- **Player collision**: triangle-vs-circle (ship hitbox matches sprite exactly)
- **Other collisions**: circle-vs-circle (distance ≤ r₁ + r₂)
- **Wrap-around**: objects wrap at screen edges — fly off one side, appear on the other (classic Asteroids)
- **Shots**: die when leaving screen — no wrapping, no accumulation
- **Explosions**: particle burst + screen shake on asteroid destruction

---

## 🔫 Weapon System

Press **Q/E** to cycle through 4 weapon types:

| Weapon | Behavior | Cooldown | Speed | Damage |
|--------|----------|----------|-------|--------|
| **Single** | One straight shot | 0.30s | 500 | 1 |
| **Spread** | 3-shot fan (±15°) | 0.50s | 450 | 1 |
| **Homing** | Tracks nearest asteroid | 0.60s | 350 | 1 |
| **Laser** | Continuous beam, 0.2s duration | 1.00s | 800 | 2 |

Current weapon shown in HUD (top-left).

---

## 🛡️ Power-ups

**Shield Power-up** (cyan glowing pickup):
- Spawns with 15% chance when asteroids are destroyed
- Drifts downward with pulsing glow
- Collect to gain **5 seconds of invincibility**
- Visual: pulsing cyan ring around ship + HUD timer "SHIELD: X.Xs"
- While active: asteroid collisions destroy the asteroid (with points + split) but **no damage/lives lost**
- Can be refreshed by collecting another shield before timer expires

**Speed Boost Power-up** (yellow/orange glowing pickup):
- Spawns with 10% chance when asteroids are destroyed
- Drifts downward with pulsing glow
- Collect to gain **5 seconds of 2x speed boost**
- Visual: pulsing yellow ring around ship + HUD timer "SPEED BOOST: X.Xs"
- While active: player acceleration is doubled, making movement much faster
- Can be refreshed by collecting another speed boost before timer expires

**Bomb Power-up** (red glowing pickup):
- Spawns with 5% chance when asteroids are destroyed
- Drifts downward with pulsing glow
- Collect to gain **1 bomb** (max 3 carried)
- Visual: bomb icon with fuse + HUD counter "BOMBS: X"
- Press **Shift** to drop bomb — destroys all asteroids within 200px radius
- Awards points for each destroyed asteroid + screen shake
- Can stack up to 3 bombs

Current shield/speed/bomb status shown in HUD (top-left, below weapon).

---

## 🔊 Sound Effects

All sound effects are **procedurally generated** at runtime — no external audio files needed:

| Event | Sound Description |
|-------|-------------------|
| **Shoot** | Quick descending laser tone (800→200 Hz) |
| **Explosion** | White noise burst with low-frequency rumble |
| **Thrust** | Loopable engine rumble (80 Hz base + noise) |
| **Power-up** | Ascending 4-note chime (C5 → E5 → G5 → C6) |
| **Bomb** | Deep explosion with heavy low-end rumble |
| **Game Over** | Descending minor chord over 1 second |

Generated via `pygame.mixer.Sound` from raw PCM buffers in `sounds.py`.

---

## 📊 High Scores
High scores are automatically saved to `highscores.json` and displayed on the Game Over screen. The top 10 scores persist between game sessions.

---

## 📜 Logging (built-in)

Every run produces two JSONL files:

```json
// game_state.jsonl — once per second
{"timestamp":"14:23:12.045","elapsed_s":12,"frame":720,"screen_size":[1280,720],
 "updatable":{"count":14,"sprites":[{"type":"Player","pos":[640.0,360.0],"vel":[0.0,0.0],"rad":20.0,"rot":0.0},...]}}

// game_events.jsonl — discrete events
{"timestamp":"14:23:15.102","elapsed_s":15,"frame":903,"type":"asteroid_shot"}
{"timestamp":"14:23:15.103","elapsed_s":15,"frame":903,"type":"asteroid_split"}
{"timestamp":"14:23:18.441","elapsed_s":18,"frame":1082,"type":"player_hit"}
```

Perfect for post-game analysis, replay visualisation, or training an RL agent.

---

## 🛠️ Extending Ideas

- **Score / lives / levels** — `constants.py` already has the hooks
- **Background starfield** — parallax layers in draw loop
- **Lumpy asteroids** — per-vertex radius variation in `Asteroid.draw()`
- **Sound** — `pygame.mixer` one-liners at event sites
- **High-score file** — append to `logger.py`'s event sink
- **AI bot** — replace `Player.update()` with a policy network; state log is your dataset

---

## 📜 License

MIT — do whatever, just don't blame me when you lose 3 hours to "one more run".

---

*Built with ☕ and 🎮 by following Boot.dev's "Build Asteroids" course.  
If you enjoyed this, go build the next one — [Boot.dev](https://boot.dev) teaches backend by building real things.*