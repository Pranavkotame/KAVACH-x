"""
Generate a Morse code WAV audio file for the CTF challenge.
The audio spells out: MORSECODE
The flag answer: FLAG{morse_code}
"""

import wave
import struct
import math

# Morse code lookup
MORSE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
}

# Audio parameters
SAMPLE_RATE = 44100
FREQ = 700          # Hz - tone frequency
DOT_MS = 100        # milliseconds per dot
AMPLITUDE = 0.7

def generate_tone(duration_ms):
    """Generate a sine wave tone."""
    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        value = AMPLITUDE * math.sin(2 * math.pi * FREQ * t)
        # Apply fade in/out to avoid clicks (5ms fade)
        fade_samples = int(SAMPLE_RATE * 0.005)
        if i < fade_samples:
            value *= i / fade_samples
        elif i > n_samples - fade_samples:
            value *= (n_samples - i) / fade_samples
        samples.append(value)
    return samples

def generate_silence(duration_ms):
    """Generate silence."""
    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    return [0.0] * n_samples

def text_to_morse_audio(text):
    """Convert text to Morse code audio samples."""
    samples = []
    # Add a brief silence at start
    samples.extend(generate_silence(300))

    words = text.upper().split()
    for w_idx, word in enumerate(words):
        for c_idx, char in enumerate(word):
            if char not in MORSE:
                continue
            morse = MORSE[char]
            for s_idx, symbol in enumerate(morse):
                if symbol == '.':
                    samples.extend(generate_tone(DOT_MS))
                elif symbol == '-':
                    samples.extend(generate_tone(DOT_MS * 3))
                # Gap between symbols within a letter
                if s_idx < len(morse) - 1:
                    samples.extend(generate_silence(DOT_MS))
            # Gap between letters (3 dots)
            if c_idx < len(word) - 1:
                samples.extend(generate_silence(DOT_MS * 3))
        # Gap between words (7 dots)
        if w_idx < len(words) - 1:
            samples.extend(generate_silence(DOT_MS * 7))

    # Add silence at end
    samples.extend(generate_silence(500))
    return samples

def save_wav(filename, samples):
    """Save samples as a WAV file."""
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)         # mono
        wav.setsampwidth(2)         # 16-bit
        wav.setframerate(SAMPLE_RATE)
        for s in samples:
            # Clamp and convert to 16-bit integer
            s = max(-1.0, min(1.0, s))
            wav.writeframes(struct.pack('<h', int(s * 32767)))

if __name__ == '__main__':
    message = "DRONACHARYA"
    print(f"Generating Morse audio for: {message}")
    print(f"Morse: {' / '.join(MORSE.get(c, '') for c in message if c != ' ')}")

    samples = text_to_morse_audio(message)
    duration = len(samples) / SAMPLE_RATE

    output = "static/signal.wav"
    import os
    os.makedirs("static", exist_ok=True)
    save_wav(output, samples)

    print(f"Saved: {output} ({duration:.1f}s, {len(samples)} samples)")
    print(f"Answer: DRONACHARYA")
