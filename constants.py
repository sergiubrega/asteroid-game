SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 1.5
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3
PLAYER_ACCELERATION = 100   # pixels/sec²
PLAYER_DRAG = 0.98          # per-frame velocity multiplier (2% drag at 60fps)
PLAYER_MAX_SPEED = 400      # optional speed cap

# Weapons
WEAPON_TYPES = ["single", "spread", "homing", "laser"]
WEAPON_COUNT = len(WEAPON_TYPES)

WEAPON_STATS = {
    "single": {"speed": 500, "cooldown": 0.30, "damage": 1, "extra": {}},
    "spread": {"speed": 450, "cooldown": 0.50, "damage": 1, "extra": {"count": 3, "angle": 15}},
    "homing": {"speed": 350, "cooldown": 0.60, "damage": 1, "extra": {"turn_rate": 180}},
    "laser":  {"speed": 800, "cooldown": 1.00, "damage": 2, "extra": {"duration": 0.2, "width": 4}},
}

# Shield Power-up
SHIELD_DURATION = 5.0          # seconds
SHIELD_SPAWN_CHANCE = 0.15     # 15% chance when asteroid destroyed
SHIELD_RADIUS = 15             # pickup radius
SHIELD_COLOR = (0, 200, 255)   # cyan
SHIELD_GLOW_COLOR = (0, 255, 255, 100)  # glow for visual effect