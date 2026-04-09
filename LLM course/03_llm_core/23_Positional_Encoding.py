"""
Whiteboard explainer: Positional Encoding (Sine/Cosine Waves)

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It heavily details the "lost order" problem in Transformers, the Sine/Cosine
wave mathematical solution, and the vector addition step.
"""

from __future__ import annotations

import asyncio
import math
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

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, FlowchartProcess, Line, LinearPath, Circle
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "architecture"
AUDIO_PATH = OUTPUT_DIR / "positional_encoding_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "positional_encoding_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome! Today we are exploring one of the most brilliant tricks in the Transformer architecture: Positional Encoding. "
    
    "<bookmark mark='problem'/> To understand why we need it, we must understand a flaw in Transformers. "
    "Unlike older AI models that read text sequentially word-by-word, Transformers process all words in a sentence at the exact same time. "
    "This parallel processing makes them blazing fast, but it completely destroys word order! "
    "To a basic Transformer, 'Dog bites man' and 'Man bites dog' look exactly the same, like a scrambled bag of words. "
    
    "<bookmark mark='solution'/> To fix this, researchers introduced Positional Encoding. "
    "The idea is to inject a unique mathematical signature into every word's vector, acting like a timestamp or a GPS coordinate. "
    
    "<bookmark mark='waves'/> But they didn't just use simple numbers like 1, 2, 3. Instead, they used intersecting Sine and Cosine waves of different frequencies. "
    "Imagine a set of continuous waves flowing through the sentence. "
    "By reading the exact height of the various waves at position 1, position 2, and so on, the model gets a highly unique, continuous positional vector for every single slot. "
    
    "<bookmark mark='why_waves'/> Why use sine and cosine waves? Because waves are continuous and periodic. "
    "This beautiful mathematical property allows the model to easily calculate the relative distance between any two words. "
    "It also allows the model to perfectly generalize to sentences longer than it has ever seen during training! "
    
    "<bookmark mark='addition'/> Finally, how is it applied? It is beautifully simple. "
    "The model takes the original Word Embedding vector, which contains the meaning of the word. "
    "Then, it simply adds the Positional Encoding vector, which contains the order. "
    "The resulting final vector is passed into the network, containing both rich meaning and exact position. "
    
    "<bookmark mark='outro'/> And that is how Transformers maintain word order! Thanks for watching."
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
            stroke_style=StrokeStyle(color=color, width=3.5),
            sketch_style=SKETCH,
            align="left",
        )
        for i, line in enumerate(lines)
    ]

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
        problem_start = tracker.bookmark_time("problem")
        solution_start = tracker.bookmark_time("solution")
        waves_start = tracker.bookmark_time("waves")
        why_waves_start = tracker.bookmark_time("why_waves")
        add_start = tracker.bookmark_time("addition")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Positional Encoding", y=350, color=BLUE)
        intro_sub = make_body("Sine & Cosine Waves in Transformers", y=500, color=ORANGE, font_size=72)
        intro_note = make_body("How AI maintains word order.", y=700, color=DARK_GRAY)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        scene.add(SketchAnimation(start_time=intro_start + 4.5, duration=1.5), drawable=intro_note)

        intro_drawables =[intro_title, intro_sub, intro_note]

        # ---------------------------------------------------------
        # SECTION 2: The Problem (Lost Order)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=problem_start - 1.2)
        prob_drawables =[]

        prob_title = make_title("The Flaw of Parallel Processing", y=140, color=RED)
        
        # Sentence 1
        s1_box = FlowchartProcess("'Dog bites man'", top_left=(250, 350), width=350, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=box_stroke)
        arr1 = Arrow(start_point=(600, 410), end_point=(850, 480), stroke_style=box_stroke)

        # Sentence 2
        s2_box = FlowchartProcess("'Man bites dog'", top_left=(250, 600), width=350, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=box_stroke)
        arr2 = Arrow(start_point=(600, 660), end_point=(850, 580), stroke_style=box_stroke)

        # Bag of words
        bag_box = FlowchartProcess("Bag of Words:\n[ 'bites', 'dog', 'man' ]", top_left=(850, 430), width=450, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=StrokeStyle(color=RED, width=4.0))
        
        prob_equals = make_body("They look EXACTLY the same!", x=1075, y=700, color=RED, font_size=56)

        scene.add(SketchAnimation(start_time=problem_start + 0.5, duration=1.0), drawable=prob_title)
        
        scene.add(SketchAnimation(start_time=problem_start + 6.0, duration=1.0), drawable=s1_box)
        scene.add(SketchAnimation(start_time=problem_start + 7.0, duration=1.0), drawable=s2_box)
        
        scene.add(SketchAnimation(start_time=problem_start + 10.0, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=problem_start + 10.0, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=problem_start + 11.0, duration=1.5), drawable=bag_box)
        scene.add(SketchAnimation(start_time=problem_start + 12.5, duration=1.0), drawable=prob_equals)

        prob_drawables.extend([prob_title, s1_box, arr1, s2_box, arr2, bag_box, prob_equals])

        # ---------------------------------------------------------
        # SECTION 3: The Solution & Sine/Cosine Waves
        # ---------------------------------------------------------
        make_eraser(prob_drawables, start_time=solution_start - 1.2)
        sol_drawables =[]

        sol_title = make_title("The Solution: Sine & Cosine Waves", y=140, color=BLUE)

        # Coordinate System for waves
        axis_x = Line(start=(300, 600), end=(1600, 600), stroke_style=StrokeStyle(color=BLACK, width=4.0), sketch_style=SKETCH)
        axis_y = Line(start=(300, 300), end=(300, 900), stroke_style=StrokeStyle(color=BLACK, width=4.0), sketch_style=SKETCH)

        # Generate Wave Points
        # High frequency sine
        pts_sine1 =[(x, 600 - 150 * math.sin((x - 300) * 0.02)) for x in range(300, 1600, 10)]
        # Lower frequency cosine
        pts_cos1 =[(x, 600 - 150 * math.cos((x - 300) * 0.008)) for x in range(300, 1600, 10)]
        # Even lower frequency sine
        pts_sine2 =[(x, 600 - 150 * math.sin((x - 300) * 0.003)) for x in range(300, 1600, 10)]

        wave1 = LinearPath(points=pts_sine1, stroke_style=StrokeStyle(color=RED, width=3.0), sketch_style=SKETCH)
        wave2 = LinearPath(points=pts_cos1, stroke_style=StrokeStyle(color=GREEN, width=3.0), sketch_style=SKETCH)
        wave3 = LinearPath(points=pts_sine2, stroke_style=StrokeStyle(color=ORANGE, width=3.0), sketch_style=SKETCH)

        # Position Markers
        pos1_x = 500
        pos2_x = 900
        pos3_x = 1300

        line_p1 = Line(start=(pos1_x, 350), end=(pos1_x, 850), stroke_style=StrokeStyle(color=GRAY, width=2.0), sketch_style=SKETCH)
        label_p1 = make_body("Pos 1:\n'Dog'", x=pos1_x, y=920, font_size=42, color=BLUE)
        dots_p1 =[
            Circle(center=(pos1_x, 600 - 150 * math.sin((pos1_x - 300) * 0.02)), radius=10, fill_style=FillStyle(color=RED)),
            Circle(center=(pos1_x, 600 - 150 * math.cos((pos1_x - 300) * 0.008)), radius=10, fill_style=FillStyle(color=GREEN)),
            Circle(center=(pos1_x, 600 - 150 * math.sin((pos1_x - 300) * 0.003)), radius=10, fill_style=FillStyle(color=ORANGE))
        ]

        line_p2 = Line(start=(pos2_x, 350), end=(pos2_x, 850), stroke_style=StrokeStyle(color=GRAY, width=2.0), sketch_style=SKETCH)
        label_p2 = make_body("Pos 2:\n'bites'", x=pos2_x, y=920, font_size=42, color=BLUE)
        dots_p2 =[
            Circle(center=(pos2_x, 600 - 150 * math.sin((pos2_x - 300) * 0.02)), radius=10, fill_style=FillStyle(color=RED)),
            Circle(center=(pos2_x, 600 - 150 * math.cos((pos2_x - 300) * 0.008)), radius=10, fill_style=FillStyle(color=GREEN)),
            Circle(center=(pos2_x, 600 - 150 * math.sin((pos2_x - 300) * 0.003)), radius=10, fill_style=FillStyle(color=ORANGE))
        ]

        line_p3 = Line(start=(pos3_x, 350), end=(pos3_x, 850), stroke_style=StrokeStyle(color=GRAY, width=2.0), sketch_style=SKETCH)
        label_p3 = make_body("Pos 3:\n'man'", x=pos3_x, y=920, font_size=42, color=BLUE)
        dots_p3 =[
            Circle(center=(pos3_x, 600 - 150 * math.sin((pos3_x - 300) * 0.02)), radius=10, fill_style=FillStyle(color=RED)),
            Circle(center=(pos3_x, 600 - 150 * math.cos((pos3_x - 300) * 0.008)), radius=10, fill_style=FillStyle(color=GREEN)),
            Circle(center=(pos3_x, 600 - 150 * math.sin((pos3_x - 300) * 0.003)), radius=10, fill_style=FillStyle(color=ORANGE))
        ]

        scene.add(SketchAnimation(start_time=solution_start + 0.5, duration=1.0), drawable=sol_title)
        
        scene.add(SketchAnimation(start_time=waves_start + 0.5, duration=1.0), drawable=axis_x)
        scene.add(SketchAnimation(start_time=waves_start + 0.5, duration=1.0), drawable=axis_y)
        
        scene.add(SketchAnimation(start_time=waves_start + 2.0, duration=2.0), drawable=wave1)
        scene.add(SketchAnimation(start_time=waves_start + 3.0, duration=2.0), drawable=wave2)
        scene.add(SketchAnimation(start_time=waves_start + 4.0, duration=2.0), drawable=wave3)

        # Position 1
        scene.add(SketchAnimation(start_time=waves_start + 9.0, duration=0.5), drawable=line_p1)
        scene.add(SketchAnimation(start_time=waves_start + 9.5, duration=0.5), drawable=label_p1)
        for d in dots_p1:
            scene.add(SketchAnimation(start_time=waves_start + 10.0, duration=0.2), drawable=d)

        # Position 2
        scene.add(SketchAnimation(start_time=waves_start + 11.0, duration=0.5), drawable=line_p2)
        scene.add(SketchAnimation(start_time=waves_start + 11.5, duration=0.5), drawable=label_p2)
        for d in dots_p2:
            scene.add(SketchAnimation(start_time=waves_start + 12.0, duration=0.2), drawable=d)

        # Position 3
        scene.add(SketchAnimation(start_time=waves_start + 13.0, duration=0.5), drawable=line_p3)
        scene.add(SketchAnimation(start_time=waves_start + 13.5, duration=0.5), drawable=label_p3)
        for d in dots_p3:
            scene.add(SketchAnimation(start_time=waves_start + 14.0, duration=0.2), drawable=d)

        sol_drawables.extend([sol_title, axis_x, axis_y, wave1, wave2, wave3, line_p1, label_p1, line_p2, label_p2, line_p3, label_p3] + dots_p1 + dots_p2 + dots_p3)

        # ---------------------------------------------------------
        # SECTION 4: Why Waves?
        # ---------------------------------------------------------
        make_eraser(sol_drawables, start_time=why_waves_start - 1.2)
        why_drawables =[]

        why_title = make_title("Why Sine & Cosine?", y=150, color=GREEN)
        
        why_bullets = make_bullet_list([
            "Waves are continuous and periodic.",
            "Easy to calculate relative distance between any two words.",
            "Generalizes to unseen, infinitely long sentences!"
        ], y_start=350, x=350, font_size=56)

        scene.add(SketchAnimation(start_time=why_waves_start + 0.5, duration=1.0), drawable=why_title)
        
        for i, b in enumerate(why_bullets):
            scene.add(SketchAnimation(start_time=why_waves_start + 2.5 + (i * 3.5), duration=1.5), drawable=b)

        why_drawables.extend([why_title] + why_bullets)

        # ---------------------------------------------------------
        # SECTION 5: The Vector Addition
        # ---------------------------------------------------------
        make_eraser(why_drawables, start_time=add_start - 1.2)
        add_drawables =[]

        add_title = make_title("The Beautifully Simple Math", y=150, color=PURPLE)

        # Word Embedding Block
        w_box = FlowchartProcess("Word Embedding\n(Meaning)", top_left=(200, 350), width=400, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=box_stroke)
        w_vec = make_body("[ 0.81, -0.22, 0.45 ]", x=400, y=550, color=BLUE, font_size=48)

        # Plus Sign
        plus = make_body("+", x=700, y=425, font_size=120)

        # Positional Block
        p_box = FlowchartProcess("Positional Encoding\n(Order)", top_left=(800, 350), width=400, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)
        p_vec = make_body("[ 0.05, 0.98, -0.11 ]", x=1000, y=550, color=GREEN, font_size=48)

        # Equals Sign
        equals = make_body("=", x=1300, y=425, font_size=120)

        # Final Block
        f_box = FlowchartProcess("Final Vector\n(Meaning + Order)", top_left=(1400, 350), width=400, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=box_stroke)
        f_vec = make_body("[ 0.86, 0.76, 0.34 ]", x=1600, y=550, color=PURPLE, font_size=48)

        add_desc = make_body("A single vector with all the necessary context!", y=800, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=add_start + 0.5, duration=1.0), drawable=add_title)
        
        scene.add(SketchAnimation(start_time=add_start + 3.0, duration=1.0), drawable=w_box)
        scene.add(SketchAnimation(start_time=add_start + 4.0, duration=0.8), drawable=w_vec)

        scene.add(SketchAnimation(start_time=add_start + 6.0, duration=0.5), drawable=plus)
        scene.add(SketchAnimation(start_time=add_start + 6.5, duration=1.0), drawable=p_box)
        scene.add(SketchAnimation(start_time=add_start + 7.5, duration=0.8), drawable=p_vec)

        scene.add(SketchAnimation(start_time=add_start + 9.0, duration=0.5), drawable=equals)
        scene.add(SketchAnimation(start_time=add_start + 9.5, duration=1.0), drawable=f_box)
        scene.add(SketchAnimation(start_time=add_start + 10.5, duration=0.8), drawable=f_vec)

        scene.add(SketchAnimation(start_time=add_start + 12.0, duration=1.5), drawable=add_desc)

        add_drawables.extend([add_title, w_box, w_vec, plus, p_box, p_vec, equals, f_box, f_vec, add_desc])

        # ---------------------------------------------------------
        # SECTION 6: Outro
        # ---------------------------------------------------------
        make_eraser(add_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("And that is how Transformers know word order.", y=600, color=BLACK)

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


if __name__ == "__main__":
    main()