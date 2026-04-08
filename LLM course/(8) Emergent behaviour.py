"""
Whiteboard explainer: Emergent Behavior in AI

This scene is a short ~30 second animation explaining "Emergent Behavior".
It uses a landscape 1920x1080 canvas, edge-tts narration, handwritten fonts,
and progressive sketch animations radiating outwards to show scale.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts or uv add --dev edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, Circle, FlowchartProcess
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_ORANGE
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output"
AUDIO_PATH = OUTPUT_DIR / "emergent_behavior_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "emergent_behavior_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> What is Emergent Behavior in AI? "
    "<bookmark mark='def'/> Simply put, it's when a system develops complex abilities that it was never explicitly programmed to do. "
    "<bookmark mark='example'/> For example, we train Large Language Models on a very simple rule: just predict the next word. "
    "<bookmark mark='emergence'/> But as we add billions of parameters and scale up the data, something magical happens. "
    "The model suddenly learns to translate languages, write code, and solve logic puzzles. "
    "<bookmark mark='outro'/> These skills weren't programmed; they emerged purely from scale. Thanks for watching!"
)

BOOKMARK_RE = re.compile(r"<bookmark\s+(?:mark|name)\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

async def synthesize_narration(
    audio_path: Path, *, regenerate: bool = False, voice: str = VOICE
) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    if audio_path.exists() and not regenerate:
        return

    communicate = edge_tts.Communicate(strip_bookmarks(NARRATION), voice, rate=VOICE_RATE)
    await communicate.save(str(audio_path))

def make_title(text: str, *, y: float, color: tuple[float, float, float] = BLACK) -> Text:
    return Text(
        text,
        position=(960, y),
        font_size=100,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=4.0),
        sketch_style=SKETCH,
    )

def make_body(
    text: str, *, x: float = 960, y: float, color: tuple[float, float, float] = BLACK, align: str = "center", font_size: int = 56
) -> Text:
    return Text(
        text,
        position=(x, y),
        font_size=font_size,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=3.5),
        sketch_style=SKETCH,
        align=align,
    )

def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.2) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()


def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        intro_start = tracker.bookmark_time("intro")
        def_start = tracker.bookmark_time("def")
        example_start = tracker.bookmark_time("example")
        emergence_start = tracker.bookmark_time("emergence")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro & Definition
        # ---------------------------------------------------------
        intro_title = make_title("Emergent Behavior", y=350, color=BLUE)
        def_text = make_body("Complex abilities from simple rules.", y=550, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=intro_start + 0.2, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=def_start + 0.5, duration=2.0), drawable=def_text)

        intro_drawables = [intro_title, def_text]

        # ---------------------------------------------------------
        # SECTION 2: The Simple Rule & Massive Scale (Radiating Visual)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=example_start - 1.2)

        scale_drawables =[]

        # The core simple rule
        core_box = FlowchartProcess(
            "Simple Rule:\nPredict Next Word", 
            top_left=(760, 450), width=400, height=180, 
            font_size=48, 
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), 
            stroke_style=box_stroke
        )

        # The emergence boundary (Massive Scale)
        scale_circle = Circle(
            center=(960, 540), radius=350, 
            stroke_style=StrokeStyle(color=ORANGE, width=4.0, opacity=0.5), 
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.1, hachure_gap=15),
            sketch_style=SKETCH
        )
        scale_label = make_body("Massive Scale (Billions of Params)", x=960, y=940, color=ORANGE, font_size=52)

        # Emergent Skills (shooting outwards)
        arr1 = Arrow(start_point=(960, 450), end_point=(960, 250), stroke_style=StrokeStyle(color=GREEN, width=4.0))
        skill1 = make_body("Translation", x=960, y=180, color=GREEN, font_size=56)

        arr2 = Arrow(start_point=(760, 540), end_point=(400, 540), stroke_style=StrokeStyle(color=RED, width=4.0))
        skill2 = make_body("Writing Code", x=240, y=540, color=RED, font_size=56)

        arr3 = Arrow(start_point=(1160, 540), end_point=(1520, 540), stroke_style=StrokeStyle(color=PURPLE, width=4.0))
        skill3 = make_body("Logic & Reasoning", x=1680, y=540, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=example_start + 0.5, duration=1.5), drawable=core_box)
        
        # Scale up happens at emergence_start
        scene.add(SketchAnimation(start_time=emergence_start + 0.5, duration=1.5), drawable=scale_circle)
        scene.add(SketchAnimation(start_time=emergence_start + 1.0, duration=1.0), drawable=scale_label)

        # Skills pop out
        scene.add(SketchAnimation(start_time=emergence_start + 3.0, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=emergence_start + 3.5, duration=1.0), drawable=skill1)

        scene.add(SketchAnimation(start_time=emergence_start + 4.5, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=emergence_start + 5.0, duration=1.0), drawable=skill2)

        scene.add(SketchAnimation(start_time=emergence_start + 6.0, duration=0.8), drawable=arr3)
        scene.add(SketchAnimation(start_time=emergence_start + 6.5, duration=1.0), drawable=skill3)

        scale_drawables.extend([core_box, scale_circle, scale_label, arr1, skill1, arr2, skill2, arr3, skill3])

        # ---------------------------------------------------------
        # SECTION 3: Outro
        # ---------------------------------------------------------
        make_eraser(scale_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("Scale is all you need.", y=600, color=BLACK)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.5), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 2.0, duration=1.5), drawable=outro_body)

        return tracker.end_time + 1.0


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")
    print(f"Video saved to: {VIDEO_PATH}")


if __name__ == "__main__":
    main()