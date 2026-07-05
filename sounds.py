"""Sound effects module for Asteroids game.
Generates procedural sound effects using pygame's sound buffer."""
import pygame
import math
import array


def generate_tone(frequency: float, duration: float, volume: float = 0.5, 
                  sample_rate: int = 44100, wave_type: str = 'sine') -> pygame.mixer.Sound:
    """Generate a simple tone as a pygame Sound object."""
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)  # stereo
    
    max_amplitude = int(32767 * volume)
    
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'sine':
            value = math.sin(2 * math.pi * frequency * t)
        elif wave_type == 'square':
            value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        elif wave_type == 'sawtooth':
            value = 2 * (t * frequency - math.floor(t * frequency + 0.5))
        elif wave_type == 'noise':
            import random
            value = random.uniform(-1, 1)
        else:
            value = math.sin(2 * math.pi * frequency * t)
        
        # Apply envelope (fade in/out to avoid clicks)
        envelope = 1.0
        fade_samples = min(int(0.01 * sample_rate), n_samples // 4)
        if i < fade_samples:
            envelope = i / fade_samples
        elif i > n_samples - fade_samples:
            envelope = (n_samples - i) / fade_samples
        
        sample = int(max_amplitude * value * envelope)
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample  # stereo
    
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def generate_shoot_sound() -> pygame.mixer.Sound:
    """Generate a short laser/shoot sound."""
    # Quick descending tone - laser-like
    duration = 0.1
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)
    max_amp = 10000
    
    for i in range(n_samples):
        t = i / sample_rate
        # Frequency sweeps down from 800 to 200 Hz
        freq = 800 - 600 * (t / duration)
        value = math.sin(2 * math.pi * freq * t)
        # Quick decay envelope
        envelope = 1.0 - (t / duration)
        sample = int(max_amp * value * envelope)
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample
    
    return pygame.mixer.Sound(buffer=buf)


def generate_explosion_sound() -> pygame.mixer.Sound:
    """Generate an explosion sound using noise with envelope."""
    duration = 0.5
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)
    max_amp = 12000
    import random
    
    for i in range(n_samples):
        t = i / sample_rate
        # Noise with decaying envelope
        envelope = math.exp(-t * 8)  # Fast decay
        value = random.uniform(-1, 1) * envelope
        # Add some low-frequency rumble
        rumble = math.sin(2 * math.pi * 60 * t) * 0.3 * envelope
        sample = int(max_amp * (value + rumble))
        # Clamp
        sample = max(-32767, min(32767, sample))
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample
    
    return pygame.mixer.Sound(buffer=buf)


def generate_thrust_sound() -> pygame.mixer.Sound:
    """Generate a continuous thrust/engine sound."""
    duration = 0.3  # Loopable segment
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)
    max_amp = 6000
    import random
    
    for i in range(n_samples):
        t = i / sample_rate
        # Low-frequency rumble with noise
        rumble = math.sin(2 * math.pi * 80 * t) * 0.5
        noise = random.uniform(-1, 1) * 0.5
        # Modulate with a slight wobble
        wobble = math.sin(2 * math.pi * 15 * t) * 0.2
        value = (rumble + noise + wobble) / 2
        sample = int(max_amp * value)
        sample = max(-32767, min(32767, sample))
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample
    
    return pygame.mixer.Sound(buffer=buf)


def generate_powerup_sound() -> pygame.mixer.Sound:
    """Generate a positive power-up collection sound (ascending chime)."""
    duration = 0.4
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)
    max_amp = 10000
    
    for i in range(n_samples):
        t = i / sample_rate
        # Ascending arpeggio: C5 -> E5 -> G5 -> C6
        notes = [523.25, 659.25, 783.99, 1046.50]
        note_duration = duration / len(notes)
        note_index = min(int(t / note_duration), len(notes) - 1)
        freq = notes[note_index]
        # Envelope per note
        note_t = (t % note_duration) / note_duration
        envelope = 1.0 - note_t
        value = math.sin(2 * math.pi * freq * t) * envelope
        sample = int(max_amp * value)
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample
    
    return pygame.mixer.Sound(buffer=buf)


def generate_game_over_sound() -> pygame.mixer.Sound:
    """Generate a descending game over sound."""
    duration = 1.0
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)
    max_amp = 10000
    
    for i in range(n_samples):
        t = i / sample_rate
        # Descending minor chord
        freq = 440 * (2 ** (-t * 12 / 12))  # Down an octave
        value = math.sin(2 * math.pi * freq * t)
        envelope = 1.0 - t
        sample = int(max_amp * value * envelope)
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample
    
    return pygame.mixer.Sound(buffer=buf)


def generate_bomb_sound() -> pygame.mixer.Sound:
    """Generate a bomb drop/explosion sound - deeper explosion."""
    duration = 0.8
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)
    max_amp = 15000
    import random
    
    for i in range(n_samples):
        t = i / sample_rate
        # Deep rumble + noise
        envelope = math.exp(-t * 4)
        rumble = math.sin(2 * math.pi * 40 * t) * 0.6
        noise = random.uniform(-1, 1) * 0.4
        value = (rumble + noise) * envelope
        sample = int(max_amp * value)
        sample = max(-32767, min(32767, sample))
        buf[i * 2] = sample
        buf[i * 2 + 1] = sample
    
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    """Manages all game sound effects."""
    
    def __init__(self):
        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Generate sounds
        self.shoot_sound = generate_shoot_sound()
        self.explosion_sound = generate_explosion_sound()
        self.thrust_sound = generate_thrust_sound()
        self.powerup_sound = generate_powerup_sound()
        self.game_over_sound = generate_game_over_sound()
        self.bomb_sound = generate_bomb_sound()
        
        # Set volumes
        self.shoot_sound.set_volume(0.4)
        self.explosion_sound.set_volume(0.6)
        self.thrust_sound.set_volume(0.3)
        self.powerup_sound.set_volume(0.5)
        self.game_over_sound.set_volume(0.6)
        self.bomb_sound.set_volume(0.7)
        
        # Thrust sound channel for looping
        self.thrust_channel = None
        self.thrust_playing = False
    
    def play_shoot(self):
        """Play shoot sound."""
        self.shoot_sound.play()
    
    def play_explosion(self):
        """Play explosion sound."""
        self.explosion_sound.play()
    
    def play_powerup(self):
        """Play powerup collection sound."""
        self.powerup_sound.play()
    
    def play_game_over(self):
        """Play game over sound."""
        self.game_over_sound.play()
    
    def play_bomb(self):
        """Play bomb explosion sound."""
        self.bomb_sound.play()
    
    def start_thrust(self):
        """Start continuous thrust sound."""
        if not self.thrust_playing:
            self.thrust_channel = self.thrust_sound.play(loops=-1)
            self.thrust_playing = True
    
    def stop_thrust(self):
        """Stop continuous thrust sound."""
        if self.thrust_playing and self.thrust_channel:
            self.thrust_channel.stop()
            self.thrust_playing = False
    
    def set_volume(self, volume: float):
        """Set master volume for all sounds (0.0 to 1.0)."""
        self.shoot_sound.set_volume(0.4 * volume)
        self.explosion_sound.set_volume(0.6 * volume)
        self.thrust_sound.set_volume(0.3 * volume)
        self.powerup_sound.set_volume(0.5 * volume)
        self.game_over_sound.set_volume(0.6 * volume)
        self.bomb_sound.set_volume(0.7 * volume)


# Global sound manager instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """Get or create the global sound manager."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager