from sound_base import *

def adsr(duration, attack=0.01, decay=0.1, sustain=0.7, release=0.1):
    """Return an ADSR envelope as a numpy array."""
    n = int(SR * duration)
    env = np.zeros(n)

    a = int(SR * attack)
    d = int(SR * decay)
    r = int(SR * release)
    s = n - a - d - r

    env[:a]         = np.linspace(0, 1, a)           # attack
    env[a:a+d]      = np.linspace(1, sustain, d)      # decay
    env[a+d:a+d+s]  = sustain                         # sustain
    env[a+d+s:]     = np.linspace(sustain, 0, r)      # release

    return env

def note(freq, duration, amplitude=0.3, waveform='sine'):
    t = timeline(duration)
    if waveform == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif waveform == 'sawtooth':
        wave = 2 * (t * freq % 1) - 1
    elif waveform == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))

    env = adsr(duration, attack=0.02, decay=0.1, sustain=0.6, release=0.15)
    return amplitude * wave * env

def semitones(base_freq, steps):
    """Shift a frequency by `steps` semitones."""
    return base_freq * (2 ** (steps / 12))

def chord(freqs, duration, amplitude=0.25):
    waves = [note(f, duration, amplitude) for f in freqs]
    mixed = sum(waves)
    return mixed / np.max(np.abs(mixed)) * amplitude

A3 = 220.0

# Build three chords using frequency ratios
# Major chord: root, major third (+4 semitones), perfect fifth (+7)
# Minor chord: root, minor third (+3 semitones), perfect fifth (+7)

am = chord([semitones(A3, 0), semitones(A3, 3), semitones(A3, 7)], 1.5)  # A minor
C  = chord([semitones(A3, 3), semitones(A3, 7), semitones(A3, 10)], 1.5) # C major
G  = chord([semitones(A3, 10), semitones(A3, 14), semitones(A3, 17)], 1.5) # G major

progression = np.concatenate([am, C, G, am])
play(progression)
save(progression, "chords.wav")
