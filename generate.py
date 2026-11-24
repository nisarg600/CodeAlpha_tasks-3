import os
import numpy as np
import torch
import torch.nn as nn
import pretty_midi

# Model definition (matches train.py)
class MusicLSTM(nn.Module):
    def __init__(self, vocab_size=128, embed_dim=64, hidden_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        return self.fc(x)

def generate_music(model_path="music_model.pth", 
                   data_path="sequences.npy", 
                   output_path="output/generated_music.mid",
                   num_notes_to_generate=100,
                   temperature=0.85):
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_path}' not found. Please run train.py first.")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file '{data_path}' not found. Please run preprocess.py first.")

    # Load trained model
    model = MusicLSTM().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print(f"Loaded trained model from '{model_path}'.")

    # Load starting seed notes
    data = np.load(data_path)
    seed_notes = list(data[0][:50])
    seed = torch.tensor(seed_notes, dtype=torch.long, device=device).unsqueeze(0)
    generated = list(seed_notes)

    print(f"Starting seed with {len(seed_notes)} notes.")
    print(f"Generating {num_notes_to_generate} new notes (temperature={temperature})...")

    # Generate new notes using autoregressive generation
    with torch.no_grad():
        current_input = seed
        for step in range(num_notes_to_generate):
            # Forward pass through model
            logits = model(current_input)
            
            # Extract prediction for the next note (last timestep)
            next_note_logits = logits[0, -1, :] / max(temperature, 1e-4)
            probs = torch.softmax(next_note_logits, dim=-1)

            # Sample next note
            next_note = torch.multinomial(probs, num_samples=1).item()
            generated.append(next_note)

            # Update input window: slide by 1 or append
            # Using last 50 notes to maintain consistent context
            new_input_notes = generated[-50:]
            current_input = torch.tensor(new_input_notes, dtype=torch.long, device=device).unsqueeze(0)

    print(f"Total notes in composition: {len(generated)}")

    # Convert generated notes to MIDI
    midi = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)

    current_time = 0.0
    note_duration = 0.35  # Duration of each note in seconds

    for pitch in generated:
        # Clamp pitch to valid MIDI range [0, 127]
        safe_pitch = max(0, min(127, int(pitch)))
        note = pretty_midi.Note(
            velocity=95,
            pitch=safe_pitch,
            start=current_time,
            end=current_time + note_duration
        )
        piano.notes.append(note)
        current_time += note_duration

    midi.instruments.append(piano)

    # Save generated MIDI
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    midi.write(output_path)
    print(f"\nGenerated music successfully saved to: {output_path}")
    print(f"Duration: {current_time:.1f} seconds")

if __name__ == "__main__":
    generate_music()
