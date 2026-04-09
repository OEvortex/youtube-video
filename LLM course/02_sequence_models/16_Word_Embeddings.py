"""
Whiteboard explainer: Word Embeddings (Word2Vec, GloVe, and Semantic Space)

This scene provides a detailed animation on how words are converted into 
high-dimensional vectors. It covers the concept of semantic space, 
vector math (King - Man + Woman = Queen), and the two legendary algorithms: 
Word2Vec and GloVe.
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
from handanim.primitives import Arrow, FlowchartProcess, Line, Circle, Table
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "embeddings"
AUDIO_PATH = OUTPUT_DIR / "word_embeddings_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "word_embeddings_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Once text is tokenized, the AI still needs to understand the meaning of those tokens. "
    "This is where Word Embeddings come in—turning words into high-dimensional numerical vectors. "
    
    "<bookmark mark='space'/> Imagine a massive mathematical space. In this 'Semantic Space', "
    "words with similar meanings are placed physically close to each other. "
    "But it's more than just location—it's about relationships. "
    "This space is famous for its vector math: if you take the vector for 'King', "
    "subtract 'Man', and add 'Woman', the resulting point is almost exactly at 'Queen'. "
    
    "<bookmark mark='word2vec'/> One of the first breakthroughs was Word2Vec, released by Google in 2013. "
    "It uses a shallow neural network to learn word meanings by predicting context. "
    "Whether using CBOW to predict a word from its neighbors, or Skip-gram to predict neighbors from a word, "
    "it learns that words appearing in similar spots must have similar meanings. "
    
    "<bookmark mark='glove'/> Then came GloVe, or Global Vectors, from Stanford. "
    "While Word2Vec looks at local windows of text, GloVe looks at the whole dataset at once. "
    "It builds a massive 'Co-occurrence Matrix' to see how often every word appears with every other word. "
    "By factorizing this matrix, it creates vectors that capture global statistical relationships across the entire library. "
    
    "<bookmark mark='summary'/> Today's Large Language Models use even more advanced versions, "
    "where vectors can have thousands of dimensions. "
    "This allows AI to understand irony, synonyms, and complex concepts as simple geometric relationships. "
    
    "<bookmark mark='outro'/> Word embeddings are the true 'soul' of AI's language understanding. Thanks for watching!"
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
        space_start = tracker.bookmark_time("space")
        w2v_start = tracker.bookmark_time("word2vec")
        glove_start = tracker.bookmark_time("glove")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Word Embeddings", y=350, color=BLUE)
        intro_sub = make_body("Turning Meanings into Math", y=500, color=ORANGE, font_size=72)
        intro_desc = make_body("How AI 'visualizes' the relationships between words.", y=650, color=DARK_GRAY)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        scene.add(SketchAnimation(start_time=intro_start + 4.5, duration=1.5), drawable=intro_desc)

        intro_drawables = [intro_title, intro_sub, intro_desc]

        # ---------------------------------------------------------
        # SECTION 2: Semantic Space & Vector Math
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=space_start - 1.2)
        space_drawables = []

        space_title = make_title("High-Dimensional Semantic Space", y=120, color=BLUE)
        
        # Draw 2D Axes
        xaxis = Line(start=(300, 750), end=(1200, 750), stroke_style=box_stroke, sketch_style=SKETCH)
        yaxis = Line(start=(300, 300), end=(300, 750), stroke_style=box_stroke, sketch_style=SKETCH)
        x_label = make_body("Gender", x=1250, y=750, font_size=32)
        y_label = make_body("Royalty", x=300, y=260, font_size=32)

        # Word Dots
        king_dot = Circle(center=(1000, 350), radius=15, fill_style=FillStyle(color=BLUE))
        king_txt = make_body("King", x=1000, y=310, font_size=42, color=BLUE)
        
        man_dot = Circle(center=(1000, 650), radius=15, fill_style=FillStyle(color=RED))
        man_txt = make_body("Man", x=1000, y=610, font_size=42, color=RED)
        
        woman_dot = Circle(center=(500, 650), radius=15, fill_style=FillStyle(color=RED))
        woman_txt = make_body("Woman", x=500, y=610, font_size=42, color=RED)

        queen_dot = Circle(center=(500, 350), radius=15, fill_style=FillStyle(color=GREEN))
        queen_txt = make_body("Queen", x=500, y=310, font_size=42, color=GREEN)

        # Vector Math Equation
        math_txt = make_body("King - Man + Woman = Queen", x=1500, y=500, font_size=56, color=ORANGE)
        
        scene.add(SketchAnimation(start_time=space_start + 0.5, duration=1.0), drawable=space_title)
        scene.add(SketchAnimation(start_time=space_start + 2.0, duration=1.0), drawable=xaxis)
        scene.add(SketchAnimation(start_time=space_start + 2.0, duration=1.0), drawable=yaxis)
        scene.add(SketchAnimation(start_time=space_start + 2.5, duration=0.5), drawable=x_label)
        scene.add(SketchAnimation(start_time=space_start + 2.5, duration=0.5), drawable=y_label)

        scene.add(SketchAnimation(start_time=space_start + 4.0, duration=0.8), drawable=king_dot)
        scene.add(SketchAnimation(start_time=space_start + 4.2, duration=0.8), drawable=king_txt)
        scene.add(SketchAnimation(start_time=space_start + 5.0, duration=0.8), drawable=man_dot)
        scene.add(SketchAnimation(start_time=space_start + 5.2, duration=0.8), drawable=man_txt)
        scene.add(SketchAnimation(start_time=space_start + 6.0, duration=0.8), drawable=woman_dot)
        scene.add(SketchAnimation(start_time=space_start + 6.2, duration=0.8), drawable=woman_txt)
        
        scene.add(SketchAnimation(start_time=space_start + 8.5, duration=1.5), drawable=math_txt)
        scene.add(SketchAnimation(start_time=space_start + 10.0, duration=0.8), drawable=queen_dot)
        scene.add(SketchAnimation(start_time=space_start + 10.2, duration=0.8), drawable=queen_txt)

        space_drawables.extend([space_title, xaxis, yaxis, x_label, y_label, king_dot, king_txt, man_dot, man_txt, woman_dot, woman_txt, queen_dot, queen_txt, math_txt])

        # ---------------------------------------------------------
        # SECTION 3: Word2Vec (Prediction)
        # ---------------------------------------------------------
        make_eraser(space_drawables, start_time=w2v_start - 1.2)
        w2v_drawables = []

        w2v_title = make_title("Word2Vec (Google, 2013)", y=140, color=GREEN)
        w2v_sub = make_body("Learning by Prediction", y=240, color=DARK_GRAY, font_size=48)

        # Neural Net Diagram
        in_layer = FlowchartProcess("Input Word", top_left=(300, 450), width=300, height=120, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=box_stroke)
        hidden_layer = FlowchartProcess("Hidden Layer\n(Embeddings)", top_left=(810, 420), width=300, height=180, font_size=42, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=box_stroke)
        out_layer = FlowchartProcess("Predicted Context", top_left=(1320, 450), width=300, height=120, font_size=42, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)

        arr_w1 = Arrow(start_point=(600, 510), end_point=(810, 510), stroke_style=box_stroke)
        arr_w2 = Arrow(start_point=(1110, 510), end_point=(1320, 510), stroke_style=box_stroke)

        w2v_note = make_body("Nearby words should have similar vectors.", y=750, color=ORANGE, font_size=52)
        w2v_variants = make_body("CBOW  vs  Skip-gram", y=880, color=DARK_GRAY, font_size=48)

        scene.add(SketchAnimation(start_time=w2v_start + 0.5, duration=1.0), drawable=w2v_title)
        scene.add(SketchAnimation(start_time=w2v_start + 1.5, duration=1.0), drawable=w2v_sub)
        
        scene.add(SketchAnimation(start_time=w2v_start + 3.5, duration=1.0), drawable=in_layer)
        scene.add(SketchAnimation(start_time=w2v_start + 4.5, duration=0.8), drawable=arr_w1)
        scene.add(SketchAnimation(start_time=w2v_start + 5.5, duration=1.2), drawable=hidden_layer)
        scene.add(SketchAnimation(start_time=w2v_start + 7.5, duration=0.8), drawable=arr_w2)
        scene.add(SketchAnimation(start_time=w2v_start + 8.5, duration=1.0), drawable=out_layer)

        scene.add(SketchAnimation(start_time=w2v_start + 11.0, duration=1.5), drawable=w2v_note)
        scene.add(SketchAnimation(start_time=w2v_start + 14.0, duration=1.2), drawable=w2v_variants)

        w2v_drawables.extend([w2v_title, w2v_sub, in_layer, hidden_layer, out_layer, arr_w1, arr_w2, w2v_note, w2v_variants])

        # ---------------------------------------------------------
        # SECTION 4: GloVe (Global Vectors)
        # ---------------------------------------------------------
        make_eraser(w2v_drawables, start_time=glove_start - 1.2)
        glove_drawables = []

        glove_title = make_title("GloVe (Stanford, 2014)", y=140, color=RED)
        glove_sub = make_body("Global Co-occurrence Statistics", y=240, color=DARK_GRAY, font_size=48)

        # Co-occurrence Matrix (Table)
        matrix = Table(
            top_left=(560, 350),
            data=[
                ["", "Ice", "Steam", "Water"],
                ["Solid", "542", "2", "310"],
                ["Gas", "1", "498", "280"]
            ],
            col_widths=[250, 250, 250, 250],
            row_heights=[100, 100, 100],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=box_stroke
        )

        glove_desc = make_body("Looks at the ENTIRE dataset to see how often words co-occur.", y=750, color=RED, font_size=52)

        scene.add(SketchAnimation(start_time=glove_start + 0.5, duration=1.0), drawable=glove_title)
        scene.add(SketchAnimation(start_time=glove_start + 1.5, duration=1.0), drawable=glove_sub)
        
        scene.add(SketchAnimation(start_time=glove_start + 4.5, duration=3.0), drawable=matrix)
        scene.add(SketchAnimation(start_time=glove_start + 10.0, duration=1.5), drawable=glove_desc)

        glove_drawables.extend([glove_title, glove_sub, matrix, glove_desc])

        # ---------------------------------------------------------
        # SECTION 5: Summary & Outro
        # ---------------------------------------------------------
        make_eraser(glove_drawables, start_time=summary_start - 1.2)
        sum_drawables = []

        sum_title = make_title("Summary", y=150, color=BLUE)
        
        comp_table = Table(
            top_left=(300, 300),
            data=[
                ["Algorithm", "Source", "Key Idea"],
                ["Word2Vec", "Google", "Local Prediction (Nearby Words)"],
                ["GloVe", "Stanford", "Global Statistics (Entire Dataset)"]
            ],
            col_widths=[400, 400, 600],
            row_heights=[120, 150, 150],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=box_stroke
        )

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 2.0, duration=3.0), drawable=comp_table)

        sum_drawables.extend([sum_title, comp_table])

        # Outro
        make_eraser(sum_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now know how AI maps the world of words.", y=600, color=BLACK)

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