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

| Key | Action |
|-----|--------|
| `W` | Thrust forward |
| `S` | Thrust backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `SPACE` | Fire |
| `✕` (window close) | Quit |

---

## 🧱 Architecture

```
main.py           → game loop, collision, sprite groups
constants.py      → every tunable number in one place
circleshape.py    → base class: position, velocity, radius, collision
player.py         → ship: triangle draw, WASD movement, shoot cooldown
shot.py           → projectiles: simple circle, linear motion
asteroid.py       → rocks: draw, drift, split into 2 smaller + faster
asteroidfield.py  → spawner: 4 screen edges, 0.8s interval, 3 size tiers
logger.py         → JSONL state/events (game_state.jsonl, game_events.jsonl)
```

**Inheritance**: `CircleShape(pygame.sprite.Sprite)` → `Player`, `Asteroid`, `Shot`  
**Groups**: `updatable`, `drawable`, `asteroids`, `shots` — all via class-level `containers`

---

## 💥 Mechanics

- **Asteroids** come in 3 sizes (radius 20, 40, 60). Large → medium → small → *poof*
- **Split physics**: 20–50° divergence, 1.2× speed boost — classic "ricochet" feel
- **Shoot cooldown**: 0.3s — spam prevented, rhythm rewarded
- **Collision**: pixel-perfect circle-vs-circle (distance ≤ r₁ + r₂)
- **Wrap-around**: none — rocks spawn off-screen, drift through, exit opposite side

---

## 📊 Logging (built-in)

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
- **Particle explosions** — `Shot.kill()` + `Asteroid.split()` are your entry points
- **Sound** — `pygame.mixer` one-liners at event sites
- **High-score file** — append to `logger.py`'s event sink
- **AI bot** — replace `Player.update()` with a policy network; state log is your dataset

---

## 📜 License

MIT — do whatever, just don't blame me when you lose 3 hours to "one more run".

---

*Built with ☕ and 🎮 by following Boot.dev's "Build Asteroids" course.  
If you enjoyed this, go build the next one — [Boot.dev](https://boot.dev) teaches backend by building real things.*