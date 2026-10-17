"""Checks on a finished video. Needs opencv-python + numpy.
  python qa.py blank  <video> [end_card_start_s]   flag near-empty frames, print last-frame brightness
  python qa.py sheet  <video> [n=12]               timestamped contact sheet -> <dir>/sheets/
  python qa.py phone  <video>                      6 frames scaled to 360 px wide (phone readability)
  python qa.py loop   <video>                      first vs last frame difference (~0 for a clean loop)
"""
import sys
from pathlib import Path
import cv2
import numpy as np


def frames_at(v, ts, width):
    cap = cv2.VideoCapture(v)
    out = []
    for t in ts:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, im = cap.read()
        if not ok:
            continue
        h, w = im.shape[:2]
        im = cv2.resize(im, (width, int(h * width / w)))
        for c, th in (((0, 0, 0), 4), ((255, 255, 255), 2)):
            cv2.putText(im, f"{t:.2f}s", (6, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, c, th)
        out.append(im)
    return out


def grid(tiles, cols):
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    return np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])


def info(v):
    cap = cv2.VideoCapture(v)
    return cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


def sheets_dir(v):
    d = Path(v).parent / "sheets"
    d.mkdir(exist_ok=True)
    return d


def blank(v, end_t=1e9):
    fps, n = info(v)
    cap = cv2.VideoCapture(v)
    flag, last = [], None
    for i in range(n):
        ok, im = cap.read()
        if not ok:
            break
        last = im
        sm = cv2.resize(im, (160, 90)).astype(np.int16)
        _, cnt = np.unique((sm // 12).reshape(-1, 3), axis=0, return_counts=True)
        dom, std = cnt.max() / (160 * 90), sm.std()
        if i / fps < end_t and (dom > 0.6 or std < 8):
            flag.append((i, round(float(dom), 2), round(float(std), 1)))
    print(f"frames={n} fps={fps:.2f} flagged={len(flag)}", flag[:20])
    print("last frame mean", round(float(last.mean()), 1), "(black is ~0; a finished last frame should not be black)")


def sheet(v, n=12):
    fps, total = info(v)
    tiles = frames_at(v, np.linspace(0.3, total / fps - 0.05, int(n)), 480)
    p = sheets_dir(v) / f"{Path(v).stem}-sheet.png"
    cv2.imwrite(str(p), grid(tiles, 4))
    print("sheet", p)


def phone(v):
    fps, total = info(v)
    tiles = frames_at(v, np.linspace(0.5, total / fps - 0.1, 6), 360)
    p = sheets_dir(v) / f"{Path(v).stem}-phone.png"
    cv2.imwrite(str(p), grid(tiles, 3))
    print("phone", p, "- can you still read every word?")


def loop(v):
    fps, n = info(v)
    cap = cv2.VideoCapture(v)
    _, a = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES, n - 1)
    _, b = cap.read()
    d = float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())
    print(f"first/last mean abs diff = {d:.2f} ({'loops cleanly' if d < 3 else 'visible jump at the loop point'})")


if __name__ == "__main__":
    cmd, v, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    {"blank": blank, "sheet": sheet, "phone": phone, "loop": loop}[cmd](v, *[float(x) for x in rest])
