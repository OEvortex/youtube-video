"""
Whiteboard explainer: Zero-Shot vs Few-Shot Learning

This scene is designed for a 1920x1080 landscape whiteboard animation
with edge-tts narration, handwritten fonts, and progressive sketch animations.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

# Ensure we can import edge_tts
try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, GRAY, PASTEL_BLUE, PASTEL_GREEN
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output"
AUDIO_PATH = OUTPUT_DIR / "zero_vs_few_shot_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "zero_vs_few_shot_whiteboard.mp4"

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Zero-shot versus Few-shot learning. What is the difference? "
    "<bookmark mark='zero_shot'/> In zero-shot learning, you ask the AI to perform a task without giving it any examples. "
    "You simply provide the instruction, like 'Translate Apple to Spanish', and the model uses its base knowledge to answer. "
    "<bookmark mark='few_shot'/> In few-shot learning, you give the AI a few examples first to show it exactly the pattern you want. "
    "You might show 'Dog becomes Perro', and 'Cat becomes Gato'. Then you ask for 'Apple'. "
    "Seeing the pattern, the model provides a highly accurate, properly formatted response. "
    "<bookmark mark='summary'/> To summarize: Zero-shot uses zero examples and relies purely on general knowledge. "
    "Few-shot uses a small set of examples to perfectly steer the model towards your specific goal. "
    "<bookmark mark='outro'/> Thanks for watching!"
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
        stroke_style=StrokeStyle(color=color, width=3.0),
        sketch_style=SKETCH,
        align=align,
    )


def make_bullet_list(
    lines: list[str],
    *,
    y_start: float,
    x: float = 300,
    color: tuple[float, float, float] = BLACK,
    y_step: float = 85,
    font_size: float = 50,
) -> list[Text]:
    return[
        Text(
            f"• {line}",
            position=(x, y_start + i * y_step),
            font_size=font_size,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=color, width=3.0),
            sketch_style=SKETCH,
            align="left",
        )
        for i, line in enumerate(lines)
    ]


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()


def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.2) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)


def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        intro_start = tracker.bookmark_time("intro")
        zero_shot_start = tracker.bookmark_time("zero_shot")
        few_shot_start = tracker.bookmark_time("few_shot")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Zero-Shot vs Few-Shot Learning", y=450, color=BLUE)
        intro_sub = make_body("How do we instruct AI models?", y=600, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.0, duration=1.5), drawable=intro_sub)

        intro_drawables = [intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Zero-Shot
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=zero_shot_start - 1.0)
        zero_drawables =[]

        zs_title = make_title("Zero-Shot Learning", y=150, color=RED)
        zs_sub = make_body("Providing the instruction with 0 examples.", y=260, color=GRAY, font_size=48)

        # Prompt Box
        prompt_box_z = Rectangle(top_left=(250, 400), width=600, height=250, stroke_style=StrokeStyle(color=BLACK, width=3.0), fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        p_label_z = make_body("PROMPT", x=550, y=360, font_size=42, color=BLUE)
        p_text_z = make_body("Translate to Spanish:\n'Apple'", x=550, y=525, font_size=56, align="center")

        arrow_z = Arrow(start_point=(880, 525), end_point=(1180, 525), stroke_style=StrokeStyle(color=BLACK, width=4.0))

        # Output Box
        out_box_z = Rectangle(top_left=(1220, 400), width=450, height=250, stroke_style=StrokeStyle(color=BLACK, width=3.0), fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        o_label_z = make_body("MODEL OUTPUT", x=1445, y=360, font_size=42, color=GREEN)
        o_text_z = make_body("Manzana", x=1445, y=525, font_size=64, color=GREEN)

        zs_highlight = make_body("Relies completely on pre-trained knowledge", y=800, color=ORANGE, font_size=56)

        scene.add(SketchAnimation(start_time=zero_shot_start + 0.5, duration=1.0), drawable=zs_title)
        scene.add(SketchAnimation(start_time=zero_shot_start + 1.5, duration=1.0), drawable=zs_sub)
        
        scene.add(SketchAnimation(start_time=zero_shot_start + 3.0, duration=1.0), drawable=prompt_box_z)
        scene.add(SketchAnimation(start_time=zero_shot_start + 3.5, duration=0.5), drawable=p_label_z)
        scene.add(SketchAnimation(start_time=zero_shot_start + 4.0, duration=1.0), drawable=p_text_z)
        
        scene.add(SketchAnimation(start_time=zero_shot_start + 6.0, duration=0.8), drawable=arrow_z)
        
        scene.add(SketchAnimation(start_time=zero_shot_start + 7.0, duration=1.0), drawable=out_box_z)
        scene.add(SketchAnimation(start_time=zero_shot_start + 7.5, duration=0.5), drawable=o_label_z)
        scene.add(SketchAnimation(start_time=zero_shot_start + 8.0, duration=1.0), drawable=o_text_z)

        scene.add(SketchAnimation(start_time=zero_shot_start + 9.5, duration=1.5), drawable=zs_highlight)

        zero_drawables.extend([zs_title, zs_sub, prompt_box_z, p_label_z, p_text_z, arrow_z, out_box_z, o_label_z, o_text_z, zs_highlight])

        # ---------------------------------------------------------
        # SECTION 3: Few-Shot
        # ---------------------------------------------------------
        make_eraser(zero_drawables, start_time=few_shot_start - 1.0)
        few_drawables =[]

        fs_title = make_title("Few-Shot Learning", y=150, color=GREEN)
        fs_sub = make_body("Providing the instruction WITH a few examples.", y=260, color=GRAY, font_size=48)

        # Bigger Prompt Box for examples
        prompt_box_f = Rectangle(top_left=(200, 380), width=650, height=400, stroke_style=StrokeStyle(color=BLACK, width=3.0), fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        p_label_f = make_body("PROMPT", x=525, y=340, font_size=42, color=BLUE)
        
        p_text_f1 = make_body("Dog -> Perro", x=525, y=450, font_size=50)
        p_text_f2 = make_body("Cat -> Gato", x=525, y=550, font_size=50)
        p_text_f3 = make_body("Apple -> ?", x=525, y=680, font_size=56, color=RED)

        arrow_f = Arrow(start_point=(880, 580), end_point=(1180, 580), stroke_style=StrokeStyle(color=BLACK, width=4.0))

        # Output Box
        out_box_f = Rectangle(top_left=(1220, 480), width=450, height=200, stroke_style=StrokeStyle(color=BLACK, width=3.0), fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        o_label_f = make_body("MODEL OUTPUT", x=1445, y=440, font_size=42, color=GREEN)
        o_text_f = make_body("Manzana", x=1445, y=580, font_size=64, color=GREEN)

        fs_highlight = make_body("Steers the model using pattern recognition", y=880, color=ORANGE, font_size=56)

        scene.add(SketchAnimation(start_time=few_shot_start + 0.5, duration=1.0), drawable=fs_title)
        scene.add(SketchAnimation(start_time=few_shot_start + 1.5, duration=1.0), drawable=fs_sub)

        scene.add(SketchAnimation(start_time=few_shot_start + 2.5, duration=1.0), drawable=prompt_box_f)
        scene.add(SketchAnimation(start_time=few_shot_start + 3.0, duration=0.5), drawable=p_label_f)
        
        scene.add(SketchAnimation(start_time=few_shot_start + 4.0, duration=0.8), drawable=p_text_f1)
        scene.add(SketchAnimation(start_time=few_shot_start + 5.0, duration=0.8), drawable=p_text_f2)
        scene.add(SketchAnimation(start_time=few_shot_start + 6.5, duration=1.0), drawable=p_text_f3)

        scene.add(SketchAnimation(start_time=few_shot_start + 8.0, duration=0.8), drawable=arrow_f)

        scene.add(SketchAnimation(start_time=few_shot_start + 9.0, duration=1.0), drawable=out_box_f)
        scene.add(SketchAnimation(start_time=few_shot_start + 9.5, duration=0.5), drawable=o_label_f)
        scene.add(SketchAnimation(start_time=few_shot_start + 10.0, duration=1.0), drawable=o_text_f)

        scene.add(SketchAnimation(start_time=few_shot_start + 11.5, duration=1.5), drawable=fs_highlight)

        few_drawables.extend([fs_title, fs_sub, prompt_box_f, p_label_f, p_text_f1, p_text_f2, p_text_f3, arrow_f, out_box_f, o_label_f, o_text_f, fs_highlight])

        # ---------------------------------------------------------
        # SECTION 4: Summary
        # ---------------------------------------------------------
        make_eraser(few_drawables, start_time=summary_start - 1.0)
        sum_drawables =[]

        sum_title = make_title("Summary", y=150, color=BLUE)
        mid_line = Line(start=(960, 280), end=(960, 850), stroke_style=StrokeStyle(color=GRAY, width=4.0), sketch_style=SKETCH)

        sum_zs_title = make_body("ZERO-SHOT", x=480, y=320, font_size=72, color=RED)
        zs_bullets = make_bullet_list([
            "0 Examples provided",
            "Relies on base training",
            "Fast & easy to write"
        ], y_start=480, x=150, font_size=46)

        sum_fs_title = make_body("FEW-SHOT", x=1440, y=320, font_size=72, color=GREEN)
        fs_bullets = make_bullet_list([
            "1 to N Examples provided",
            "Establishes a strict pattern",
            "Highly accurate & guided"
        ], y_start=480, x=1120, font_size=46)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 1.5, duration=0.5), drawable=mid_line)
        
        scene.add(SketchAnimation(start_time=summary_start + 2.0, duration=1.0), drawable=sum_zs_title)
        for i, b in enumerate(zs_bullets):
            scene.add(SketchAnimation(start_time=summary_start + 3.0 + (i * 0.5), duration=0.8), drawable=b)

        scene.add(SketchAnimation(start_time=summary_start + 5.5, duration=1.0), drawable=sum_fs_title)
        for i, b in enumerate(fs_bullets):
            scene.add(SketchAnimation(start_time=summary_start + 6.5 + (i * 0.5), duration=0.8), drawable=b)

        sum_drawables.extend([sum_title, mid_line, sum_zs_title, sum_fs_title] + zs_bullets + fs_bullets)

        # ---------------------------------------------------------
        # SECTION 5: Outro
        # ---------------------------------------------------------
        make_eraser(sum_drawables, start_time=outro_start - 1.0)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("Now you know how to prompt like a pro.", y=600, color=BLACK)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.5), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 2.5, duration=1.5), drawable=outro_body)

        return tracker.end_time + 1.5


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