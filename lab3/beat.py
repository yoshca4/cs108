from sound_base import *

def kick(duration=0.4):
    """Low thump — a sine wave that drops in pitch quickly."""
    t = timeline(duration)
    freq_env = np.exp(-t * 20) * 150 + 50   # pitch drops from 200 to 50 Hz
    wave = np.sin(2 * np.pi * np.cumsum(freq_env) / SR)
    env  = np.exp(-t * 10)
    return 0.8 * wave * env

def snare(duration=0.2):
    """Snappy noise burst — filtered white noise."""
    t = timeline(duration)
    noise = np.random.uniform(-1, 1, len(t))
    env   = np.exp(-t * 20)
    return 0.5 * noise * env

def hihat(duration=0.05):
    """Short high noise click."""
    t = timeline(duration)
    noise = np.random.uniform(-1, 1, len(t))
    env   = np.exp(-t * 60)
    return 0.3 * noise * env

def place(sound, position_seconds, total_length_seconds):
    """Place a sound at a position in a longer buffer."""
    buf   = np.zeros(int(SR * total_length_seconds))
    start = int(SR * position_seconds)
    end   = start + len(sound)
    if end <= len(buf):
        buf[start:end] += sound
    return buf

# One measure = 2 seconds, 8 eighth-note slots
BPM       = 120
beat      = 60 / BPM          # one beat in seconds
measure   = beat * 4           # 4 beats per measure
slot      = beat / 2           # eighth note

# Patterns: 1 = hit, 0 = rest
kick_pat   = [1, 0, 0, 0, 1, 0, 0, 0]
snare_pat  = [0, 0, 1, 0, 0, 0, 1, 0]
hihat_pat  = [0, 0, 0, 0, 0, 0, 0, 0]

buf = np.zeros(int(SR * measure))
for i, hit in enumerate(kick_pat):
    if hit: buf += place(kick(),  i * slot, measure)
for i, hit in enumerate(snare_pat):
    if hit: buf += place(snare(), i * slot, measure)
for i, hit in enumerate(hihat_pat):
    if hit: buf += place(hihat(), i * slot, measure)

buf /= np.max(np.abs(buf))

# Loop it 4 times
beat_loop = np.tile(buf, 4)
play(beat_loop)
save(beat_loop, "beat.wav")
