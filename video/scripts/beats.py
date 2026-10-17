"""Measure a music track before animating to it.  pip install numpy librosa soundfile
  python beats.py song.wav > beats.json   ->  {bpm, beats[], downbeats[], duration}
State changes go on beats, big moments on downbeats. Cut the track on a bar boundary and fade out in numpy."""
import json
import sys

import librosa

y, sr = librosa.load(sys.argv[1], sr=None, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
beats = [round(float(b), 3) for b in beats]
print(json.dumps({"bpm": round(float(tempo), 2), "beats": beats, "downbeats": beats[::4],
                  "duration": round(len(y) / sr, 2)}))
