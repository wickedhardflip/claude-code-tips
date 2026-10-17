"""Tile out/f<N>.png stills into one contact sheet. usage: python sheet.py <name> <frame>... [--cols 2]"""
import sys
from PIL import Image, ImageDraw

args = sys.argv[1:]
cols = 2
if "--cols" in args:
    i = args.index("--cols")
    cols = int(args[i + 1])
    del args[i:i + 2]
name, frames = args[0], args[1:]
tw, th = 640, 360
ims = [Image.open(f"out/f{f}.png").convert("RGB").resize((tw, th)) for f in frames]
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (tw * cols, th * rows))
for i, (f, im) in enumerate(zip(frames, ims)):
    ImageDraw.Draw(im).text((8, 6), f"f{f}", fill=(255, 255, 0))
    sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
sheet.save(f"out/{name}.png")
