import mido
from mido import MidiFile, MidiTrack, Message
import pygame
import time
import random
import os

SR      = 44100
TEMPO   = 500000          # microseconds per beat = 120 BPM
TICKS   = 480             # ticks per beat

def play_midi(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    # Wait for playback to finish
    clock = pygame.time.Clock()
    while pygame.mixer.music.get_busy():
        clock.tick(10)
    pygame.mixer.quit()

def note_on(track, note, velocity, time=0):
    track.append(Message('note_on',  note=note, velocity=velocity, time=time))

def note_off(track, note, time):
    track.append(Message('note_off', note=note, velocity=0,        time=time))

def add_note(track, note, duration_ticks, velocity=80, gap=10):
    """Add a note_on then note_off with a small gap."""
    note_on(track,  note, velocity, time=0)
    note_off(track, note, time=duration_ticks - gap)

# ── Compose ───────────────────────────────────────────────────────────────────
def compose_scale_melody(scale_notes, length=32, bpm=60):
    """Walk randomly through a scale."""
    tempo   = int(60_000_000 / bpm)
    quarter = TICKS

    mid   = MidiFile(ticks_per_beat=TICKS)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    note = random.choice(scale_notes)
    for _ in range(length):
        duration = random.choice([quarter // 2, quarter, quarter * 2])
        velocity = random.randint(60, 100)
        add_note(track, note, duration, velocity)
        # Step up, down, or jump in the scale
        step = random.choice([-2, -1, -1, 0, 1, 1, 2])
        idx  = scale_notes.index(note)
        note = scale_notes[max(0, min(len(scale_notes)-1, idx + step))]

    mid.save("melody.mid")
    return "melody.mid"

# A minor pentatonic starting at A3
A_MINOR_PENTATONIC = [57, 60, 62, 64, 67, 69, 72, 74, 76]

path = compose_scale_melody(A_MINOR_PENTATONIC, length=48, bpm=130)

pygame.mixer.init()
pygame.mixer.music.load(path)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)