"""
Whiteboard explainer: Encoder vs Decoder in Deep Detail

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It heavily details the functional differences between the Encoder and Decoder,
explaining bidirectional vs unidirectional flow, masked attention, and use cases.
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
from handanim.primitives import Arrow, FlowchartProcess, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = ROOT / "output"
AUDIO_PATH = OUTPUT_DIR / "encoder_vs_decoder_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "encoder_vs_decoder_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> What is the exact difference between an Encoder and a Decoder? "
    "In modern AI, these are the two fundamental engines that power Large Language Models. "
    "Let's break down their mechanics in deep detail. "
    
    "<bookmark mark='encoder_def'/> Let's start with the Encoder. Think of the Encoder as the 'Reader'. "
    "Its primary job is to process the input text and build a deep, rich contextual understanding of it. "
    
    "<bookmark mark='encoder_mech'/> The defining feature of the Encoder is that it reads bidirectionally. "
    "This means its Self-Attention mechanism looks at the entire sequence at once. "
    "It looks both left and right to understand how words relate to their surrounding context. "
    "Models that only use an Encoder, like BERT, excel at tasks like document classification and sentiment analysis. "
    
    "<bookmark mark='decoder_def'/> Now, let's look at the Decoder. Think of the Decoder as the 'Writer' or 'Generator'. "
    "Its primary job is to produce new text, outputting one token at a time. "
    
    "<bookmark mark='decoder_mech'/> Unlike the Encoder, the Decoder is strictly unidirectional and autoregressive. "
    "It uses a mechanism called 'Masked Attention'. This means it can only look at the words it has already generated, "
    "and it is completely blind to the future. "
    "Models that only use a Decoder, like GPT, are the powerhouse behind modern chatbots and text generation. "
    
    "<bookmark mark='seq2seq'/> But what happens when you combine them? "
    "In the original Sequence-to-Sequence Transformer, they work together via 'Cross-Attention'. "
    "The Encoder processes the source language into a context vector. "
    "Then, the Decoder generates the translated text, constantly looking back at the Encoder's context to know what to write next. "
    
    "<bookmark mark='summary'/> To summarize: "
    "The Encoder is for understanding, reads bidirectionally, and powers models like BERT. "
    "The Decoder is for generation, reads unidirectionally, and powers models like GPT. "
    
    "<bookmark mark='outro'/> Knowing the difference gives you the keys to understanding modern AI architectures. "
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
        enc_def_start = tracker.bookmark_time("encoder_def")
        enc_mech_start = tracker.bookmark_time("encoder_mech")
        dec_def_start = tracker.bookmark_time("decoder_def")
        dec_mech_start = tracker.bookmark_time("decoder_mech")
        seq2seq_start = tracker.bookmark_time("seq2seq")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Encoder vs Decoder", y=300, color=BLUE)
        intro_sub = make_body("The Two Engines of the Transformer", y=450, color=BLACK, font_size=64)
        intro_note = make_body("Understanding the DNA of modern Large Language Models.", y=650, color=ORANGE)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        scene.add(SketchAnimation(start_time=intro_start + 4.5, duration=1.5), drawable=intro_note)

        intro_drawables =[intro_title, intro_sub, intro_note]

        # ---------------------------------------------------------
        # SECTION 2: The Encoder (Definition & Mechanics)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=enc_def_start - 1.5)

        enc_drawables =[]
        box_stroke = StrokeStyle(color=BLACK, width=3.0)
        enc_fill = FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8)

        enc_title = make_title("The Encoder: 'The Reader'", y=140, color=GREEN)
        
        # Encoder diagram
        enc_box = FlowchartProcess("Encoder Block", top_left=(200, 350), width=400, height=200, font_size=48, fill_style=enc_fill, stroke_style=box_stroke)
        enc_input = make_body("Input: 'The bank is closed'", x=400, y=700, font_size=42)
        enc_in_arr = Arrow(start_point=(400, 650), end_point=(400, 570), stroke_style=box_stroke)
        enc_out_arr = Arrow(start_point=(400, 330), end_point=(400, 250), stroke_style=box_stroke)
        enc_output = make_body("Rich Context Vector", x=400, y=200, color=BLUE, font_size=42)

        scene.add(SketchAnimation(start_time=enc_def_start + 0.5, duration=1.5), drawable=enc_title)
        scene.add(SketchAnimation(start_time=enc_def_start + 2.5, duration=1.0), drawable=enc_box)
        scene.add(SketchAnimation(start_time=enc_def_start + 3.5, duration=1.0), drawable=enc_input)
        scene.add(SketchAnimation(start_time=enc_def_start + 4.0, duration=0.5), drawable=enc_in_arr)
        scene.add(SketchAnimation(start_time=enc_def_start + 5.0, duration=0.5), drawable=enc_out_arr)
        scene.add(SketchAnimation(start_time=enc_def_start + 5.5, duration=1.0), drawable=enc_output)

        enc_drawables.extend([enc_title, enc_box, enc_input, enc_in_arr, enc_out_arr, enc_output])

        # Encoder Mechanics (Bidirectional)
        bidi_title = make_body("Key Feature: Bidirectional", x=1300, y=350, color=ORANGE, font_size=56)
        
        # Diagram of bidirectional flow
        word1 = make_body("word_1", x=1050, y=450, font_size=40)
        word2 = make_body("word_2", x=1300, y=450, font_size=40, color=BLUE) # focus word
        word3 = make_body("word_3", x=1550, y=450, font_size=40)
        
        arr_left = Arrow(start_point=(1220, 450), end_point=(1130, 450), stroke_style=StrokeStyle(color=GREEN, width=3.0))
        arr_right = Arrow(start_point=(1380, 450), end_point=(1470, 450), stroke_style=StrokeStyle(color=GREEN, width=3.0))
        
        enc_bullets = make_bullet_list([
            "Looks left and right simultaneously",
            "Understands full surrounding context",
            "Perfect for: Classification, Sentiment",
            "Famous Model: BERT"
        ], y_start=600, x=950, font_size=42)

        scene.add(SketchAnimation(start_time=enc_mech_start + 0.5, duration=1.0), drawable=bidi_title)
        scene.add(SketchAnimation(start_time=enc_mech_start + 2.0, duration=0.5), drawable=word1)
        scene.add(SketchAnimation(start_time=enc_mech_start + 2.3, duration=0.5), drawable=word2)
        scene.add(SketchAnimation(start_time=enc_mech_start + 2.6, duration=0.5), drawable=word3)
        scene.add(SketchAnimation(start_time=enc_mech_start + 3.0, duration=0.8), drawable=arr_left)
        scene.add(SketchAnimation(start_time=enc_mech_start + 3.0, duration=0.8), drawable=arr_right)
        
        for i, b in enumerate(enc_bullets):
            scene.add(SketchAnimation(start_time=enc_mech_start + 5.0 + (i * 1.5), duration=1.0), drawable=b)

        enc_drawables.extend([bidi_title, word1, word2, word3, arr_left, arr_right] + enc_bullets)

        # ---------------------------------------------------------
        # SECTION 3: The Decoder (Definition & Mechanics)
        # ---------------------------------------------------------
        make_eraser(enc_drawables, start_time=dec_def_start - 1.5)

        dec_drawables =[]
        dec_fill = FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8)

        dec_title = make_title("The Decoder: 'The Writer'", y=140, color=RED)
        
        # Decoder diagram
        dec_box = FlowchartProcess("Decoder Block", top_left=(200, 350), width=400, height=200, font_size=48, fill_style=dec_fill, stroke_style=box_stroke)
        dec_input = make_body("Input: 'Once upon a...'", x=400, y=700, font_size=42)
        dec_in_arr = Arrow(start_point=(400, 650), end_point=(400, 570), stroke_style=box_stroke)
        dec_out_arr = Arrow(start_point=(400, 330), end_point=(400, 250), stroke_style=box_stroke)
        dec_output = make_body("Generated: 'time'", x=400, y=200, color=BLUE, font_size=42)

        scene.add(SketchAnimation(start_time=dec_def_start + 0.5, duration=1.5), drawable=dec_title)
        scene.add(SketchAnimation(start_time=dec_def_start + 2.5, duration=1.0), drawable=dec_box)
        scene.add(SketchAnimation(start_time=dec_def_start + 3.5, duration=1.0), drawable=dec_input)
        scene.add(SketchAnimation(start_time=dec_def_start + 4.0, duration=0.5), drawable=dec_in_arr)
        scene.add(SketchAnimation(start_time=dec_def_start + 5.0, duration=0.5), drawable=dec_out_arr)
        scene.add(SketchAnimation(start_time=dec_def_start + 5.5, duration=1.0), drawable=dec_output)

        dec_drawables.extend([dec_title, dec_box, dec_input, dec_in_arr, dec_out_arr, dec_output])

        # Decoder Mechanics (Unidirectional)
        uni_title = make_body("Key Feature: Unidirectional (Masked)", x=1300, y=350, color=ORANGE, font_size=52)
        
        # Diagram of unidirectional flow (Masked)
        word1_d = make_body("word_1", x=1050, y=450, font_size=40)
        word2_d = make_body("word_2", x=1300, y=450, font_size=40, color=BLUE) # focus word
        word3_d = make_body("word_3", x=1550, y=450, font_size=40, color=DARK_GRAY)
        
        arr_left_d = Arrow(start_point=(1130, 450), end_point=(1220, 450), stroke_style=StrokeStyle(color=RED, width=3.0)) # Can look back
        cross_mask = Text("X", position=(1425, 450), font_size=60, font_name=FONT_NAME, stroke_style=StrokeStyle(color=RED, width=4.0)) # Cannot look forward
        
        dec_bullets = make_bullet_list([
            "Autoregressive: Generates 1 token at a time",
            "Masked Attention: Blind to future words",
            "Perfect for: Text Gen, Chatbots, Code",
            "Famous Model: GPT"
        ], y_start=600, x=950, font_size=42)

        scene.add(SketchAnimation(start_time=dec_mech_start + 0.5, duration=1.0), drawable=uni_title)
        scene.add(SketchAnimation(start_time=dec_mech_start + 2.0, duration=0.5), drawable=word1_d)
        scene.add(SketchAnimation(start_time=dec_mech_start + 2.3, duration=0.5), drawable=word2_d)
        scene.add(SketchAnimation(start_time=dec_mech_start + 2.6, duration=0.5), drawable=word3_d)
        scene.add(SketchAnimation(start_time=dec_mech_start + 3.0, duration=0.8), drawable=arr_left_d)
        scene.add(SketchAnimation(start_time=dec_mech_start + 4.5, duration=0.8), drawable=cross_mask)
        
        for i, b in enumerate(dec_bullets):
            scene.add(SketchAnimation(start_time=dec_mech_start + 7.0 + (i * 1.5), duration=1.0), drawable=b)

        dec_drawables.extend([uni_title, word1_d, word2_d, word3_d, arr_left_d, cross_mask] + dec_bullets)

        # ---------------------------------------------------------
        # SECTION 4: Cross-Attention (Seq2Seq)
        # ---------------------------------------------------------
        make_eraser(dec_drawables, start_time=seq2seq_start - 1.5)
        
        seq_drawables =[]

        seq_title = make_title("Together: Sequence-to-Sequence", y=140, color=BLUE)
        seq_sub = make_body("The Original Architecture (e.g., Translation)", y=260, color=BLACK, font_size=50)

        # Blocks
        enc_s_box = FlowchartProcess("Encoder", top_left=(300, 500), width=350, height=150, font_size=56, fill_style=enc_fill, stroke_style=box_stroke)
        dec_s_box = FlowchartProcess("Decoder", top_left=(1270, 500), width=350, height=150, font_size=56, fill_style=dec_fill, stroke_style=box_stroke)
        
        # Flows
        in_txt = make_body("English: 'Hello'", x=475, y=750, font_size=46, color=GREEN)
        in_arr = Arrow(start_point=(475, 700), end_point=(475, 660), stroke_style=box_stroke)

        out_txt = make_body("French: 'Bonjour'", x=1445, y=350, font_size=46, color=RED)
        out_arr = Arrow(start_point=(1445, 490), end_point=(1445, 410), stroke_style=box_stroke)

        # Cross Attention Arrow
        cross_arr = Arrow(start_point=(670, 575), end_point=(1250, 575), stroke_style=StrokeStyle(color=ORANGE, width=6.0))
        cross_label = make_body("Cross-Attention", x=960, y=500, font_size=48, color=ORANGE)
        cross_sub = make_body("(Context flows to Decoder)", x=960, y=650, font_size=36, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=seq2seq_start + 0.5, duration=1.0), drawable=seq_title)
        scene.add(SketchAnimation(start_time=seq2seq_start + 1.5, duration=1.0), drawable=seq_sub)
        
        scene.add(SketchAnimation(start_time=seq2seq_start + 3.0, duration=1.0), drawable=enc_s_box)
        scene.add(SketchAnimation(start_time=seq2seq_start + 3.5, duration=0.8), drawable=in_txt)
        scene.add(SketchAnimation(start_time=seq2seq_start + 4.0, duration=0.5), drawable=in_arr)
        
        scene.add(SketchAnimation(start_time=seq2seq_start + 6.0, duration=1.0), drawable=dec_s_box)
        scene.add(SketchAnimation(start_time=seq2seq_start + 7.5, duration=1.0), drawable=cross_arr)
        scene.add(SketchAnimation(start_time=seq2seq_start + 8.0, duration=0.8), drawable=cross_label)
        scene.add(SketchAnimation(start_time=seq2seq_start + 8.5, duration=0.8), drawable=cross_sub)
        
        scene.add(SketchAnimation(start_time=seq2seq_start + 10.0, duration=0.5), drawable=out_arr)
        scene.add(SketchAnimation(start_time=seq2seq_start + 10.5, duration=1.0), drawable=out_txt)

        seq_drawables.extend([seq_title, seq_sub, enc_s_box, dec_s_box, in_txt, in_arr, out_txt, out_arr, cross_arr, cross_label, cross_sub])

        # ---------------------------------------------------------
        # SECTION 5: Summary & Outro
        # ---------------------------------------------------------
        make_eraser(seq_drawables, start_time=summary_start - 1.5)

        sum_drawables =[]

        sum_title = make_title("Summary Comparison", y=140, color=BLUE)

        # Table-like visual
        mid_line = Line(start=(960, 250), end=(960, 850), stroke_style=StrokeStyle(color=GRAY, width=4.0), sketch_style=SKETCH)

        # Left: Encoder
        sum_enc_title = make_body("ENCODER", x=480, y=300, font_size=72, color=GREEN)
        sum_enc_bullets = make_bullet_list([
            "Focus: Understanding context",
            "Flow: Bidirectional",
            "Mechanism: Self-Attention",
            "Example Model: BERT"
        ], y_start=450, x=150, font_size=44)

        # Right: Decoder
        sum_dec_title = make_body("DECODER", x=1440, y=300, font_size=72, color=RED)
        sum_dec_bullets = make_bullet_list([
            "Focus: Generating sequences",
            "Flow: Unidirectional",
            "Mechanism: Masked Attention",
            "Example Model: GPT"
        ], y_start=450, x=1100, font_size=44)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.5), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 1.5, duration=0.5), drawable=mid_line)
        
        scene.add(SketchAnimation(start_time=summary_start + 2.0, duration=1.0), drawable=sum_enc_title)
        for i, b in enumerate(sum_enc_bullets):
            scene.add(SketchAnimation(start_time=summary_start + 3.0 + (i * 0.5), duration=0.8), drawable=b)
            
        scene.add(SketchAnimation(start_time=summary_start + 5.5, duration=1.0), drawable=sum_dec_title)
        for i, b in enumerate(sum_dec_bullets):
            scene.add(SketchAnimation(start_time=summary_start + 6.5 + (i * 0.5), duration=0.8), drawable=b)

        sum_drawables.extend([sum_title, mid_line, sum_enc_title, sum_dec_title] + sum_enc_bullets + sum_dec_bullets)

        # Outro
        make_eraser(sum_drawables, start_time=outro_start - 1.5)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now understand the DNA of modern AI.", y=600, color=BLACK)

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