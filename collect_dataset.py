import os
import sys
from music21 import corpus

def download_or_export_classical_midi(num_files=35, output_dir="dataset"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Collecting {num_files} classical MIDI files into '{output_dir}'...")

    works = corpus.getComposer('bach')
    count = 0
    
    for work in works:
        if count >= num_files:
            break
        try:
            score = corpus.parse(work)
            out_path = os.path.join(output_dir, f"bach_{count + 1:02d}.mid")
            score.write('midi', fp=out_path)
            count += 1
            print(f"[{count:02d}/{num_files}] Saved: {out_path}")
        except Exception as e:
            print(f"Skipping {work}: {e}")
            continue

    print(f"\nDone! Successfully collected {count} classical MIDI files in '{output_dir}'.")

if __name__ == "__main__":
    num = 35
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    download_or_export_classical_midi(num)
