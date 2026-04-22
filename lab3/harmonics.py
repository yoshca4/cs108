from sound_base import *

def harmonic_tone(freq, duration, num_harmonics=6):
    t = timeline(duration)
    wave = np.zeros(len(t))
    for n in range(1, num_harmonics + 1):
        amplitude = 1.0 / n          # each harmonic is quieter
        wave += amplitude * np.sin(2 * np.pi * freq * n * t)
    wave *= 0.3 / np.max(np.abs(wave))  # normalize
    return wave

plain    = sine(440, 2.0)
rich     = harmonic_tone(440, 2.0, num_harmonics=6)
very_rich = harmonic_tone(440, 2.0, num_harmonics=20)

play(plain)
play(rich)
play(very_rich)
