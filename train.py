import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Check for GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load dataset
data_file = "sequences.npy"
if not os.path.exists(data_file):
    raise FileNotFoundError(f"'{data_file}' not found. Please run preprocess.py first.")

data = np.load(data_file)
print(f"Loaded {len(data)} note sequences from {data_file}.")

# Dataset class
class MusicDataset(Dataset):
    def __init__(self, sequences):
        self.sequences = sequences

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]
        # x is the sequence of notes, y is target sequence shifted by 1 note
        x = torch.tensor(seq[:-1], dtype=torch.long)
        y = torch.tensor(seq[1:], dtype=torch.long)
        return x, y

# LSTM Model
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

# Training configuration
batch_size = 16
epochs = 40
learning_rate = 0.005

dataset = MusicDataset(data)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

model = MusicLSTM().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

print("\nStarting Training...")
print(f"Epochs: {epochs} | Batch Size: {batch_size} | Learning Rate: {learning_rate}\n")

for epoch in range(1, epochs + 1):
    model.train()
    total_loss = 0.0

    for batch_x, batch_y in loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        optimizer.zero_grad()
        predictions = model(batch_x)

        # Reshape for CrossEntropyLoss: (batch * seq_len, vocab_size) vs (batch * seq_len)
        loss = criterion(predictions.view(-1, 128), batch_y.view(-1))
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(loader)
    if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
        print(f"Epoch [{epoch:02d}/{epochs}] - Loss: {avg_loss:.4f}")

# Save the trained model
model_path = "music_model.pth"
torch.save(model.state_dict(), model_path)
print(f"\nModel training finished successfully!")
print(f"Model saved to: {model_path}")
