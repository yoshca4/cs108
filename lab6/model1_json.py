import ollama
import json
import numpy as np
import re
from synth import play, save, note, midi_to_freq

# Configure your server URL here
SERVER_HOST = 'http://ollama.cs.wallawalla.edu:11434'
client = ollama.Client(host=SERVER_HOST)

SYSTEM = """You are a music composer. When asked to compose,
respond ONLY with a valid JSON array. No explanation, no markdown,
no code blocks. Each element must have exactly these fields:
  "note"     : MIDI note number (integer, 48-84)
  "duration" : note length in seconds (float, 0.1-1.0)
  "velocity" : volume 0-127 (integer)

Example of valid output:
[{"note":60,"duration":0.4,"velocity":80},{"note":62,"duration":0.3,"velocity":70}]"""

def ask_ollama(prompt):
    response = client.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": prompt},
        ]
    )
    return response["message"]["content"]

def parse_json(text):
    text  = re.sub(r"```[a-z]*", "", text).strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in:\n{text}")
    data = json.loads(match.group())
    # Validate each note has required fields and sane values
    for i, n in enumerate(data):
        for field in ("note", "duration", "velocity"):
            if field not in n:
                raise ValueError(f"Note {i} missing field '{field}'")
        if not (0 <= int(n["note"]) <= 127):
            raise ValueError(f"Note {i} has out-of-range MIDI note {n['note']}")
        if not (0.05 <= float(n["duration"]) <= 4.0):
            raise ValueError(f"Note {i} has bad duration {n['duration']}")
    return data

def render(notes, waveform='sine'):
    fragments = []
    for n in notes:
        freq = midi_to_freq(int(n["note"]))
        dur  = max(0.05, float(n["duration"]))
        amp  = float(n["velocity"]) / 127 * 0.4
        frag = note(freq, dur, amplitude=amp, waveform=waveform)
        fragments.append(frag.flatten())
    return np.concatenate(fragments)

def generate_and_play(prompt, waveform='sine', retries=3):
    print(f"\nPrompt: {prompt}")
    original_prompt = prompt
    for attempt in range(1, retries + 1):
        print(f"  Attempt {attempt}/{retries}...")
        raw = ask_ollama(prompt)
        print(f"  Raw response:\n  {raw[:120]}{'...' if len(raw) > 120 else ''}\n")
        try:
            notes = parse_json(raw)
            print(f"  Parsed {len(notes)} notes.")
            wave  = render(notes, waveform=waveform)
            play(wave)
            filename = original_prompt[:20].replace(" ", "_") + ".wav"
            save(wave, filename)
            return
        except Exception as e:
            print(f"  Error: {e}")
            prompt = (
                f"{original_prompt}\n\n"
                f"Your previous attempt failed with: {e}\n"
                f"Return ONLY a raw JSON array. No markdown, no explanation. "
                f"Every object must have note (48-84), duration (0.1-1.0), velocity (0-127)."
            )
    print(f"  Failed after {retries} attempts.")

# ── Prompts ───────────────────────────────────────────────────────────────────
prompts = [
    "Compose a 12-note jazz melody in C major.",
]

for prompt in prompts:
    generate_and_play(prompt, waveform='sine')