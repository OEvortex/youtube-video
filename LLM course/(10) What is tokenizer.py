"""
Whiteboard explainer: What is a Tokenizer and Types of Tokenizers

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It details Word-based, Character-based, and Subword-based tokenization.
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

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, FlowchartProcess, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "tokenizer"
AUDIO_PATH = OUTPUT_DIR / "what_is_tokenizer_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "what_is_tokenizer_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> What exactly is a tokenizer, and why do AI models need them? "
    "Simply put, AI models cannot read text; they only understand numbers. "
    
    "<bookmark mark='definition'/> A tokenizer is the bridge between human language and machine math. "
    "It takes raw text and chops it into smaller pieces called tokens. "
    "Each unique token is then assigned a specific number, known as a Token ID, allowing the AI to process it. "
    
    "<bookmark mark='word_based'/> There are three main types of tokenizers. First is Word-based tokenization. "
    "This splits text by spaces. For example, 'I love AI' becomes three tokens. "
    "It is simple, but it creates a massive dictionary, and struggles when you encounter punctuation or misspelled words. "
    
    "<bookmark mark='char_based'/> Second is Character-based tokenization. "
    "This breaks text down into individual letters. "
    "While it handles misspellings easily and keeps the vocabulary small, it completely destroys the meaning of words, "
    "and creates sequences that are way too long for the AI to handle efficiently. "
    
    "<bookmark mark='subword_based'/> This brings us to the modern standard: Subword tokenization. "
    "Methods like Byte Pair Encoding, or BPE, break words into meaningful chunks. "
    "For example, a rare word like 'unbelievably' might be split into 'un', 'believe', and 'ably'. "
    
    "<bookmark mark='subword_benefits'/> Subword tokenization is the best of both worlds. "
    "It keeps the vocabulary at a reasonable size, handles rare words perfectly without errors, "
    "and preserves meaning. This is exactly what models like GPT and BERT use today. "
    
    "<bookmark mark='outro'/> Understanding tokenization is the very first step in understanding how AI processes language. "
    "Thanks for watching!"
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
        def_start = tracker.bookmark_time("definition")
        word_start = tracker.bookmark_time("word_based")
        char_start = tracker.bookmark_time("char_based")
        subword_start = tracker.bookmark_time("subword_based")
        subword_ben_start = tracker.bookmark_time("subword_benefits")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("What is a Tokenizer?", y=350, color=BLUE)
        intro_sub = make_body("AI only understands Math, not Words.", y=550, color=RED, font_size=72)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 3.0, duration=1.5), drawable=intro_sub)

        intro_drawables =[intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Definition (The Bridge)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=def_start - 1.2)
        def_drawables =[]

        def_title = make_title("The Bridge to AI", y=140, color=BLUE)
        
        # Raw Text (Human)
        raw_box = FlowchartProcess("Raw Text\n'Hello World'", top_left=(200, 400), width=350, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        arr1 = Arrow(start_point=(550, 490), end_point=(780, 490), stroke_style=box_stroke)
        
        # Tokenizer (The Chopper)
        tok_box = FlowchartProcess("Tokenizer\n(Chopping Engine)", top_left=(780, 380), width=380, height=220, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        arr2 = Arrow(start_point=(1160, 490), end_point=(1390, 490), stroke_style=box_stroke)
        
        # Numbers (Machine)
        num_box = FlowchartProcess("Token IDs\n[853, 142]", top_left=(1390, 400), width=350, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)

        def_note = make_body("Chops text into 'Tokens' and maps them to numbers.", y=800, color=ORANGE, font_size=56)

        scene.add(SketchAnimation(start_time=def_start + 0.5, duration=1.0), drawable=def_title)
        
        scene.add(SketchAnimation(start_time=def_start + 2.0, duration=1.0), drawable=raw_box)
        scene.add(SketchAnimation(start_time=def_start + 4.0, duration=0.8), drawable=tok_box)
        scene.add(SketchAnimation(start_time=def_start + 4.5, duration=0.5), drawable=arr1)
        
        scene.add(SketchAnimation(start_time=def_start + 6.0, duration=1.0), drawable=num_box)
        scene.add(SketchAnimation(start_time=def_start + 6.5, duration=0.5), drawable=arr2)
        
        scene.add(SketchAnimation(start_time=def_start + 8.5, duration=1.2), drawable=def_note)

        def_drawables.extend([def_title, raw_box, arr1, tok_box, arr2, num_box, def_note])

        # ---------------------------------------------------------
        # SECTION 3: Word-Based Tokenization
        # ---------------------------------------------------------
        make_eraser(def_drawables, start_time=word_start - 1.2)
        wb_drawables =[]

        wb_title = make_title("1. Word-Based Tokenization", y=140, color=RED)
        wb_sub = make_body("Splits text exactly by spaces.", y=260, color=DARK_GRAY, font_size=48)

        # Example visual
        wb_text = make_body("I love AI!", x=500, y=450, font_size=80)
        wb_arr = Arrow(start_point=(700, 450), end_point=(900, 450), stroke_style=box_stroke)
        wb_result = make_body("[ 'I', 'love', 'AI!' ]", x=1250, y=450, font_size=80, color=BLUE)
        
        wb_bullets = make_bullet_list([
            "Simple to understand",
            "Cons: Creates a massive dictionary (millions of words)",
            "Cons: Fails on punctuation ('AI' vs 'AI!')",
            "Cons: Fails on misspelled words"
        ], y_start=600, x=300, font_size=46)

        scene.add(SketchAnimation(start_time=word_start + 0.5, duration=1.0), drawable=wb_title)
        scene.add(SketchAnimation(start_time=word_start + 1.5, duration=1.0), drawable=wb_sub)
        
        scene.add(SketchAnimation(start_time=word_start + 2.5, duration=1.0), drawable=wb_text)
        scene.add(SketchAnimation(start_time=word_start + 3.0, duration=0.5), drawable=wb_arr)
        scene.add(SketchAnimation(start_time=word_start + 3.5, duration=1.0), drawable=wb_result)

        for i, b in enumerate(wb_bullets):
            scene.add(SketchAnimation(start_time=word_start + 5.0 + (i * 1.5), duration=1.0), drawable=b)

        wb_drawables.extend([wb_title, wb_sub, wb_text, wb_arr, wb_result] + wb_bullets)

        # ---------------------------------------------------------
        # SECTION 4: Character-Based Tokenization
        # ---------------------------------------------------------
        make_eraser(wb_drawables, start_time=char_start - 1.2)
        cb_drawables =[]

        cb_title = make_title("2. Character-Based Tokenization", y=140, color=ORANGE)
        cb_sub = make_body("Splits text into individual letters.", y=260, color=DARK_GRAY, font_size=48)

        # Example visual
        cb_text = make_body("Apple", x=500, y=450, font_size=80)
        cb_arr = Arrow(start_point=(700, 450), end_point=(900, 450), stroke_style=box_stroke)
        cb_result = make_body("[ 'A', 'p', 'p', 'l', 'e' ]", x=1250, y=450, font_size=80, color=BLUE)
        
        cb_bullets = make_bullet_list([
            "Small vocabulary (only 26 letters + symbols)",
            "Handles misspellings easily",
            "Cons: Individual letters lack meaning",
            "Cons: Sequences become way too long for AI to process"
        ], y_start=600, x=300, font_size=46)

        scene.add(SketchAnimation(start_time=char_start + 0.5, duration=1.0), drawable=cb_title)
        scene.add(SketchAnimation(start_time=char_start + 1.5, duration=1.0), drawable=cb_sub)
        
        scene.add(SketchAnimation(start_time=char_start + 2.5, duration=1.0), drawable=cb_text)
        scene.add(SketchAnimation(start_time=char_start + 3.0, duration=0.5), drawable=cb_arr)
        scene.add(SketchAnimation(start_time=char_start + 3.5, duration=1.0), drawable=cb_result)

        for i, b in enumerate(cb_bullets):
            scene.add(SketchAnimation(start_time=char_start + 5.0 + (i * 1.8), duration=1.0), drawable=b)

        cb_drawables.extend([cb_title, cb_sub, cb_text, cb_arr, cb_result] + cb_bullets)

        # ---------------------------------------------------------
        # SECTION 5: Subword-Based Tokenization
        # ---------------------------------------------------------
        make_eraser(cb_drawables, start_time=subword_start - 1.2)
        sb_drawables =[]

        sb_title = make_title("3. Subword Tokenization (BPE)", y=140, color=GREEN)
        sb_sub = make_body("The Modern Standard (Used by GPT & BERT)", y=260, color=BLUE, font_size=48)

        # Example visual
        sb_text = make_body("unbelievably", x=400, y=450, font_size=80)
        sb_arr = Arrow(start_point=(680, 450), end_point=(880, 450), stroke_style=box_stroke)
        sb_result = make_body("[ 'un', 'believe', 'ably' ]", x=1350, y=450, font_size=80, color=GREEN)
        
        sb_bullets = make_bullet_list([
            "Breaks words into meaningful chunks",
            "Keeps vocabulary at a reasonable size (~50k tokens)",
            "Handles rare or new words without errors (OOV)",
            "Preserves the semantic meaning perfectly"
        ], y_start=600, x=300, font_size=46)

        scene.add(SketchAnimation(start_time=subword_start + 0.5, duration=1.0), drawable=sb_title)
        scene.add(SketchAnimation(start_time=subword_start + 1.5, duration=1.0), drawable=sb_sub)
        
        scene.add(SketchAnimation(start_time=subword_start + 3.0, duration=1.0), drawable=sb_text)
        scene.add(SketchAnimation(start_time=subword_start + 3.5, duration=0.5), drawable=sb_arr)
        scene.add(SketchAnimation(start_time=subword_start + 4.5, duration=1.5), drawable=sb_result)

        for i, b in enumerate(sb_bullets):
            scene.add(SketchAnimation(start_time=subword_ben_start + 0.5 + (i * 1.5), duration=1.0), drawable=b)

        sb_drawables.extend([sb_title, sb_sub, sb_text, sb_arr, sb_result] + sb_bullets)

        # ---------------------------------------------------------
        # SECTION 6: Outro
        # ---------------------------------------------------------
        make_eraser(sb_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("Now you understand how AI reads text.", y=600, color=BLACK)

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