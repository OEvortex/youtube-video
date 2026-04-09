"""
Whiteboard explainer: How GPT Works & GPT-3 Architecture

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It heavily details the Decoder-only architecture, autoregressive generation, 
and visualizes the massive scale of the GPT-3 model (175B params, 300B tokens).
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
from handanim.primitives import Arrow, CurvedArrow, FlowchartProcess, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output"
AUDIO_PATH = OUTPUT_DIR / "how_gpt_works_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "how_gpt_works_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Have you ever wondered how ChatGPT actually works? "
    "At its core is a model called GPT, which stands for Generative Pre-trained Transformer. "
    
    "<bookmark mark='decoder_only'/> Unlike the original Transformer that had two halves, GPT is a 'Decoder-Only' architecture. "
    "It completely drops the Encoder, relying entirely on a powerful stack of Decoder blocks. "
    "Because it only has a Decoder, it specializes entirely in generating text. "
    
    "<bookmark mark='autoregressive'/> It does this using a simple rule: predict the next word. "
    "When you give it a prompt like 'The sky is', it calculates probabilities and outputs 'blue'. "
    "Then, it takes 'blue', loops it back into the input, and predicts the next word. "
    "This loop is called Autoregressive Generation. "
    
    "<bookmark mark='gpt3_stats'/> To understand its true power, let's look at the famous GPT-3 architecture. "
    "GPT-3 isn't doing anything fundamentally different, it is just doing it at an unimaginable scale. "
    
    "<bookmark mark='params_tokens'/> It was built with a staggering 175 Billion parameters. "
    "Think of parameters as the artificial synapses or neural connections in its brain. "
    "It was trained on 300 Billion tokens, which is essentially the entire public internet, books, and articles. "
    
    "<bookmark mark='layers'/> Physically, this looks like 96 massive Decoder layers stacked on top of each other. "
    "And it uses 96 attention heads to look for context in thousands of words simultaneously. "
    
    "<bookmark mark='summary'/> So, a simple objective: predicting the next word. "
    "Combined with massive layers, parameters, and data. "
    "This perfectly forms the emergent intelligence and reasoning we see today. "
    
    "<bookmark mark='outro'/> That is how GPT works. Thanks for watching!"
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
        decoder_only_start = tracker.bookmark_time("decoder_only")
        autoregressive_start = tracker.bookmark_time("autoregressive")
        gpt3_stats_start = tracker.bookmark_time("gpt3_stats")
        params_tokens_start = tracker.bookmark_time("params_tokens")
        layers_start = tracker.bookmark_time("layers")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("How GPT Works", y=350, color=BLUE)
        intro_sub = make_body("Generative Pre-trained Transformer", y=500, color=BLACK, font_size=72)
        intro_note = make_body("The engine behind ChatGPT.", y=700, color=ORANGE)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        scene.add(SketchAnimation(start_time=intro_start + 4.5, duration=1.5), drawable=intro_note)

        intro_drawables =[intro_title, intro_sub, intro_note]

        # ---------------------------------------------------------
        # SECTION 2: Decoder Only Architecture
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=decoder_only_start - 1.5)

        dec_only_drawables =[]

        dec_title = make_title("Decoder-Only Architecture", y=140, color=RED)
        
        # Cross out Encoder
        enc_box = FlowchartProcess("Encoder", top_left=(400, 450), width=350, height=150, font_size=56, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        enc_cross = Text("X", position=(575, 525), font_size=200, font_name=FONT_NAME, stroke_style=StrokeStyle(color=RED, width=6.0))
        enc_text = make_body("Dropped entirely", x=575, y=650, font_size=42, color=RED)

        # Highlight Decoder
        dec_box = FlowchartProcess("Decoder Stack", top_left=(1100, 350), width=450, height=350, font_size=64, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        dec_text = make_body("Specializes in generation", x=1325, y=750, font_size=48, color=GREEN)

        scene.add(SketchAnimation(start_time=decoder_only_start + 0.5, duration=1.5), drawable=dec_title)
        
        scene.add(SketchAnimation(start_time=decoder_only_start + 2.0, duration=1.0), drawable=enc_box)
        scene.add(SketchAnimation(start_time=decoder_only_start + 3.0, duration=0.8), drawable=enc_cross)
        scene.add(SketchAnimation(start_time=decoder_only_start + 3.5, duration=0.8), drawable=enc_text)
        
        scene.add(SketchAnimation(start_time=decoder_only_start + 5.0, duration=1.5), drawable=dec_box)
        scene.add(SketchAnimation(start_time=decoder_only_start + 6.5, duration=1.0), drawable=dec_text)

        dec_only_drawables.extend([dec_title, enc_box, enc_cross, enc_text, dec_box, dec_text])

        # ---------------------------------------------------------
        # SECTION 3: Autoregressive Loop
        # ---------------------------------------------------------
        make_eraser(dec_only_drawables, start_time=autoregressive_start - 1.5)

        ar_drawables =[]

        ar_title = make_title("Autoregressive Generation", y=140, color=BLUE)
        ar_sub = make_body("Rule #1: Predict the next word.", y=260, color=ORANGE, font_size=56)
        
        # Center GPT block
        gpt_box = FlowchartProcess("GPT Model", top_left=(760, 450), width=400, height=180, font_size=56, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        
        # I/O setup
        in_txt = make_body("'The sky is'", x=450, y=540, font_size=56)
        arr_in = Arrow(start_point=(600, 540), end_point=(740, 540), stroke_style=box_stroke)
        
        arr_out = Arrow(start_point=(1180, 540), end_point=(1320, 540), stroke_style=box_stroke)
        out_txt = make_body("'blue'", x=1450, y=540, font_size=64, color=RED)

        # Loop Arrow
        loop_arrow = CurvedArrow(points=[(1450, 600), (960, 850), (450, 600)], stroke_style=StrokeStyle(color=GREEN, width=5.0))
        loop_text = make_body("Loop back to predict again", x=960, y=880, color=GREEN, font_size=48)

        scene.add(SketchAnimation(start_time=autoregressive_start + 0.5, duration=1.5), drawable=ar_title)
        scene.add(SketchAnimation(start_time=autoregressive_start + 2.0, duration=1.0), drawable=ar_sub)
        
        scene.add(SketchAnimation(start_time=autoregressive_start + 3.5, duration=1.0), drawable=in_txt)
        scene.add(SketchAnimation(start_time=autoregressive_start + 4.0, duration=0.5), drawable=arr_in)
        scene.add(SketchAnimation(start_time=autoregressive_start + 4.5, duration=1.0), drawable=gpt_box)
        scene.add(SketchAnimation(start_time=autoregressive_start + 5.5, duration=0.5), drawable=arr_out)
        scene.add(SketchAnimation(start_time=autoregressive_start + 6.0, duration=1.0), drawable=out_txt)
        
        scene.add(SketchAnimation(start_time=autoregressive_start + 7.5, duration=1.0), drawable=loop_arrow)
        scene.add(SketchAnimation(start_time=autoregressive_start + 8.5, duration=1.0), drawable=loop_text)

        ar_drawables.extend([ar_title, ar_sub, gpt_box, in_txt, arr_in, arr_out, out_txt, loop_arrow, loop_text])

        # ---------------------------------------------------------
        # SECTION 4: GPT-3 Stats & Architecture
        # ---------------------------------------------------------
        make_eraser(ar_drawables, start_time=gpt3_stats_start - 1.5)

        stats_drawables =[]

        gpt3_title = make_title("The Scale of GPT-3 (2020)", y=140, color=GREEN)
        gpt3_sub = make_body("Same objective, unimaginable scale.", y=260, color=BLACK, font_size=48)

        scene.add(SketchAnimation(start_time=gpt3_stats_start + 0.5, duration=1.5), drawable=gpt3_title)
        scene.add(SketchAnimation(start_time=gpt3_stats_start + 2.0, duration=1.0), drawable=gpt3_sub)

        stats_drawables.extend([gpt3_title, gpt3_sub])

        # Parameters & Tokens
        box_p = FlowchartProcess("175 Billion Parameters", top_left=(250, 400), width=500, height=120, font_size=46, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        p_desc = make_body("Artificial Brain Synapses", x=500, y=560, font_size=42, color=ORANGE)

        box_t = FlowchartProcess("300 Billion Tokens", top_left=(250, 700), width=500, height=120, font_size=46, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        t_desc = make_body("The Entire Public Internet", x=500, y=860, font_size=42, color=BLUE)

        scene.add(SketchAnimation(start_time=params_tokens_start + 0.5, duration=1.5), drawable=box_p)
        scene.add(SketchAnimation(start_time=params_tokens_start + 2.0, duration=1.0), drawable=p_desc)
        
        scene.add(SketchAnimation(start_time=params_tokens_start + 4.5, duration=1.5), drawable=box_t)
        scene.add(SketchAnimation(start_time=params_tokens_start + 6.0, duration=1.0), drawable=t_desc)

        stats_drawables.extend([box_p, p_desc, box_t, t_desc])

        # Massive Stack of Layers
        stack_title = make_body("Massive Decoder Stack", x=1400, y=340, font_size=48, color=RED)
        
        layer96 = Rectangle(top_left=(1150, 420), width=500, height=80, stroke_style=box_stroke, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        l96_txt = make_body("Layer 96", x=1400, y=460, font_size=42)
        
        layer_dots = make_body("• • •", x=1400, y=550, font_size=80)
        
        layer2 = Rectangle(top_left=(1150, 620), width=500, height=80, stroke_style=box_stroke, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        l2_txt = make_body("Layer 2", x=1400, y=660, font_size=42)
        
        layer1 = Rectangle(top_left=(1150, 740), width=500, height=80, stroke_style=box_stroke, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), sketch_style=SKETCH)
        l1_txt = make_body("Layer 1", x=1400, y=780, font_size=42)

        heads_txt = make_body("(96 Attention Heads per layer)", x=1400, y=880, font_size=36, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=layers_start + 0.5, duration=1.0), drawable=stack_title)
        scene.add(SketchAnimation(start_time=layers_start + 1.5, duration=0.8), drawable=layer1)
        scene.add(SketchAnimation(start_time=layers_start + 1.5, duration=0.8), drawable=l1_txt)
        scene.add(SketchAnimation(start_time=layers_start + 2.3, duration=0.8), drawable=layer2)
        scene.add(SketchAnimation(start_time=layers_start + 2.3, duration=0.8), drawable=l2_txt)
        scene.add(SketchAnimation(start_time=layers_start + 3.1, duration=0.5), drawable=layer_dots)
        scene.add(SketchAnimation(start_time=layers_start + 3.6, duration=0.8), drawable=layer96)
        scene.add(SketchAnimation(start_time=layers_start + 3.6, duration=0.8), drawable=l96_txt)
        scene.add(SketchAnimation(start_time=layers_start + 4.5, duration=1.0), drawable=heads_txt)

        stats_drawables.extend([stack_title, layer96, l96_txt, layer_dots, layer2, l2_txt, layer1, l1_txt, heads_txt])

        # ---------------------------------------------------------
        # SECTION 5: Summary & Outro
        # ---------------------------------------------------------
        make_eraser(stats_drawables, start_time=summary_start - 1.5)

        sum_drawables =[]

        sum_title = make_title("The Equation for Intelligence", y=200, color=BLUE)

        # Equation Style
        eq_part1 = make_body("Predicting the\nNext Word", x=450, y=450, font_size=56, color=ORANGE)
        plus_sign = make_body("+", x=960, y=450, font_size=100, color=BLACK)
        eq_part2 = make_body("Unimaginable\nScale", x=1470, y=450, font_size=56, color=GREEN)
        
        equals_sign = make_body("=", x=960, y=650, font_size=100, color=BLACK)
        eq_result = make_body("Emergent Reasoning", x=960, y=800, font_size=80, color=RED)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.5), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 2.5, duration=1.2), drawable=eq_part1)
        scene.add(SketchAnimation(start_time=summary_start + 4.0, duration=0.5), drawable=plus_sign)
        scene.add(SketchAnimation(start_time=summary_start + 4.5, duration=1.2), drawable=eq_part2)
        scene.add(SketchAnimation(start_time=summary_start + 6.5, duration=0.5), drawable=equals_sign)
        scene.add(SketchAnimation(start_time=summary_start + 7.0, duration=1.5), drawable=eq_result)

        sum_drawables.extend([sum_title, eq_part1, plus_sign, eq_part2, equals_sign, eq_result])

        # Outro
        make_eraser(sum_drawables, start_time=outro_start - 1.5)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now know how GPT actually works.", y=600, color=BLACK)

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