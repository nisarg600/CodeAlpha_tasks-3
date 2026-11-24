import math
import struct
import wave
import numpy as np
import pretty_midi

def midi_pitch_to_frequency(pitch):
    return 440.0 * (2.0 ** ((pitch - 69) / 12.0))

def midi_to_wav(midi_path="output/generated_music.mid", wav_path="output/generated_music.wav", sample_rate=44100):
    midi = pretty_midi.PrettyMIDI(midi_path)
    total_time = midi.get_end_time() + 1.0
    total_samples = int(total_time * sample_rate)
    audio = np.zeros(total_samples, dtype=np.float32)

    for instrument in midi.instruments:
        for note in instrument.notes:
            freq = midi_pitch_to_frequency(note.pitch)
            start_sample = int(note.start * sample_rate)
            end_sample = int(note.end * sample_rate)
            duration_samples = end_sample - start_sample
            if duration_samples <= 0 or start_sample >= total_samples:
                continue

            t = np.linspace(0, note.end - note.start, duration_samples, endpoint=False)
            
            # Simple piano-like harmonic synthesis (Fundamental + Overtones)
            harmonic1 = np.sin(2 * np.pi * freq * t)
            harmonic2 = 0.5 * np.sin(2 * np.pi * 2 * freq * t)
            harmonic3 = 0.25 * np.sin(2 * np.pi * 3 * freq * t)
            harmonic4 = 0.125 * np.sin(2 * np.pi * 4 * freq * t)
            tone = harmonic1 + harmonic2 + harmonic3 + harmonic4

            # ADSR Envelope
            attack_len = min(int(0.02 * sample_rate), duration_samples)
            decay_len = duration_samples - attack_len
            attack = np.linspace(0, 1, attack_len)
            decay = np.exp(-3.0 * np.linspace(0, 1, decay_len))
            envelope = np.concatenate([attack, decay])

            note_audio = tone * envelope * (note.velocity / 127.0) * 0.2
            end_bound = min(start_sample + duration_samples, total_samples)
            actual_len = end_bound - start_sample
            audio[start_sample:end_bound] += note_audio[:actual_len]

    # Normalize audio to prevent clipping
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.9

    # Convert to 16-bit PCM WAV
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(wav_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())

    print(f"Synthesized audio WAV saved to: {wav_path} ({total_time:.1f} seconds)")

if __name__ == "__main__":
    midi_to_wav()
