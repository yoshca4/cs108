import numpy as np
import pygame
from scipy.io.wavfile import write

SR = 44100

def play(wave):
    wave = wave.astype(np.float32)
    wave /= np.max(np.abs(wave)) + 1e-9
    pcm = (wave * 32767).astype(np.int16)
    pcm_stereo = np.column_stack([pcm, pcm])
    pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=2048)
    sound = pygame.sndarray.make_sound(pcm_stereo)
    sound.play()
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

def save(wave, filename):
    wave = wave.astype(np.float32)
    wave /= np.max(np.abs(wave)) + 1e-9
    write(filename, SR, (wave * 32767).astype(np.int16))
    print(f"Saved: {filename}")

def adsr(duration, attack=0.01, decay=0.1, sustain=0.7, release=0.15):
    n   = int(SR * duration)
    env = np.zeros(n)
    a, d, r = int(SR*attack), int(SR*decay), int(SR*release)
    s = max(0, n - a - d - r)
    env[:a]        = np.linspace(0, 1, a)
    env[a:a+d]     = np.linspace(1, sustain, d)
    env[a+d:a+d+s] = sustain
    env[a+d+s:]    = np.linspace(sustain, 0, max(1, n-a-d-s))
    return env

def note(freq, duration, amplitude=0.3, waveform='sine'):
    t = np.linspace(0, duration, int(SR * duration))
    if waveform == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif waveform == 'sawtooth':
        wave = 2 * (t * freq % 1) - 1
    elif waveform == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    else:
        wave = np.sin(2 * np.pi * freq * t)
    return amplitude * wave * adsr(duration)

def midi_to_freq(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12))