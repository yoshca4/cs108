from sound_base import *

tone = sine(440, 2.0)   # 440 Hz = the note A4 (concert pitch)
show(tone, "440 Hz sine wave")
play(tone)

for freq in [220, 440, 880, 1760]:
    print(f"Playing {freq} Hz")
    play(sine(freq, 1.0))
