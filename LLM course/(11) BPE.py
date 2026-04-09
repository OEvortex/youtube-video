"""
Whiteboard explainer: Byte Pair Encoding (BPE) Deep Dive

This scene provides a detailed ~2.5 minute animation on BPE.
It covers the 1994 history, a visual data compression example, 
its modern adaptation for LLMs (solving OOV), and a practical step-by-step
merge iteration example.
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
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "tokenizer"
AUDIO_PATH = OUTPUT_DIR / "bpe_deep_dive_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "bpe_deep_dive_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome back! Today, we are taking a deep dive into Byte Pair Encoding, or BPE. "
    "It is the core tokenization algorithm that powers modern Large Language Models like GPT-4, Claude, and LLaMA. "
    "But what is it, and how does it actually work? "
    
    "<bookmark mark='history'/> Let's start with a bit of history. Did you know BPE was not originally invented for Artificial Intelligence? "
    "It was created in 1994 by a programmer named Philip Gage as a general data compression technique. "
    "The original goal was simply to shrink the size of text files to save disk space and memory. "
    
    "<bookmark mark='compression'/> How did it compress data? Let's look at a visual example. "
    "Imagine a simple text string: A, B, A, B, C, A, B, A, B. "
    "The algorithm scans the string and looks for the most frequent pair of adjacent characters. "
    "Here, the pair 'A B' appears four times. BPE creates a new rule: replace all 'A B' pairs with a new, unused symbol, like 'X'. "
    "Our nine-character string instantly shrinks to: X, X, C, X, X. "
    
    "<bookmark mark='comp_step2'/> But BPE doesn't stop there. It loops again. "
    "Now, it sees the pair 'X X' appears twice. It makes a new rule: replace 'X X' with 'Y'. "
    "Our string becomes: Y, C, Y. Through these iterations, we compressed nine characters down to just three! "
    
    "<bookmark mark='llm_transition'/> So, how did a 1994 compression algorithm become the heart of modern AI? "
    "Fast forward to 2015. AI researchers realized that human language has highly repetitive patterns. "
    "Prefixes like 'un', or suffixes like 'ing' and 'est', appear constantly. "
    "By using BPE, AI could compress letters into meaningful subwords. "
    
    "<bookmark mark='oov_problem'/> This solved a massive issue called the 'Out of Vocabulary' problem. "
    "Before BPE, if an AI saw a rare or made-up word, it would crash or output an 'unknown' error. "
    "With BPE, if it sees a new word like 'lowest', it doesn't panic. It just breaks it down into known subwords, like 'low' and 'est'. "
    
    "<bookmark mark='practical_example'/> Let's walk through a practical example of how BPE trains its vocabulary for an LLM. "
    "We start with a base vocabulary of individual characters: l, o, w, e, r, s, t. "
    "The algorithm scans our dataset and counts pairs. "
    
    "<bookmark mark='iteration1'/> It finds that 'e' and 'r' appear together very frequently. "
    "It merges them, adding the new subword 'er' to our vocabulary. "
    
    "<bookmark mark='iteration2'/> On the next loop, it finds 'e' and 's', creating the token 'es'. "
    
    "<bookmark mark='iteration3'/> On the next loop, it merges 'es' and 't' to create the suffix 'est'. "
    "Iteration by iteration, BPE builds a highly efficient dictionary of subwords, finding the perfect balance between individual characters and whole words. "
    
    "<bookmark mark='outro'/> And that is exactly how Byte Pair Encoding teaches your AI to read. Thanks for watching!"
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
        history_start = tracker.bookmark_time("history")
        compression_start = tracker.bookmark_time("compression")
        comp_step2_start = tracker.bookmark_time("comp_step2")
        llm_trans_start = tracker.bookmark_time("llm_transition")
        oov_start = tracker.bookmark_time("oov_problem")
        prac_start = tracker.bookmark_time("practical_example")
        iter1_start = tracker.bookmark_time("iteration1")
        iter2_start = tracker.bookmark_time("iteration2")
        iter3_start = tracker.bookmark_time("iteration3")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro & History
        # ---------------------------------------------------------
        intro_title = make_title("Byte Pair Encoding (BPE)", y=150, color=BLUE)
        intro_sub = make_body("The Tokenizer behind GPT, Claude, and LLaMA", y=250, color=ORANGE, font_size=56)
        
        hist_title = make_body("A Brief History", x=960, y=400, color=BLACK, font_size=72)
        
        paper_box = FlowchartProcess("Invented in 1994\nby Philip Gage", top_left=(300, 500), width=500, height=180, font_size=56, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=box_stroke)
        arr_hist = Arrow(start_point=(800, 590), end_point=(1050, 590), stroke_style=box_stroke)
        comp_box = FlowchartProcess("Data Compression\nTechnique", top_left=(1050, 500), width=500, height=180, font_size=56, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)
        
        hist_note = make_body("Goal: Shrink text files to save disk space.", y=800, color=DARK_GRAY, font_size=56)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.0, duration=1.5), drawable=intro_sub)
        
        scene.add(SketchAnimation(start_time=history_start + 0.5, duration=1.0), drawable=hist_title)
        scene.add(SketchAnimation(start_time=history_start + 4.0, duration=1.5), drawable=paper_box)
        scene.add(SketchAnimation(start_time=history_start + 6.0, duration=0.8), drawable=arr_hist)
        scene.add(SketchAnimation(start_time=history_start + 7.5, duration=1.5), drawable=comp_box)
        scene.add(SketchAnimation(start_time=history_start + 11.0, duration=1.5), drawable=hist_note)

        hist_drawables =[intro_title, intro_sub, hist_title, paper_box, arr_hist, comp_box, hist_note]

        # ---------------------------------------------------------
        # SECTION 2: Compression Visual Example
        # ---------------------------------------------------------
        make_eraser(hist_drawables, start_time=compression_start - 1.2)
        comp_drawables =[]

        comp_title = make_title("How BPE Compresses Data", y=150, color=GREEN)

        # Original String
        str1_label = make_body("Original (9 chars):", x=400, y=350, font_size=48, color=BLACK)
        str1_text = make_body("A B A B C A B A B", x=1050, y=350, font_size=72, color=DARK_GRAY, align="left")
        
        # Step 1
        rule1_text = make_body("Rule 1: Replace 'A B' ➔ 'X'", x=1050, y=480, font_size=48, color=BLUE, align="left")
        arr_step1 = Arrow(start_point=(600, 380), end_point=(600, 580), stroke_style=StrokeStyle(color=BLUE, width=4.0))
        
        str2_label = make_body("Step 1 (5 chars):", x=400, y=600, font_size=48, color=BLACK)
        str2_text = make_body("X X C X X", x=1050, y=600, font_size=72, color=BLUE, align="left")

        # Step 2
        rule2_text = make_body("Rule 2: Replace 'X X' ➔ 'Y'", x=1050, y=730, font_size=48, color=RED, align="left")
        arr_step2 = Arrow(start_point=(600, 630), end_point=(600, 830), stroke_style=StrokeStyle(color=RED, width=4.0))
        
        str3_label = make_body("Step 2 (3 chars):", x=400, y=850, font_size=48, color=BLACK)
        str3_text = make_body("Y C Y", x=1050, y=850, font_size=72, color=RED, align="left")

        scene.add(SketchAnimation(start_time=compression_start + 0.5, duration=1.0), drawable=comp_title)
        
        scene.add(SketchAnimation(start_time=compression_start + 3.0, duration=1.0), drawable=str1_label)
        scene.add(SketchAnimation(start_time=compression_start + 4.0, duration=1.5), drawable=str1_text)
        
        scene.add(SketchAnimation(start_time=compression_start + 11.5, duration=1.5), drawable=rule1_text)
        scene.add(SketchAnimation(start_time=compression_start + 13.5, duration=0.8), drawable=arr_step1)
        scene.add(SketchAnimation(start_time=compression_start + 14.5, duration=1.0), drawable=str2_label)
        scene.add(SketchAnimation(start_time=compression_start + 15.0, duration=1.5), drawable=str2_text)

        scene.add(SketchAnimation(start_time=comp_step2_start + 1.0, duration=1.5), drawable=rule2_text)
        scene.add(SketchAnimation(start_time=comp_step2_start + 3.0, duration=0.8), drawable=arr_step2)
        scene.add(SketchAnimation(start_time=comp_step2_start + 4.0, duration=1.0), drawable=str3_label)
        scene.add(SketchAnimation(start_time=comp_step2_start + 4.5, duration=1.5), drawable=str3_text)

        comp_drawables.extend([comp_title, str1_label, str1_text, rule1_text, arr_step1, str2_label, str2_text, rule2_text, arr_step2, str3_label, str3_text])

        # ---------------------------------------------------------
        # SECTION 3: BPE for LLMs & OOV Problem
        # ---------------------------------------------------------
        make_eraser(comp_drawables, start_time=llm_trans_start - 1.2)
        llm_drawables =[]

        llm_title = make_title("From Compression to AI (2015)", y=150, color=ORANGE)
        
        llm_bullets = make_bullet_list([
            "Language has highly repetitive patterns",
            "Prefixes: 'un-', 're-'",
            "Suffixes: '-ing', '-est', '-ably'"
        ], y_start=300, x=450, font_size=56)

        # OOV Problem Visual
        oov_box = FlowchartProcess("The 'Out of Vocabulary' Problem", top_left=(460, 600), width=1000, height=350, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.2), stroke_style=box_stroke)
        
        old_way = make_body("Before BPE: 'lowest' ➔ ERROR (Unknown Word)", x=960, y=700, color=RED, font_size=48)
        new_way = make_body("With BPE: 'lowest' ➔ [ 'low', 'est' ]", x=960, y=850, color=GREEN, font_size=56)

        scene.add(SketchAnimation(start_time=llm_trans_start + 0.5, duration=1.0), drawable=llm_title)
        
        for i, b in enumerate(llm_bullets):
            scene.add(SketchAnimation(start_time=llm_trans_start + 4.0 + (i * 2.0), duration=1.5), drawable=b)

        scene.add(SketchAnimation(start_time=oov_start + 0.5, duration=1.5), drawable=oov_box)
        scene.add(SketchAnimation(start_time=oov_start + 2.5, duration=1.5), drawable=old_way)
        scene.add(SketchAnimation(start_time=oov_start + 8.5, duration=1.5), drawable=new_way)

        llm_drawables.extend([llm_title, oov_box, old_way, new_way] + llm_bullets)

        # ---------------------------------------------------------
        # SECTION 4: Practical Example (Iteration by Iteration)
        # ---------------------------------------------------------
        make_eraser(llm_drawables, start_time=prac_start - 1.2)
        prac_drawables =[]

        prac_title = make_title("BPE Training: A Practical Example", y=120, color=BLUE)

        # Base Vocab Box (Top)
        vocab_box = Rectangle(top_left=(200, 250), width=1520, height=120, stroke_style=box_stroke, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.2, hachure_gap=10), sketch_style=SKETCH)
        vocab_label = make_body("Vocabulary:", x=350, y=310, font_size=48, color=BLUE)
        v_base = make_body("'l', 'o', 'w', 'e', 'r', 's', 't'", x=800, y=310, font_size=56, color=BLACK)
        
        # Dataset
        data_label = make_body("Training Data: 'lower', 'lowest'", x=960, y=450, font_size=56, color=DARK_GRAY)

        # Iterations
        # Iteration 1
        it1_box = FlowchartProcess("Loop 1:\n'e' + 'r'", top_left=(300, 550), width=300, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)
        arr_it1 = Arrow(start_point=(600, 625), end_point=(700, 625), stroke_style=box_stroke)
        it1_result = make_body("New Token: 'er'", x=880, y=625, font_size=48, color=GREEN)
        v_add1 = make_body(", 'er'", x=1220, y=310, font_size=56, color=GREEN)

        # Iteration 2
        it2_box = FlowchartProcess("Loop 2:\n'e' + 's'", top_left=(300, 750), width=300, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=box_stroke)
        arr_it2 = Arrow(start_point=(600, 825), end_point=(700, 825), stroke_style=box_stroke)
        it2_result = make_body("New Token: 'es'", x=880, y=825, font_size=48, color=ORANGE)
        v_add2 = make_body(", 'es'", x=1350, y=310, font_size=56, color=ORANGE)

        # Iteration 3
        it3_box = FlowchartProcess("Loop 3:\n'es' + 't'", top_left=(1150, 650), width=300, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=box_stroke)
        arr_it3 = Arrow(start_point=(1450, 725), end_point=(1550, 725), stroke_style=box_stroke)
        it3_result = make_body("New Token: 'est'", x=1730, y=725, font_size=48, color=PURPLE)
        v_add3 = make_body(", 'est'", x=1500, y=310, font_size=56, color=PURPLE)

        scene.add(SketchAnimation(start_time=prac_start + 0.5, duration=1.0), drawable=prac_title)
        scene.add(SketchAnimation(start_time=prac_start + 3.0, duration=1.0), drawable=vocab_box)
        scene.add(SketchAnimation(start_time=prac_start + 3.5, duration=0.8), drawable=vocab_label)
        scene.add(SketchAnimation(start_time=prac_start + 4.0, duration=1.5), drawable=v_base)
        scene.add(SketchAnimation(start_time=prac_start + 6.0, duration=1.5), drawable=data_label)

        scene.add(SketchAnimation(start_time=iter1_start + 0.5, duration=1.0), drawable=it1_box)
        scene.add(SketchAnimation(start_time=iter1_start + 2.0, duration=0.5), drawable=arr_it1)
        scene.add(SketchAnimation(start_time=iter1_start + 2.5, duration=1.0), drawable=it1_result)
        scene.add(SketchAnimation(start_time=iter1_start + 4.0, duration=1.0), drawable=v_add1)

        scene.add(SketchAnimation(start_time=iter2_start + 0.5, duration=1.0), drawable=it2_box)
        scene.add(SketchAnimation(start_time=iter2_start + 1.5, duration=0.5), drawable=arr_it2)
        scene.add(SketchAnimation(start_time=iter2_start + 2.0, duration=1.0), drawable=it2_result)
        scene.add(SketchAnimation(start_time=iter2_start + 3.0, duration=1.0), drawable=v_add2)

        scene.add(SketchAnimation(start_time=iter3_start + 0.5, duration=1.0), drawable=it3_box)
        scene.add(SketchAnimation(start_time=iter3_start + 1.5, duration=0.5), drawable=arr_it3)
        scene.add(SketchAnimation(start_time=iter3_start + 2.0, duration=1.0), drawable=it3_result)
        scene.add(SketchAnimation(start_time=iter3_start + 3.0, duration=1.0), drawable=v_add3)

        prac_drawables.extend([
            prac_title, vocab_box, vocab_label, v_base, data_label,
            it1_box, arr_it1, it1_result, v_add1,
            it2_box, arr_it2, it2_result, v_add2,
            it3_box, arr_it3, it3_result, v_add3
        ])

        # ---------------------------------------------------------
        # SECTION 5: Outro
        # ---------------------------------------------------------
        make_eraser(prac_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now know how AI learns its vocabulary.", y=600, color=BLACK)

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