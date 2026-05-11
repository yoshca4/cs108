import numpy as np
import pygame
import sys
from scipy.io.wavfile import read
from scipy.fft import rfft

# ── Load audio ────────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: python visualizer.py path/to/file.wav")
    sys.exit(1)

sr, data = read(sys.argv[1])

# Flatten to mono
if data.ndim == 2:
    data = data.mean(axis=1)
data = data.astype(np.float32)
data /= np.max(np.abs(data)) + 1e-9

# ── Settings ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 500
NUM_BARS      = 64
FRAME_SIZE    = 2048
FPS           = 60
BG_COLOR      = (30, 30, 46)
PEAK_COLOR    = (243, 139, 168)
peak_decay    = 0.5

# ── Pygame + mixer ────────────────────────────────────────────────────────────
pygame.init()

# Always init as stereo — duplicate mono to satisfy pygame no matter what
pygame.mixer.init(frequency=sr, size=-16, channels=2, buffer=2048)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FFT Visualizer")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("monospace", 13)

# Build stereo array regardless of source
pcm        = (data * 32767).astype(np.int16)
pcm_stereo = np.column_stack([pcm, pcm])
sound      = pygame.sndarray.make_sound(pcm_stereo)
sound.play()
start_tick = pygame.time.get_ticks()

# ── Spectrum ──────────────────────────────────────────────────────────────────
peaks = np.zeros(NUM_BARS)

def get_spectrum(sample_pos):
    chunk = data[sample_pos : sample_pos + FRAME_SIZE]
    if len(chunk) < FRAME_SIZE:
        chunk = np.pad(chunk, (0, FRAME_SIZE - len(chunk)))
    window   = chunk * np.hanning(FRAME_SIZE)
    fft_out  = np.abs(rfft(window))
    freqs     = np.logspace(np.log10(20), np.log10(sr / 2), NUM_BARS + 1)
    bin_freqs = np.linspace(0, sr / 2, len(fft_out))
    bars = np.zeros(NUM_BARS)
    for i in range(NUM_BARS):
        lo = np.searchsorted(bin_freqs, freqs[i])
        hi = np.searchsorted(bin_freqs, freqs[i + 1])
        if hi > lo:
            bars[i] = np.mean(fft_out[lo:hi])
    bars = np.log1p(bars)
    if bars.max() > 0:
        bars /= bars.max()
    return bars

# ── Main loop ─────────────────────────────────────────────────────────────────
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

    elapsed_ms = pygame.time.get_ticks() - start_tick
    sample_pos = int((elapsed_ms / 1000) * sr)
    if sample_pos >= len(data):
        pygame.quit(); sys.exit()

    bars  = get_spectrum(sample_pos)
    peaks = np.where(bars > peaks, bars, peaks * peak_decay)

    screen.fill(BG_COLOR)

    bar_w   = WIDTH // NUM_BARS
    padding = 2
    for i, (bar, peak) in enumerate(zip(bars, peaks)):
        x  = i * bar_w
        bh = int(bar  * (HEIGHT - 60))
        ph = int(peak * (HEIGHT - 60))
        r  = int(137 + (243 - 137) * bar)
        g  = int(180 -  100        * bar)
        b  = int(250 -  100        * bar)
        pygame.draw.rect(screen, (r, g, b),
                         (x + padding, HEIGHT - bh - 30,
                          bar_w - padding * 2, bh))
        pygame.draw.rect(screen, PEAK_COLOR,
                         (x + padding, HEIGHT - ph - 34,
                          bar_w - padding * 2, 4))

    secs = elapsed_ms // 1000
    txt  = font.render(
        f"{secs//60:02d}:{secs%60:02d}  |  {NUM_BARS} bands  |  ESC to quit",
        True, (108, 112, 134))
    screen.blit(txt, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)