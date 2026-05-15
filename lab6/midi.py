import numpy as np
import pygame
import mido
from mido import MidiFile, MidiTrack, Message
import time

def life_step(grid):
    """One step of Conway's Game of Life."""
    neighbors = sum(
        np.roll(np.roll(grid, i, 0), j, 1)
        for i in (-1, 0, 1) for j in (-1, 0, 1)
        if (i, j) != (0, 0)
    )
    return ((neighbors == 3) | (grid & (neighbors == 2))).astype(np.uint8)

def life_to_midi(rows=16, cols=64, bpm=120, seed=42):
    """
    Run Game of Life for `cols` steps.
    Map living cells to MIDI notes in a pentatonic scale.
    """
    np.random.seed(seed)
    grid = (np.random.random((rows, cols)) > 0.5).astype(np.uint8)

    # Run the automaton
    frames = [grid.copy()]
    for _ in range(cols - 1):
        grid = life_step(grid)
        frames.append(grid.copy())

    # Pentatonic scale — maps row index to MIDI note
    pentatonic = [60, 62, 64, 67, 69,
                  72, 74, 76, 79, 81,
                  84, 86, 88, 91, 93, 96]
    scale = pentatonic[:rows]

    tempo   = int(60_000_000 / bpm)
    quarter = 480
    step_t  = quarter // 2    # eighth note per column

    mid   = MidiFile(ticks_per_beat=quarter)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    prev = np.zeros((rows, cols), dtype=np.uint8)

    for col, frame in enumerate(frames):
        for row in range(rows):
            note = scale[row]
            vel  = np.random.randint(50, 90)
            if frame[row, col % cols] and not prev[row, col % cols]:
                track.append(Message('note_on',  note=note,
                                     velocity=vel, time=0))
                track.append(Message('note_off', note=note,
                                     velocity=0,  time=step_t))
        prev = frame.copy()

    mid.save("life_music.mid")

    # Visualize the grid evolution
    import matplotlib.pyplot as plt
    arr = np.array(frames).T
    plt.figure(figsize=(14, 4))
    plt.imshow(arr[:, :, 0] if arr.ndim == 3 else
               np.array([f[:,0] for f in frames]).T,
               cmap='plasma', aspect='auto', origin='lower')
    plt.xlabel("Time step (column)")
    plt.ylabel("Pitch (row)")
    plt.title("Game of Life → Music  |  bright = alive = note plays")
    plt.colorbar(label="alive")
    plt.tight_layout()
    plt.show()

    return "life_music.mid"

path = life_to_midi(rows=16, cols=64, bpm=110, seed=7)

pygame.mixer.init()
pygame.mixer.music.load(path)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)