import ollama
import re
import pygame
from music21 import converter, midi as m21midi, stream, meter

# Configure your server URL here
SERVER_HOST = 'http://ollama.cs.wallawalla.edu:11434'
client = ollama.Client(host=SERVER_HOST)

SYSTEM = """You are a music composer who writes in ABC notation.
Respond ONLY with valid ABC notation. No explanation. No markdown. No extra text after the notes.

STRICT RULES:
1. Always include L:1/8 header — this is required.
2. M: must be exactly one of: 4/4  3/4  6/8  2/4
3. K: must be a standard key like: C  G  D  A  E  F  Amin  Dmin  Emin
4. Notes are letters A-G only. Use lowercase for one octave up (a,b,c...).
5. Accidentals: ^A = A sharp, _B = B flat. Never use # or b.
6. Duration multipliers only: A2 = double length, A/2 = half length.
7. No comments. No text after the last bar line.
8. End every line of music with a bar line |

VALID EXAMPLE:
X:1
T:Simple Tune
M:4/4
L:1/8
K:G
G2 AB c2 BA | G4 D4 | E2 FG A2 GF | G8 |"""

def ask_ollama(prompt):
    response = client.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": prompt},
        ]
    )
    return response["message"]["content"]

def clean_abc(text):
    text = re.sub(r"```[a-z]*", "", text)
    text = re.sub(r"```", "", text)
    lines    = []
    in_music = False
    has_L    = False
    has_X    = False
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r'^[A-Z]:', line):
            if line.startswith('X:'): has_X = True
            if line.startswith('L:'): has_L = True
            if line.startswith('K:'): in_music = True
            lines.append(line)
        elif in_music and re.search(r'[A-Ga-gz|]', line):
            line = re.sub(r'\|[^|A-Ga-gz\s]*$', '|', line)
            lines.append(line)

    if not has_X:
        lines.insert(0, 'X:1')
    if not has_L:
        for i, l in enumerate(lines):
            if l.startswith('K:'):
                lines.insert(i, 'L:1/8')
                break
    return '\n'.join(lines)

def validate_abc(text):
    errors = []
    for line in text.splitlines():
        if line.startswith('L:'):
            val = line[2:].strip()
            if val not in ('1/8', '1/4', '1/16', '1/2', '1'):
                errors.append(f"Bad L: value '{val}' — must be 1/8, 1/4, or 1/16")
        if line.startswith('K:'):
            val = line[2:].strip()
            if re.search(r'[^A-Ga-gmin#b ]', val):
                errors.append(f"Suspicious K: value '{val}'")
        if not line.startswith(('X:', 'T:', 'M:', 'L:', 'K:', 'Q:')):
            if re.search(r'\b[A-Ga-gN][1-9][0-9]+', line):
                errors.append(f"Possible MIDI-style pitch in: {line}")
            if re.search(r'\(Note:', line, re.IGNORECASE):
                errors.append(f"Trailing comment in: {line}")
    return errors

def fix_duplicate_timesig(score):
    """
    Workaround for music21 bug: TimeSignature already in Stream.
    Flatten the score and remove duplicate time signatures manually.
    """
    for part in score.parts:
        seen = set()
        for ts in part.recurse().getElementsByClass(meter.TimeSignature):
            key = (ts.numerator, ts.denominator)
            if key in seen:
                part.remove(ts, recurse=True)
            else:
                seen.add(key)
    return score

def abc_to_midi(abc_text, out_path="ollama_abc.mid"):
    score = converter.parse(abc_text, format='abc')
    score = fix_duplicate_timesig(score)
    mf    = m21midi.translate.music21ObjectToMidiFile(score)
    mf.open(out_path, 'wb')
    mf.write()
    mf.close()
    print(f"MIDI written: {out_path}")
    return out_path

def play_midi(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

def generate_and_play(prompt, retries=4):
    print(f"\nPrompt: {prompt}")
    original_prompt = prompt
    for attempt in range(1, retries + 1):
        print(f"  Attempt {attempt}/{retries}...")
        raw = ask_ollama(prompt)
        abc = clean_abc(raw)
        print(f"  Cleaned ABC:\n{abc}\n")

        errors = validate_abc(abc)
        if errors:
            print(f"  Validation failed: {errors}")
            prompt = (f"{original_prompt}\n\nYour previous attempt had errors: "
                      f"{errors}. Fix them. Remember: always include L:1/8.")
            continue

        try:
            path = abc_to_midi(abc)
            play_midi(path)
            return
        except Exception as e:
            print(f"  Parse error: {e}")
            prompt = (f"{original_prompt}\n\nPrevious attempt failed: {e}. "
                      f"Write simpler ABC. Use L:1/8 and only basic notes.")

    print(f"  Failed after {retries} attempts.")

# ── Prompts ───────────────────────────────────────────────────────────────────
prompts = [
    "Compose a melody in Dorian mode — dark but not quite minor.",
    "Compose a waltz melody in 3/4 time."
]

for prompt in prompts:
    generate_and_play(prompt)