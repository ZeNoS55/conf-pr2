"""PlantUML diagram generation and visualization module."""

import os
import subprocess
import sys
import urllib.error
import urllib.request
import zlib
from typing import Optional
from src.graph import GraphResult

ZERO = 0
ONE = 1
TWO = 2
THREE = 3
CHUNK_SIZE = 3
SHIFT_TWO = 2
SHIFT_FOUR = 4
SHIFT_SIX = 6
MASK_THREE = 0x3
MASK_FIFTEEN = 0xF
MASK_SIXTY_THREE = 0x3F
EMPTY_COUNT = 0
TIMEOUT_SECONDS = 15
USER_AGENT = "Mozilla/5.0"

PLANTUML_CHARS = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
)


def generate_plantuml_text(graph: GraphResult) -> str:
    """Generate PlantUML diagram source code from graph result."""
    lines = [
        "@startuml",
        "skinparam roundcorner 12",
        "skinparam componentStyle rectangle",
        f'[{graph.root}] #LightBlue',
    ]

    cycle_set = set(graph.cycles)

    for src in sorted(graph.adj.keys()):
        for dst in sorted(graph.adj[src]):
            if (src, dst) in cycle_set:
                lines.append(f"[{src}] ..> [{dst}] : cycle")
            else:
                lines.append(f"[{src}] --> [{dst}]")

    lines.append("@enduml")
    return "\n".join(lines)


def encode_3bytes(b1: int, b2: int, b3: int) -> str:
    """Encode three bytes into four PlantUML 6-bit characters."""
    c1 = b1 >> SHIFT_TWO
    c2 = ((b1 & MASK_THREE) << SHIFT_FOUR) | (b2 >> SHIFT_FOUR)
    c3 = ((b2 & MASK_FIFTEEN) << SHIFT_TWO) | (b3 >> SHIFT_SIX)
    c4 = b3 & MASK_SIXTY_THREE
    return (
        PLANTUML_CHARS[c1]
        + PLANTUML_CHARS[c2]
        + PLANTUML_CHARS[c3]
        + PLANTUML_CHARS[c4]
    )


def encode_plantuml(text: str) -> str:
    """Encode PlantUML text into PlantUML URL-safe base64 string."""
    compressed = zlib.compress(text.encode("utf-8"))[TWO:-4]
    result = []
    idx = ZERO
    length = len(compressed)

    while idx < length:
        b1 = compressed[idx]
        b2 = compressed[idx + ONE] if (idx + ONE) < length else ZERO
        b3 = compressed[idx + TWO] if (idx + TWO) < length else ZERO
        chunk = encode_3bytes(b1, b2, b3)

        if (idx + TWO) < length:
            result.append(chunk)
        elif (idx + ONE) < length:
            result.append(chunk[:THREE])
        else:
            result.append(chunk[:TWO])

        idx += CHUNK_SIZE

    return "".join(result)


def render_plantuml_to_png(plantuml_text: str, output_png_path: str) -> bool:
    """Download rendered PNG image from PlantUML server."""
    encoded = encode_plantuml(plantuml_text)
    url = f"http://www.plantuml.com/plantuml/png/~1{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = resp.read()
            with open(output_png_path, "wb") as file_handle:
                file_handle.write(data)
            return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def display_image_on_screen(image_path: str, no_gui: bool = False) -> None:
    """Open generated graph image using the system default image viewer."""
    if no_gui or not os.path.isfile(image_path):
        return

    abs_path = os.path.abspath(image_path)
    if hasattr(os, "startfile"):
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", abs_path])
    else:
        subprocess.Popen(["xdg-open", abs_path])
