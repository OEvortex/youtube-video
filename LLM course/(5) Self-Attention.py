"""
Whiteboard explainer: Autoregressive & Self-Attention Mechanisms

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It heavily details "Autoregressive Generation" and the "Self-Attention (QKV) Mechanism"
using clear, non-overlapping visual metaphors and diagrams.
"""

from __future__ import annotations

import asyncio
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
from handanim.primitives import Arrow, CurvedArrow, FlowchartProcess, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_YELLOW, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = ROOT / "output"
AUDIO_PATH = OUTPUT_DIR / "ar_and_attention_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "ar_and_attention_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> You asked about two of the most critical concepts in modern AI: "
    "Autoregressive generation, and the Self-Attention mechanism. "
    "Let's break down exactly what these terms mean visually. "
    
    "<bookmark mark='ar_def'/> First, what does 'Autoregressive' mean? "
    "In statistics and AI, 'Auto' means self, and 'Regressive' means predicting the next step. "
    "So, an autoregressive model predicts the next word in a sequence based on its own past outputs. "
    
    "<bookmark mark='ar_visual'/> Imagine a model generating a sentence. "
    "It starts with a prompt, and predicts the word 'The'. "
    "Then, it takes that output, loops it back as the new input, and predicts 'cat'. "
    "It repeats this loop: taking the past to generate the future, one single word at a time. "
    "It is strictly a one-way street. This is how ChatGPT writes its answers! "
    
    "<bookmark mark='sa_def'/> Now, what is the 'Self-Attention Mechanism'? "
    "If Autoregressive is how the model writes, Self-Attention is how the model thinks. "
    "It is how the model understands the context and relationships between words in a sequence. "
    
    "<bookmark mark='sa_visual'/> Take these two sentences: 'The bank of the river' and 'The bank on the corner'. "
    "How does the model know that 'bank' means land in the first, and a building in the second? "
    "By paying attention to the surrounding words! "
    "The word 'river' dynamically alters the mathematical meaning of the word 'bank'. "
    
    "<bookmark mark='sa_qkv'/> It does this using three mathematical matrices: Query, Key, and Value. "
    "Think of the Query as a word asking, 'What context do I need to understand myself?' "
    "The Key is other words saying, 'Here is the context I contain.' "
    "When a Query and Key match, the model transfers the actual meaning—the Value—between the words. "
    
    "<bookmark mark='summary'/> To summarize: "
    "Autoregressive generation is the step-by-step writing process. "
    "Self-Attention is the interconnected web of context that makes the writing make sense. "
    
    "<bookmark mark='outro'/> Together, they are the secret recipe behind modern language models. "
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
        ar_def_start = tracker.bookmark_time("ar_def")
        ar_vis_start = tracker.bookmark_time("ar_visual")
        sa_def_start = tracker.bookmark_time("sa_def")
        sa_vis_start = tracker.bookmark_time("sa_visual")
        sa_qkv_start = tracker.bookmark_time("sa_qkv")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Autoregressive & Self-Attention", y=300, color=BLUE)
        intro_sub = make_body("The two pillars of Large Language Models", y=450, color=BLACK, font_size=64)
        intro_note = make_body("How AI writes, and how AI thinks.", y=650, color=ORANGE)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        scene.add(SketchAnimation(start_time=intro_start + 4.5, duration=1.5), drawable=intro_note)

        intro_drawables =[intro_title, intro_sub, intro_note]

        # ---------------------------------------------------------
        # SECTION 2: Autoregressive (Definition & Visual)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=ar_def_start - 1.5)

        ar_drawables =[]

        ar_title = make_title("What is 'Autoregressive'?", y=140, color=GREEN)
        ar_sub = make_body("Auto = Self   |   Regressive = Predicting the next step", y=260, color=ORANGE, font_size=56)
        
        # Core mechanics visual
        llm_box = FlowchartProcess("LLM Engine\n(Decoder)", top_left=(760, 450), width=400, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        
        # Base setup
        in_label = make_body("INPUT", x=400, y=420, font_size=42, color=BLUE)
        out_label = make_body("OUTPUT", x=1520, y=420, font_size=42, color=BLUE)
        arr_in = Arrow(start_point=(550, 550), end_point=(740, 550), stroke_style=box_stroke)
        arr_out = Arrow(start_point=(1180, 550), end_point=(1370, 550), stroke_style=box_stroke)

        # Loop Arrow (Output -> Input)
        loop_arrow = CurvedArrow(points=[(1400, 600), (960, 850), (500, 600)], stroke_style=StrokeStyle(color=ORANGE, width=4.0))
        loop_text = make_body("Past output becomes new input", x=960, y=880, color=ORANGE, font_size=42)

        # Sequences
        seq_in_1 = make_body("[Start]", x=400, y=550, font_size=48)
        seq_out_1 = make_body("'The'", x=1520, y=550, font_size=48, color=RED)
        
        seq_in_2 = make_body("'The'", x=400, y=650, font_size=48)
        seq_out_2 = make_body("'cat'", x=1520, y=650, font_size=48, color=RED)

        seq_in_3 = make_body("'The cat'", x=400, y=750, font_size=48)
        seq_out_3 = make_body("'sat'", x=1520, y=750, font_size=48, color=RED)

        # Animation sequence
        scene.add(SketchAnimation(start_time=ar_def_start + 0.5, duration=1.5), drawable=ar_title)
        scene.add(SketchAnimation(start_time=ar_def_start + 2.5, duration=1.5), drawable=ar_sub)
        
        # Build base visual
        scene.add(SketchAnimation(start_time=ar_vis_start + 0.5, duration=1.0), drawable=llm_box)
        scene.add(SketchAnimation(start_time=ar_vis_start + 1.0, duration=0.8), drawable=in_label)
        scene.add(SketchAnimation(start_time=ar_vis_start + 1.0, duration=0.8), drawable=out_label)
        scene.add(SketchAnimation(start_time=ar_vis_start + 1.5, duration=0.5), drawable=arr_in)
        scene.add(SketchAnimation(start_time=ar_vis_start + 1.5, duration=0.5), drawable=arr_out)

        # Step 1
        scene.add(SketchAnimation(start_time=ar_vis_start + 2.5, duration=0.5), drawable=seq_in_1)
        scene.add(SketchAnimation(start_time=ar_vis_start + 4.0, duration=0.5), drawable=seq_out_1)
        
        # Loop Draw
        scene.add(SketchAnimation(start_time=ar_vis_start + 5.0, duration=1.0), drawable=loop_arrow)
        scene.add(SketchAnimation(start_time=ar_vis_start + 5.5, duration=1.0), drawable=loop_text)

        # Step 2
        scene.add(SketchAnimation(start_time=ar_vis_start + 7.5, duration=0.5), drawable=seq_in_2)
        scene.add(SketchAnimation(start_time=ar_vis_start + 9.5, duration=0.5), drawable=seq_out_2)

        # Step 3
        scene.add(SketchAnimation(start_time=ar_vis_start + 11.5, duration=0.5), drawable=seq_in_3)
        scene.add(SketchAnimation(start_time=ar_vis_start + 13.5, duration=0.5), drawable=seq_out_3)

        ar_drawables.extend([ar_title, ar_sub, llm_box, in_label, out_label, arr_in, arr_out, loop_arrow, loop_text, seq_in_1, seq_out_1, seq_in_2, seq_out_2, seq_in_3, seq_out_3])

        # ---------------------------------------------------------
        # SECTION 3: Self-Attention (Definition & Visual)
        # ---------------------------------------------------------
        make_eraser(ar_drawables, start_time=sa_def_start - 1.5)

        sa_drawables =[]

        sa_title = make_title("Self-Attention Mechanism", y=140, color=BLUE)
        sa_sub = make_body("How words build contextual relationships", y=260, color=BLACK, font_size=56)
        
        # Visual sentences
        sent1_word1 = make_body("The", x=500, y=450, font_size=72)
        sent1_word2 = make_body("bank", x=700, y=450, font_size=72, color=GREEN)
        sent1_word3 = make_body("of", x=900, y=450, font_size=72)
        sent1_word4 = make_body("the", x=1100, y=450, font_size=72)
        sent1_word5 = make_body("river", x=1300, y=450, font_size=72, color=RED)
        
        attn_arrow1 = CurvedArrow(points=[(1280, 400), (990, 320), (740, 400)], stroke_style=StrokeStyle(color=GREEN, width=5.0))
        attn_label1 = make_body("Context: Land", x=1010, y=280, font_size=42, color=GREEN)

        sent2_word1 = make_body("The", x=500, y=750, font_size=72)
        sent2_word2 = make_body("bank", x=700, y=750, font_size=72, color=ORANGE)
        sent2_word3 = make_body("on", x=900, y=750, font_size=72)
        sent2_word4 = make_body("the", x=1100, y=750, font_size=72)
        sent2_word5 = make_body("corner", x=1320, y=750, font_size=72, color=BLUE)
        
        attn_arrow2 = CurvedArrow(points=[(1300, 700), (990, 620), (740, 700)], stroke_style=StrokeStyle(color=ORANGE, width=5.0))
        attn_label2 = make_body("Context: Building", x=1010, y=580, font_size=42, color=ORANGE)

        scene.add(SketchAnimation(start_time=sa_def_start + 0.5, duration=1.5), drawable=sa_title)
        scene.add(SketchAnimation(start_time=sa_def_start + 2.5, duration=1.5), drawable=sa_sub)
        
        scene.add(SketchAnimation(start_time=sa_vis_start + 0.5, duration=1.0), drawable=sent1_word1)
        scene.add(SketchAnimation(start_time=sa_vis_start + 0.7, duration=1.0), drawable=sent1_word2)
        scene.add(SketchAnimation(start_time=sa_vis_start + 0.9, duration=1.0), drawable=sent1_word3)
        scene.add(SketchAnimation(start_time=sa_vis_start + 1.1, duration=1.0), drawable=sent1_word4)
        scene.add(SketchAnimation(start_time=sa_vis_start + 1.3, duration=1.0), drawable=sent1_word5)

        scene.add(SketchAnimation(start_time=sa_vis_start + 4.5, duration=1.0), drawable=sent2_word1)
        scene.add(SketchAnimation(start_time=sa_vis_start + 4.7, duration=1.0), drawable=sent2_word2)
        scene.add(SketchAnimation(start_time=sa_vis_start + 4.9, duration=1.0), drawable=sent2_word3)
        scene.add(SketchAnimation(start_time=sa_vis_start + 5.1, duration=1.0), drawable=sent2_word4)
        scene.add(SketchAnimation(start_time=sa_vis_start + 5.3, duration=1.0), drawable=sent2_word5)

        # Arrows appearing at the realization moment
        scene.add(SketchAnimation(start_time=sa_vis_start + 9.0, duration=1.0), drawable=attn_arrow1)
        scene.add(SketchAnimation(start_time=sa_vis_start + 9.5, duration=1.0), drawable=attn_label1)
        
        scene.add(SketchAnimation(start_time=sa_vis_start + 11.5, duration=1.0), drawable=attn_arrow2)
        scene.add(SketchAnimation(start_time=sa_vis_start + 12.0, duration=1.0), drawable=attn_label2)

        sa_drawables.extend([sa_title, sa_sub, sent1_word1, sent1_word2, sent1_word3, sent1_word4, sent1_word5, attn_arrow1, attn_label1, sent2_word1, sent2_word2, sent2_word3, sent2_word4, sent2_word5, attn_arrow2, attn_label2])

        # ---------------------------------------------------------
        # SECTION 4: Query, Key, Value (QKV)
        # ---------------------------------------------------------
        make_eraser(sa_drawables, start_time=sa_qkv_start - 1.5)

        qkv_drawables =[]

        qkv_title = make_title("Query, Key, Value (QKV)", y=140, color=BLUE)
        
        # Draw 3 distinct boxes representing Q, K, V
        fill_q = FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8)
        fill_k = FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8)
        fill_v = FillStyle(color=PASTEL_YELLOW, opacity=0.3, hachure_gap=8)

        # Query
        box_q = FlowchartProcess("Query (Q)", top_left=(200, 350), width=350, height=150, font_size=56, fill_style=fill_q, stroke_style=box_stroke)
        desc_q1 = make_body("'What context", x=375, y=550, font_size=42, color=RED)
        desc_q2 = make_body("do I need?'", x=375, y=600, font_size=42, color=RED)

        # Key
        box_k = FlowchartProcess("Key (K)", top_left=(800, 350), width=350, height=150, font_size=56, fill_style=fill_k, stroke_style=box_stroke)
        desc_k1 = make_body("'What context", x=975, y=550, font_size=42, color=GREEN)
        desc_k2 = make_body("do I contain?'", x=975, y=600, font_size=42, color=GREEN)

        # Value
        box_v = FlowchartProcess("Value (V)", top_left=(1400, 350), width=350, height=150, font_size=56, fill_style=fill_v, stroke_style=box_stroke)
        desc_v1 = make_body("'The actual meaning", x=1575, y=550, font_size=42, color=ORANGE)
        desc_v2 = make_body("passed along.'", x=1575, y=600, font_size=42, color=ORANGE)

        # Math logic lines
        match_line = Line(start=(570, 425), end=(780, 425), stroke_style=StrokeStyle(color=BLACK, width=4.0), sketch_style=SKETCH)
        match_text = make_body("Match", x=675, y=380, font_size=36)
        
        pass_arrow = Arrow(start_point=(1170, 425), end_point=(1380, 425), stroke_style=StrokeStyle(color=BLACK, width=4.0))
        pass_text = make_body("Transfer Value", x=1275, y=380, font_size=36)

        scene.add(SketchAnimation(start_time=sa_qkv_start + 0.5, duration=1.5), drawable=qkv_title)
        
        scene.add(SketchAnimation(start_time=sa_qkv_start + 3.0, duration=1.0), drawable=box_q)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 4.0, duration=0.8), drawable=desc_q1)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 4.0, duration=0.8), drawable=desc_q2)

        scene.add(SketchAnimation(start_time=sa_qkv_start + 6.0, duration=1.0), drawable=box_k)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 7.0, duration=0.8), drawable=desc_k1)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 7.0, duration=0.8), drawable=desc_k2)

        scene.add(SketchAnimation(start_time=sa_qkv_start + 9.5, duration=0.5), drawable=match_line)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 9.5, duration=0.5), drawable=match_text)

        scene.add(SketchAnimation(start_time=sa_qkv_start + 10.5, duration=1.0), drawable=box_v)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 11.5, duration=0.8), drawable=desc_v1)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 11.5, duration=0.8), drawable=desc_v2)

        scene.add(SketchAnimation(start_time=sa_qkv_start + 12.5, duration=0.5), drawable=pass_arrow)
        scene.add(SketchAnimation(start_time=sa_qkv_start + 12.5, duration=0.5), drawable=pass_text)

        qkv_drawables.extend([qkv_title, box_q, desc_q1, desc_q2, box_k, desc_k1, desc_k2, box_v, desc_v1, desc_v2, match_line, match_text, pass_arrow, pass_text])

        # ---------------------------------------------------------
        # SECTION 5: Summary & Outro
        # ---------------------------------------------------------
        make_eraser(qkv_drawables, start_time=summary_start - 1.5)

        sum_drawables =[]

        sum_title = make_title("Summary", y=140, color=BLUE)
        mid_line = Line(start=(960, 250), end=(960, 850), stroke_style=StrokeStyle(color=GRAY, width=4.0), sketch_style=SKETCH)

        # Left: Autoregressive
        sum_ar_title = make_body("AUTOREGRESSIVE", x=480, y=300, font_size=64, color=RED)
        sum_ar_bullets = make_bullet_list([
            "The Writing Process",
            "Generates step-by-step",
            "Loops outputs to inputs",
            "Unidirectional (Future blind)"
        ], y_start=450, x=150, font_size=46)

        # Right: Self-Attention
        sum_sa_title = make_body("SELF-ATTENTION", x=1440, y=300, font_size=64, color=GREEN)
        sum_sa_bullets = make_bullet_list([
            "The Thinking Process",
            "Builds context map",
            "Computes Q, K, V relationships",
            "Connects all words together"
        ], y_start=450, x=1100, font_size=46)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.5), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 1.5, duration=0.5), drawable=mid_line)
        
        scene.add(SketchAnimation(start_time=summary_start + 2.0, duration=1.0), drawable=sum_ar_title)
        for i, b in enumerate(sum_ar_bullets):
            scene.add(SketchAnimation(start_time=summary_start + 3.0 + (i * 0.5), duration=0.8), drawable=b)
            
        scene.add(SketchAnimation(start_time=summary_start + 5.5, duration=1.0), drawable=sum_sa_title)
        for i, b in enumerate(sum_sa_bullets):
            scene.add(SketchAnimation(start_time=summary_start + 6.5 + (i * 0.5), duration=0.8), drawable=b)

        sum_drawables.extend([sum_title, mid_line, sum_ar_title, sum_sa_title] + sum_ar_bullets + sum_sa_bullets)

        # Outro
        make_eraser(sum_drawables, start_time=outro_start - 1.5)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now understand the secret recipe of modern AI.", y=600, color=BLACK)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.5), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 2.5, duration=1.5), drawable=outro_body)

        return tracker.end_time + 1.5


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")


if __name__ == "__main__":
    main()