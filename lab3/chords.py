from sound_base import *

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
