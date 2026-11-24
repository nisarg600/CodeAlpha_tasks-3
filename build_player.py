import json
import pretty_midi

midi = pretty_midi.PrettyMIDI('output/generated_music.mid')
notes = []
for n in midi.instruments[0].notes:
    notes.append({
        'pitch': int(n.pitch),
        'start': round(float(n.start), 3),
        'end': round(float(n.end), 3)
    })

notes_json = json.dumps(notes)
duration = notes[-1]['end'] if notes else 0.0

html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Music Generation - Interactive Player</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0f172a;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            padding: 30px 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: #1e293b;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            padding: 30px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            background: #0f172a;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #334155;
        }
        .stat-item { text-align: center; }
        .stat-value {
            font-size: 20px;
            font-weight: 700;
            color: #38bdf8;
        }
        .stat-label {
            font-size: 13px;
            color: #94a3b8;
            margin-top: 4px;
        }
        .controls {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
        }
        button {
            background: linear-gradient(135deg, #0284c7, #6366f1);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 9999px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
            transition: all 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        canvas {
            width: 100%;
            height: 260px;
            background: #090d16;
            border-radius: 12px;
            border: 1px solid #334155;
        }
        .audio-link {
            text-align: center;
            font-size: 14px;
            color: #94a3b8;
        }
        .audio-link a {
            color: #38bdf8;
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Music Generation - Piano Roll Player</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">""" + str(len(notes)) + """</div>
                <div class="stat-label">Total Notes</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">""" + f"{duration:.1f}" + """s</div>
                <div class="stat-label">Duration</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">PyTorch LSTM</div>
                <div class="stat-label">Model Type</div>
            </div>
        </div>

        <canvas id="pianoRoll"></canvas>

        <div class="controls">
            <button id="playBtn">&#9654; Play AI Composition</button>
            <button id="stopBtn" disabled>&#9209; Stop</button>
        </div>

        <div class="audio-link">
            Files ready in project: 
            <a href="output/generated_music.wav" download>output/generated_music.wav</a> &bull; 
            <a href="output/generated_music.mid" download>output/generated_music.mid</a>
        </div>
    </div>

    <script>
        const notes = """ + notes_json + """;
        const playBtn = document.getElementById('playBtn');
        const stopBtn = document.getElementById('stopBtn');
        const canvas = document.getElementById('pianoRoll');
        const ctx = canvas.getContext('2d');

        canvas.width = canvas.clientWidth * window.devicePixelRatio;
        canvas.height = canvas.clientHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        let audioCtx = null;
        let isPlaying = false;
        let startTime = 0;
        let activeNodes = [];
        let animationId = null;

        const totalDuration = notes.length ? notes[notes.length - 1].end : 0;
        const pitches = notes.map(n => n.pitch);
        const minPitch = Math.max(0, Math.min(...pitches) - 2);
        const maxPitch = Math.min(127, Math.max(...pitches) + 2);

        function draw(progressTime = 0) {
            const w = canvas.clientWidth;
            const h = canvas.clientHeight;
            ctx.clearRect(0, 0, w, h);

            // Draw pitch grid
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            for (let p = minPitch; p <= maxPitch; p++) {
                const y = h - ((p - minPitch) / (maxPitch - minPitch || 1)) * h;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }

            // Draw notes
            notes.forEach(note => {
                const x = (note.start / totalDuration) * w;
                const width = Math.max(3, ((note.end - note.start) / totalDuration) * w - 1);
                const y = h - ((note.pitch - minPitch) / (maxPitch - minPitch || 1)) * h;
                const isCurrent = progressTime >= note.start && progressTime <= note.end;

                ctx.fillStyle = isCurrent ? '#38bdf8' : '#818cf8';
                ctx.fillRect(x, y - 6, width, 10);
            });

            // Draw playhead
            if (progressTime > 0) {
                const playX = (progressTime / totalDuration) * w;
                ctx.strokeStyle = '#f43f5e';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(playX, 0);
                ctx.lineTo(playX, h);
                ctx.stroke();
            }
        }

        draw(0);

        function playNote(pitch, when, duration) {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            const freq = 440 * Math.pow(2, (pitch - 69) / 12);

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, when);

            gain.gain.setValueAtTime(0.001, when);
            gain.gain.exponentialRampToValueAtTime(0.2, when + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(when);
            osc.stop(when + duration);
            activeNodes.push(osc);
        }

        function startPlayback() {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();

            isPlaying = true;
            playBtn.disabled = true;
            stopBtn.disabled = false;

            const now = audioCtx.currentTime;
            startTime = now;

            notes.forEach(n => {
                playNote(n.pitch, now + n.start, n.end - n.start);
            });

            function loop() {
                if (!isPlaying) return;
                const elapsed = audioCtx.currentTime - startTime;
                draw(elapsed);
                if (elapsed < totalDuration) {
                    animationId = requestAnimationFrame(loop);
                } else {
                    stopPlayback();
                }
            }
            loop();
        }

        function stopPlayback() {
            isPlaying = false;
            playBtn.disabled = false;
            stopBtn.disabled = true;
            cancelAnimationFrame(animationId);
            activeNodes.forEach(node => {
                try { node.stop(); } catch(e) {}
            });
            activeNodes = [];
            draw(0);
        }

        playBtn.addEventListener('click', startPlayback);
        stopBtn.addEventListener('click', stopPlayback);
    </script>
</body>
</html>
"""

with open('player.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('player.html successfully generated!')
