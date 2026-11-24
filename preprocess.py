import glob
import numpy as np
import pretty_midi
import os

def preprocess_midi_files(dataset_dir="dataset", output_file="sequences.npy", seq_len=100):
    sequences = []
    files = glob.glob(os.path.join(dataset_dir, "*.mid"))
    
    if not files:
        print(f"No MIDI files found in '{dataset_dir}'. Please collect dataset first.")
        return

    print(f"Found {len(files)} MIDI files in '{dataset_dir}'. Extracting note sequences...")

    for file in files:
        try:
            midi = pretty_midi.PrettyMIDI(file)
            notes = []
            for instrument in midi.instruments:
                if not instrument.is_drum:
                    for note in instrument.notes:
                        notes.append((note.start, note.pitch))
            notes.sort()
            pitches = [pitch for start, pitch in notes]
            
            # Beginner version: extracts notes and creates sequences
            if len(pitches) >= 51:
                sequences.append(pitches)
                
                # Also extract non-overlapping chunks of 100 notes if file is long
                # to provide richer training data while preserving shape
                for i in range(100, len(pitches), 50):
                    chunk = pitches[i : i + seq_len]
                    if len(chunk) == seq_len:
                        sequences.append(chunk)

        except Exception as e:
            print("Error:", file, e)

    filtered_sequences = [s[:seq_len] for s in sequences if len(s) >= seq_len]
    np.save(output_file, np.array(filtered_sequences, dtype=np.int64))

    print("Preprocessing completed!")
    print(f"Total sequences extracted: {len(filtered_sequences)}")
    print(f"Saved dataset array to: {output_file} with shape {np.array(filtered_sequences).shape}")

if __name__ == "__main__":
    preprocess_midi_files()
