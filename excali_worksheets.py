#!/usr/bin/env python3
"""
generate_excalidraw_from_txt.py

Reads a .txt file with lines like:
1. hello _____
2. bob is a _____

Generates a .excalidraw file with one locked text element per line.

Usage:
    python generate_excalidraw_from_txt.py input.txt output.excalidraw
"""

import json
import sys
import random
import time
import uuid
from pathlib import Path

# === CONFIGURABLE SETTINGS ===
FONT_SIZE = 52          # 🧩 Adjust this to change the text size
START_X = 100           # Initial X coordinate for first text element
START_Y = 100           # Initial Y coordinate
LINE_SPACING = 200      # Vertical spacing between lines
FONT_FAMILY = 1         # 1 = Virgil, 2 = Helvetica, 3 = Cascadia
# ==============================


def rand_id():
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def now_ts():
    """Current timestamp (ms)."""
    return int(time.time() * 1000)


def make_text_element(text, x, y):
    """Return a minimal Excalidraw text element with locking enabled."""
    font_size = FONT_SIZE
    # 2x bigger width for pen annotation space: approximately 2.4 * font_size per character
    width = max(1200, len(text) * int(font_size * 2.4))
    height = int(font_size * 5.0)

    return {
        "id": rand_id(),
        "type": "text",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": "black",
        "backgroundColor": "transparent",
        "fillStyle": "hachure",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "seed": random.randint(0, 2**31),
        "version": 1,
        "versionNonce": random.randint(0, 2**31),
        "isDeleted": False,
        "groupIds": [],
        "strokeSharpness": "sharp",
        "boundElementIds": None,
        # 🔒 This flag makes the text locked in Excalidraw
        "locked": True,
        "text": text,
        "fontSize": font_size,
        "fontFamily": FONT_FAMILY,
        "textAlign": "left",
        "verticalAlign": "top",
        "baseline": font_size,
        "containerId": None,
        "originalText": text,
        "updated": now_ts(),
    }


def build_excalidraw_doc(elements):
    """Create a valid Excalidraw document object."""
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "python-script",
        "elements": elements,
        "appState": {
            "theme": "light",
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
            "currentItemStrokeColor": "black",
            "currentItemBackgroundColor": "transparent",
        },
        "files": {},
        "scrollToContent": True,
        "created": now_ts(),
        "lastModified": now_ts(),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python excali_worksheets.py input.txt")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    
    if not input_path.exists():
        print(f"Error: file '{input_path}' not found.")
        sys.exit(1)

    # Create excalidraw directory if it doesn't exist
    excalidraw_dir = Path("excalidraw")
    excalidraw_dir.mkdir(exist_ok=True)
    
    # Generate output filename based on input filename
    output_filename = input_path.stem + ".excalidraw"
    output_path = excalidraw_dir / output_filename

    # Read lines from the input file
    with input_path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    elements = []
    x, y = START_X, START_Y
    for line in lines:
        elements.append(make_text_element(line, x, y))
        y += LINE_SPACING

    doc = build_excalidraw_doc(elements)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)

    print(f"✅ Generated {len(elements)} text elements in '{output_path}'.")


if __name__ == "__main__":
    main()
