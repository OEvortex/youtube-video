"""
Whiteboard explainer: WordPiece and SentencePiece Tokenization

This scene provides a detailed animation on the two major alternatives to BPE:
WordPiece (used by BERT) and SentencePiece (used by T5 and Llama).
It covers the likelihood-based merging of WordPiece and the space-preserving,
language-agnostic approach of SentencePiece.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

# Mocking or assuming environment setup similar to user request
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, FlowchartProcess, Line, Table
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "tokenizer"
AUDIO_PATH = OUTPUT_DIR / "wordpiece_sentencepiece_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "wordpiece_sentencepiece_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> While Byte Pair Encoding is extremely popular, it's not the only way AI reads. "
    "Today, we explore WordPiece and SentencePiece—two powerful tokenization methods that handle language in very different ways. "
    
    "<bookmark mark='wordpiece_def'/> First, let's look at WordPiece. This was made famous by Google's BERT model. "
    "At first glance, it looks exactly like BPE—it merges characters into subwords. "
    "However, the internal logic is different. "
    
    "<bookmark mark='wordpiece_logic'/> While BPE merges the most frequent pair of symbols, "
    "WordPiece merges the pair that maximizes the likelihood of the training data. "
    "In simple terms, it asks: 'If I merge these two, how much better does the model understand the overall language?' "
    "It also uses a special double-hash prefix, like '##ing', to show that a token is a suffix of a larger word. "
    
    "<bookmark mark='sentencepiece_def'/> Next, we have SentencePiece. "
    "This is the modern standard for models like T5, ALBERT, and Llama. "
    "The biggest problem with BPE and WordPiece is that they assume words are always separated by spaces. "
    "But in languages like Chinese or Japanese, there are no spaces! "
    
    "<bookmark mark='sentencepiece_logic'/> SentencePiece solves this by treating the entire sentence as a raw stream of characters. "
    "It treats the whitespace itself as a special symbol—usually represented by an underscore. "
    "Because it doesn't need to 'pre-split' text by spaces, it is truly language-agnostic. "
    "It can be trained directly on raw text, making it incredibly robust for multilingual AI. "
    
    "<bookmark mark='comparison'/> To summarize our toolkit: "
    "BPE uses frequency and is the GPT standard. "
    "WordPiece uses likelihood and is the BERT standard. "
    "And SentencePiece uses raw streams with spaces as symbols, making it the multilingual champion. "
    
    "<bookmark mark='outro'/> Choosing the right tokenizer is vital for model performance. Thanks for watching!"
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
        wp_def_start = tracker.bookmark_time("wordpiece_def")
        wp_logic_start = tracker.bookmark_time("wordpiece_logic")
        sp_def_start = tracker.bookmark_time("sentencepiece_def")
        sp_logic_start = tracker.bookmark_time("sentencepiece_logic")
        comp_start = tracker.bookmark_time("comparison")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Beyond BPE: WordPiece & SentencePiece", y=350, color=BLUE)
        intro_sub = make_body("The Tokenizers of BERT, T5, and Llama", y=500, color=ORANGE, font_size=72)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)

        intro_drawables = [intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: WordPiece (BERT)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=wp_def_start - 1.2)
        wp_drawables = []

        wp_title = make_title("WordPiece (Google / BERT)", y=140, color=BLUE)
        
        # BPE vs WordPiece Logic comparison
        bpe_logic_box = FlowchartProcess("BPE Logic:\nMerge by Frequency", top_left=(250, 350), width=450, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=box_stroke)
        vs_text = make_body("vs", x=800, y=425, font_size=60)
        wp_logic_box = FlowchartProcess("WordPiece Logic:\nMerge by Likelihood", top_left=(950, 350), width=450, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)

        wp_logic_desc = make_body("How much does this pair help\nthe model understand the language?", y=650, color=DARK_GRAY, font_size=48)
        
        # Suffix example
        suffix_ex = make_body("Suffix Notation:  'playing'  ➔  ['play', '##ing']", y=850, color=ORANGE, font_size=56)

        scene.add(SketchAnimation(start_time=wp_def_start + 0.5, duration=1.0), drawable=wp_title)
        scene.add(SketchAnimation(start_time=wp_logic_start + 0.5, duration=1.2), drawable=bpe_logic_box)
        scene.add(SketchAnimation(start_time=wp_logic_start + 1.5, duration=0.5), drawable=vs_text)
        scene.add(SketchAnimation(start_time=wp_logic_start + 2.0, duration=1.2), drawable=wp_logic_box)
        
        scene.add(SketchAnimation(start_time=wp_logic_start + 5.0, duration=1.5), drawable=wp_logic_desc)
        scene.add(SketchAnimation(start_time=wp_logic_start + 11.0, duration=1.5), drawable=suffix_ex)

        wp_drawables.extend([wp_title, bpe_logic_box, vs_text, wp_logic_box, wp_logic_desc, suffix_ex])

        # ---------------------------------------------------------
        # SECTION 3: SentencePiece (T5 / Llama)
        # ---------------------------------------------------------
        make_eraser(wp_drawables, start_time=sp_def_start - 1.2)
        sp_drawables = []

        sp_title = make_title("SentencePiece (The Multilingual Standard)", y=140, color=GREEN)
        
        problem_text = make_body("Problem: Many languages don't use spaces!", y=300, color=RED, font_size=56)
        
        # Visual of space as symbol
        raw_text = make_body("Raw: 'Hello world'", x=450, y=500, font_size=60)
        arr_sp = Arrow(start_point=(700, 500), end_point=(900, 500), stroke_style=box_stroke)
        sp_text = make_body("'_Hello_world'", x=1250, y=500, font_size=72, color=GREEN)
        
        sp_note = make_body("Treats spaces as just another character ( _ )", y=650, color=ORANGE, font_size=48)
        sp_benefit = make_body("No pre-tokenization needed. Works on any language!", y=850, color=DARK_GRAY, font_size=56)

        scene.add(SketchAnimation(start_time=sp_def_start + 0.5, duration=1.0), drawable=sp_title)
        scene.add(SketchAnimation(start_time=sp_def_start + 4.0, duration=1.5), drawable=problem_text)
        
        scene.add(SketchAnimation(start_time=sp_logic_start + 0.5, duration=1.0), drawable=raw_text)
        scene.add(SketchAnimation(start_time=sp_logic_start + 1.0, duration=0.5), drawable=arr_sp)
        scene.add(SketchAnimation(start_time=sp_logic_start + 1.5, duration=1.0), drawable=sp_text)
        
        scene.add(SketchAnimation(start_time=sp_logic_start + 4.5, duration=1.2), drawable=sp_note)
        scene.add(SketchAnimation(start_time=sp_logic_start + 8.5, duration=1.5), drawable=sp_benefit)

        sp_drawables.extend([sp_title, problem_text, raw_text, arr_sp, sp_text, sp_note, sp_benefit])

        # ---------------------------------------------------------
        # SECTION 4: Comparison Table
        # ---------------------------------------------------------
        make_eraser(sp_drawables, start_time=comp_start - 1.2)
        comp_drawables = []

        comp_title = make_title("Comparison Summary", y=140, color=PURPLE)
        
        table = Table(
            top_left=(300, 300),
            data=[
                ["Method", "Decision Metric", "Space Handling", "Main Model"],
                ["BPE", "Frequency", "Pre-split by space", "GPT / Llama"],
                ["WordPiece", "Likelihood", "Pre-split by space", "BERT"],
                ["SentencePiece", "Loss / Likelihood", "Spaces as symbols", "T5 / ALBERT"]
            ],
            col_widths=[350, 350, 350, 350],
            row_heights=[100, 120, 120, 120],
            font_size=36,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=box_stroke
        )

        scene.add(SketchAnimation(start_time=comp_start + 0.5, duration=1.0), drawable=comp_title)
        scene.add(SketchAnimation(start_time=comp_start + 2.0, duration=3.5), drawable=table)

        comp_drawables.extend([comp_title, table])

        # ---------------------------------------------------------
        # SECTION 5: Outro
        # ---------------------------------------------------------
        make_eraser(comp_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("Now you know the full toolkit of AI reading.", y=600, color=BLACK)

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