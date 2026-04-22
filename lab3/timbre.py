from sound_base import *


freq = 440
dur  = 1.5
t    = timeline(dur)

sine_wave     = 0.3 * np.sin(2 * np.pi * freq * t)
square_wave   = 0.3 * np.sign(np.sin(2 * np.pi * freq * t))
sawtooth_wave = 0.3 * (2 * (t * freq % 1) - 1)
triangle_wave = 0.3 * (2 * np.abs(2 * (t * freq % 1) - 1) - 1)

for wave, name in [
    (sine_wave,     "sine"),
    (square_wave,   "square"),
    (sawtooth_wave, "sawtooth"),
    (triangle_wave, "triangle"),
]:
    play(wave)
    show(wave, name)
