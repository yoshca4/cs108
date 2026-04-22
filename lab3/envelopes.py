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

t    = timeline(2.0)
tone = 0.5 * np.sin(2 * np.pi * 440 * t)

abrupt   = tone
shaped   = tone * adsr(2.0, attack=0.01, release=0.1)
piano_like = tone * adsr(2.0, attack=0.005, decay=0.3, sustain=0.3, release=0.4)
pad_like   = tone * adsr(2.0, attack=0.6,  decay=0.1, sustain=0.9, release=0.5)

for wave, name in [
    (abrupt,     "abrupt (no envelope)"),
    (shaped,     "basic envelope"),
    (piano_like, "piano-like"),
    (pad_like,   "slow pad"),
]:
    show(wave, name, duration=2.0)
    play(wave)
