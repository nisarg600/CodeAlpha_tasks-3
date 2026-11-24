# AI Music Generation using PyTorch & LSTM

An end-to-end Deep Learning system that learns musical patterns from classical compositions and generates original piano music in MIDI and WAV audio formats.

---

## 🎼 Project Architecture

```
codeAlpha project 3/
├── dataset/                    # 35 Classical Bach MIDI compositions
│   ├── bach_01.mid
│   ├── ...
│   └── bach_35.mid
├── output/                     # Generated music outputs
│   ├── generated_music.mid     # Standard MIDI format
│   └── generated_music.wav     # 16-bit PCM Audio (playable in any media player)
├── collect_dataset.py          # Extracts classical MIDI corpus
├── preprocess.py               # Parses MIDI pitch sequences into numerical arrays
├── train.py                    # Trains PyTorch LSTM neural network
├── generate.py                 # Autoregressively generates new musical sequences
├── export_wav.py               # Synthesizes MIDI into playable WAV audio
├── requirements.txt            # Python dependencies
├── sequences.npy               # Preprocessed note sequences array (120 sequences)
└── music_model.pth             # Trained LSTM PyTorch weights
```

---

## 🚀 Step-by-Step Execution Guide

### 1. Requirements & Environment
The required libraries are:
- `torch`: Deep learning framework (PyTorch)
- `pretty_midi`: MIDI parsing and generation
- `music21`: Musical corpus and analysis
- `numpy`: Numerical processing

To install in your virtual environment:
```bash
pip install -r requirements.txt
```

---

### 2. Collect MIDI Dataset
Collect classical piano pieces into the `dataset/` directory:
```bash
python collect_dataset.py
```
This populates `dataset/` with classical compositions.

---

### 3. Preprocess the MIDI Data
Convert musical notes and pitches into numerical sequences:
```bash
python preprocess.py
```
- Reads MIDI files with `pretty_midi`.
- Filters out non-melodic and percussion tracks.
- Extracts MIDI pitch numbers ($0 - 127$).
- Outputs `sequences.npy` (Shape: `(120, 100)`).

---

### 4. Train the Deep Learning Model (LSTM)
Train the recurrent neural network:
```bash
python train.py
```
- **Architecture**:
  - `nn.Embedding(128, 64)`: Projects pitch integers into a 64-dimensional vector space.
  - `nn.LSTM(64, 128, batch_first=True)`: Recurrent network learning temporal pitch transitions.
  - `nn.Linear(128, 128)`: Predicts probabilities across all 128 possible MIDI notes.
- Loss function: Cross Entropy Loss.
- Saves the trained model to `music_model.pth`.

---

### 5. Generate New Music
Generate a new composition seeded by classical motifs:
```bash
python generate.py
```
- Loads the trained model weights from `music_model.pth`.
- Seeds generation with the initial notes of a piece.
- Uses temperature-based autoregressive sampling (`temperature=0.85`) to predict 100 new notes.
- Creates `output/generated_music.mid`.

---

### 6. Play and Listen to Your Music
You have two easy ways to listen:

#### Option A: Direct WAV Audio (Zero Setup)
Synthesize the generated MIDI into a high-fidelity WAV audio file:
```bash
python export_wav.py
```
Open and play `output/generated_music.wav` directly in Windows Media Player, Groove Music, VLC, or any browser!

#### Option B: MIDI & Sheet Music Software
Open `output/generated_music.mid` using:
- **MuseScore**: View score notation and play piano instrument.
- **VLC Media Player** or **Windows Media Player**.
- **Ableton Live**, **FL Studio**, or **GarageBand** for DAWs.
