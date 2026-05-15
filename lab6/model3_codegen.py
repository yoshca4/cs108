import ollama
import re
import numpy as np
from synth import play, save, note, adsr, midi_to_freq, SR

# Configure your server URL here
SERVER_HOST = 'http://ollama.cs.wallawalla.edu:11434'
client = ollama.Client(host=SERVER_HOST)

SYSTEM = f"""You are a Python music programmer. You have access to exactly these names:

  SR = {SR}                          # int, sample rate

  note(freq, duration, amplitude=0.3, waveform='sine') -> np.ndarray
    # freq: Hz as a float
    # duration: seconds as a float
    # waveform: 'sine', 'sawtooth', or 'square'
    # returns a 1-D float32 numpy array

  midi_to_freq(midi_note) -> float
    # midi_note: int. Middle C = 60 = 261.63 Hz
    # A4 = 69 = 440 Hz

  np                                 # numpy, fully available

WORKING EXAMPLES — study these before writing code:

# Example 1: simple scale
wave = np.concatenate([
    note(midi_to_freq(m), 0.3)
    for m in [60, 62, 64, 65, 67]
])

# Example 2: rest = array of zeros
rest = np.zeros(int(SR * 0.25))     # 0.25 second silence
wave = np.concatenate([
    note(440.0, 0.2),
    rest,
    note(440.0, 0.2),
    rest,
])

# Example 3: chord = sum of arrays, padded to same length
a = note(midi_to_freq(60), 1.0)
b = note(midi_to_freq(64), 1.0)
c = note(midi_to_freq(67), 1.0)
wave = a + b + c

# Example 4: random melody
midi_pool = [60, 62, 64, 67, 69]
chosen    = np.random.choice(midi_pool, size=8)
wave      = np.concatenate([note(midi_to_freq(int(m)), 0.35) for m in chosen])

RULES:
- Never use note names like 'C4' or 'A#3'. Always use midi_to_freq(int).
- Never call functions that are not listed above.
- Never write import statements.
- The final result must be stored in a variable called `wave`.
- `wave` must be a 1-D numpy array. Never leave it as a list.
- For rests use np.zeros(int(SR * duration)).
- Do not call play() or save()."""

def ask_ollama(prompt):
    response = client.chat(
        model="qwen2.5-coder",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": prompt},
        ]
    )
    return response["message"]["content"]

def clean_code(text):
    text = re.sub(r"```[a-z]*", "", text)
    text = re.sub(r"```",       "", text)
    # Strip any import lines — model sometimes ignores the rule
    lines = [l for l in text.splitlines()
             if not l.strip().startswith("import")]
    return '\n'.join(lines).strip()

def run_code(code):
    namespace = {
        "np":           np,
        "note":         note,
        "adsr":         adsr,
        "midi_to_freq": midi_to_freq,
        "SR":           SR,
    }
    exec(code, namespace)
    if "wave" not in namespace:
        raise ValueError("No `wave` variable produced.")
    w = namespace["wave"]
    if not isinstance(w, np.ndarray):
        raise ValueError(f"`wave` is {type(w)}, expected np.ndarray.")
    if w.ndim != 1:
        raise ValueError(f"`wave` has shape {w.shape}, must be 1-D.")
    return w.astype(np.float32)

def generate_and_play(name, prompt, retries=3):
    print(f"\n--- {name} ---")
    original_prompt = prompt
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}/{retries}...")
        raw  = ask_ollama(prompt)
        code = clean_code(raw)
        print(f"Code:\n{code}\n")
        try:
            wave = run_code(code)
            print(f"OK — shape {wave.shape}")
            play(wave)
            save(wave, f"codegen_{name}.wav")
            return
        except Exception as e:
            print(f"Error: {e}")
            prompt = (
                f"{original_prompt}\n\n"
                f"Your previous attempt failed with: {e}\n"
                f"Remember: use midi_to_freq(int) not note names. "
                f"Rests are np.zeros(int(SR * dur)). "
                f"Result must be a 1-D array named `wave`."
            )
    print(f"Failed after {retries} attempts.")

# ── Prompts ───────────────────────────────────────────────────────────────────
tasks = [
    ("generative",
     "Write code that plays a 12-bar blues progression using MIDI notes.")
]

for name, prompt in tasks:
    generate_and_play(name, prompt)