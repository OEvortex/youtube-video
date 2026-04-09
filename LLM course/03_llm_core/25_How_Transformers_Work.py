"""
Whiteboard explainer: Deep Dive into Transformers Architecture

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It features a proper, progressively drawn block diagram of the architecture 
and strict erasing to guarantee no text overwrite.
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
from handanim.primitives import Arrow, FlowchartProcess
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = ROOT / "output"
AUDIO_PATH = OUTPUT_DIR / "detailed_transformers_diagram_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "detailed_transformers_diagram_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> What are Transformers? They are the deep learning architecture that changed artificial intelligence forever. "
    "Introduced in 2017 by Google in the paper 'Attention Is All You Need', "
    "they replaced slow, sequential models with a system that processes data in parallel. "
    
    "<bookmark mark='arch_overview'/> Let's draw the full architecture. It consists of two main halves: "
    "The Encoder block on the left, and the Decoder block on the right. "
    "Let's break down exactly how data flows through them. "
    
    "<bookmark mark='token_embed'/> Step 1 is Tokenization and Embedding. "
    "The input text is mapped into high-dimensional numerical vectors. "
    "This translates human language into math, capturing the core meaning of the words. "
    
    "<bookmark mark='pos_encode'/> Step 2 is Positional Encoding. "
    "Because Transformers process all words at once, they lose the order of the sentence. "
    "Positional encoding fixes this by adding mathematical sine and cosine wave patterns to the vectors. "
    
    "<bookmark mark='self_attn'/> Step 3 is the true magic: The Self-Attention Mechanism. "
    "This allows the model to figure out how every word relates to every other word. "
    "It uses Query, Key, and Value matrices to analyze contextual relationships from multiple angles. "
    
    "<bookmark mark='encoder_block'/> Step 4 is the full Encoder Stack. "
    "By passing data through Attention and Feed-Forward Neural Networks, "
    "the Encoder outputs a deeply contextualized representation of the original input. "
    
    "<bookmark mark='decoder_block'/> Step 5 is the Decoder. "
    "It uses Masked Self-Attention to prevent cheating by looking into the future, "
    "and Cross-Attention to look back at the Encoder's context. "
    "Finally, Linear and Softmax layers generate the output sequence one token at a time. "
    
    "<bookmark mark='bert_gpt'/> Today, this architecture has splintered into specialized models. "
    "Models like BERT use only the Encoder block to deeply understand text. "
    "Meanwhile, models like GPT use only the Decoder block to autoregressively generate entirely new text. "
    
    "<bookmark mark='outro'/> Together, these form the foundation of all modern Large Language Models. "
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
        # Retrieve timestamps for synced drawing
        intro_start = tracker.bookmark_time("intro")
        arch_start = tracker.bookmark_time("arch_overview")
        token_start = tracker.bookmark_time("token_embed")
        pos_start = tracker.bookmark_time("pos_encode")
        self_attn_start = tracker.bookmark_time("self_attn")
        enc_block_start = tracker.bookmark_time("encoder_block")
        dec_block_start = tracker.bookmark_time("decoder_block")
        bert_gpt_start = tracker.bookmark_time("bert_gpt")
        outro_start = tracker.bookmark_time("outro")

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("The Transformer Architecture", y=300, color=BLUE)
        intro_paper = make_body("'Attention Is All You Need' (Google, 2017)", y=450, color=GREEN)
        intro_note = make_body("The deep neural network that changed AI forever.", y=600, color=ORANGE)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_paper)
        scene.add(SketchAnimation(start_time=intro_start + 4.5, duration=1.5), drawable=intro_note)

        intro_drawables =[intro_title, intro_paper, intro_note]

        # ---------------------------------------------------------
        # SECTION 2: Architecture Diagram Setup (Progressive)
        # ---------------------------------------------------------
        # Erase previous section with ample time buffer before next narration
        make_eraser(intro_drawables, start_time=arch_start - 1.5)

        diagram_drawables =[]
        
        # Styles for diagram
        box_stroke = StrokeStyle(color=BLACK, width=3.0)
        enc_fill = FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8)
        dec_fill = FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8)
        neutral_fill = FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8)

        # 1. Arch Overview (Boundaries)
        enc_bound = Rectangle(top_left=(280, 320), width=440, height=280, stroke_style=StrokeStyle(color=GRAY, width=4.0), sketch_style=SKETCH)
        enc_label = make_body("Encoder Block (Nx)", x=500, y=280, color=GREEN, font_size=42)
        
        dec_bound = Rectangle(top_left=(1200, 280), width=440, height=420, stroke_style=StrokeStyle(color=GRAY, width=4.0), sketch_style=SKETCH)
        dec_label = make_body("Decoder Block (Nx)", x=1420, y=240, color=RED, font_size=42)

        scene.add(SketchAnimation(start_time=arch_start + 0.5, duration=1.5), drawable=enc_bound)
        scene.add(SketchAnimation(start_time=arch_start + 1.0, duration=1.0), drawable=enc_label)
        scene.add(SketchAnimation(start_time=arch_start + 2.0, duration=1.5), drawable=dec_bound)
        scene.add(SketchAnimation(start_time=arch_start + 2.5, duration=1.0), drawable=dec_label)
        
        diagram_drawables.extend([enc_bound, enc_label, dec_bound, dec_label])

        # 2. Tokenization & Embeddings
        enc_in = make_body("Inputs", x=500, y=940, font_size=46)
        enc_in_arr = Arrow(start_point=(500, 910), end_point=(500, 870), stroke_style=box_stroke)
        enc_embed = FlowchartProcess("Input Embedding", top_left=(320, 800), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=neutral_fill)
        
        dec_in = make_body("Outputs (shifted right)", x=1420, y=940, font_size=46)
        dec_in_arr = Arrow(start_point=(1420, 910), end_point=(1420, 870), stroke_style=box_stroke)
        dec_embed = FlowchartProcess("Output Embedding", top_left=(1240, 800), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=neutral_fill)

        scene.add(SketchAnimation(start_time=token_start + 0.5, duration=0.8), drawable=enc_in)
        scene.add(SketchAnimation(start_time=token_start + 1.0, duration=0.5), drawable=enc_in_arr)
        scene.add(SketchAnimation(start_time=token_start + 1.5, duration=1.0), drawable=enc_embed)
        scene.add(SketchAnimation(start_time=token_start + 2.5, duration=0.8), drawable=dec_in)
        scene.add(SketchAnimation(start_time=token_start + 3.0, duration=0.5), drawable=dec_in_arr)
        scene.add(SketchAnimation(start_time=token_start + 3.5, duration=1.0), drawable=dec_embed)

        diagram_drawables.extend([enc_in, enc_in_arr, enc_embed, dec_in, dec_in_arr, dec_embed])

        # 3. Positional Encoding
        enc_emb_arr = Arrow(start_point=(500, 800), end_point=(500, 750), stroke_style=box_stroke)
        enc_pos = FlowchartProcess("Positional Encoding", top_left=(320, 680), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=neutral_fill)
        
        dec_emb_arr = Arrow(start_point=(1420, 800), end_point=(1420, 750), stroke_style=box_stroke)
        dec_pos = FlowchartProcess("Positional Encoding", top_left=(1240, 680), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=neutral_fill)

        scene.add(SketchAnimation(start_time=pos_start + 0.5, duration=0.5), drawable=enc_emb_arr)
        scene.add(SketchAnimation(start_time=pos_start + 1.0, duration=1.0), drawable=enc_pos)
        scene.add(SketchAnimation(start_time=pos_start + 2.0, duration=0.5), drawable=dec_emb_arr)
        scene.add(SketchAnimation(start_time=pos_start + 2.5, duration=1.0), drawable=dec_pos)

        diagram_drawables.extend([enc_emb_arr, enc_pos, dec_emb_arr, dec_pos])

        # 4. Self Attention
        enc_pos_arr = Arrow(start_point=(500, 680), end_point=(500, 570), stroke_style=box_stroke)
        enc_attn = FlowchartProcess("Multi-Head Attention", top_left=(320, 500), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=enc_fill)

        scene.add(SketchAnimation(start_time=self_attn_start + 0.5, duration=0.5), drawable=enc_pos_arr)
        scene.add(SketchAnimation(start_time=self_attn_start + 1.0, duration=1.5), drawable=enc_attn)

        diagram_drawables.extend([enc_pos_arr, enc_attn])

        # 5. Encoder Block (Feed Forward)
        enc_attn_arr = Arrow(start_point=(500, 500), end_point=(500, 410), stroke_style=box_stroke)
        enc_ff = FlowchartProcess("Feed Forward", top_left=(320, 340), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=enc_fill)

        scene.add(SketchAnimation(start_time=enc_block_start + 0.5, duration=0.5), drawable=enc_attn_arr)
        scene.add(SketchAnimation(start_time=enc_block_start + 1.0, duration=1.5), drawable=enc_ff)

        diagram_drawables.extend([enc_attn_arr, enc_ff])

        # 6. Decoder Block
        dec_pos_arr = Arrow(start_point=(1420, 680), end_point=(1420, 650), stroke_style=box_stroke)
        dec_mask_attn = FlowchartProcess("Masked Multi-Head Attn", top_left=(1240, 580), width=360, height=70, font_size=32, stroke_style=box_stroke, fill_style=dec_fill)
        
        dec_mask_arr = Arrow(start_point=(1420, 580), end_point=(1420, 510), stroke_style=box_stroke)
        dec_cross_attn = FlowchartProcess("Cross-Attention", top_left=(1240, 440), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=dec_fill)
        
        # Link Encoder to Decoder
        cross_arrow = Arrow(start_point=(680, 375), end_point=(1240, 475), stroke_style=StrokeStyle(color=ORANGE, width=5.0))
        cross_label = make_body("Key & Value Matrices", x=960, y=410, color=ORANGE, font_size=32)

        dec_cross_arr = Arrow(start_point=(1420, 440), end_point=(1420, 370), stroke_style=box_stroke)
        dec_ff = FlowchartProcess("Feed Forward", top_left=(1240, 300), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=dec_fill)

        dec_ff_arr = Arrow(start_point=(1420, 280), end_point=(1420, 210), stroke_style=box_stroke)
        dec_linear = FlowchartProcess("Linear & Softmax", top_left=(1240, 140), width=360, height=70, font_size=36, stroke_style=box_stroke, fill_style=neutral_fill)
        
        dec_lin_arr = Arrow(start_point=(1420, 140), end_point=(1420, 100), stroke_style=box_stroke)
        dec_out = make_body("Output Probabilities", x=1420, y=60, font_size=46, color=RED)

        scene.add(SketchAnimation(start_time=dec_block_start + 0.5, duration=0.5), drawable=dec_pos_arr)
        scene.add(SketchAnimation(start_time=dec_block_start + 1.0, duration=1.0), drawable=dec_mask_attn)
        scene.add(SketchAnimation(start_time=dec_block_start + 2.0, duration=0.5), drawable=dec_mask_arr)
        scene.add(SketchAnimation(start_time=dec_block_start + 2.5, duration=1.0), drawable=dec_cross_attn)
        
        scene.add(SketchAnimation(start_time=dec_block_start + 4.0, duration=1.0), drawable=cross_arrow)
        scene.add(SketchAnimation(start_time=dec_block_start + 4.5, duration=0.8), drawable=cross_label)
        
        scene.add(SketchAnimation(start_time=dec_block_start + 5.5, duration=0.5), drawable=dec_cross_arr)
        scene.add(SketchAnimation(start_time=dec_block_start + 6.0, duration=1.0), drawable=dec_ff)
        scene.add(SketchAnimation(start_time=dec_block_start + 7.0, duration=0.5), drawable=dec_ff_arr)
        scene.add(SketchAnimation(start_time=dec_block_start + 7.5, duration=1.0), drawable=dec_linear)
        scene.add(SketchAnimation(start_time=dec_block_start + 8.5, duration=0.5), drawable=dec_lin_arr)
        scene.add(SketchAnimation(start_time=dec_block_start + 9.0, duration=1.0), drawable=dec_out)

        diagram_drawables.extend([
            dec_pos_arr, dec_mask_attn, dec_mask_arr, dec_cross_attn, 
            cross_arrow, cross_label, dec_cross_arr, dec_ff, 
            dec_ff_arr, dec_linear, dec_lin_arr, dec_out
        ])

        # ---------------------------------------------------------
        # SECTION 3: BERT vs GPT
        # ---------------------------------------------------------
        make_eraser(diagram_drawables, start_time=bert_gpt_start - 1.5)

        split_title = make_title("The Modern Splintering", y=200, color=BLUE)

        # Left: BERT
        bert_title = make_body("BERT", x=500, y=400, color=GREEN, font_size=90)
        bert_box = FlowchartProcess("Encoder-Only Architecture", top_left=(320, 500), width=360, height=80, font_size=36, fill_style=enc_fill)
        bert_bullet1 = make_body("• Bidirectional Context", x=500, y=650, font_size=42)
        bert_bullet2 = make_body("• Deep Understanding", x=500, y=750, font_size=42)

        # Right: GPT
        gpt_title = make_body("GPT", x=1420, y=400, color=RED, font_size=90)
        gpt_box = FlowchartProcess("Decoder-Only Architecture", top_left=(1240, 500), width=360, height=80, font_size=36, fill_style=dec_fill)
        gpt_bullet1 = make_body("• Autoregressive Generation", x=1420, y=650, font_size=42)
        gpt_bullet2 = make_body("• Creates New Text", x=1420, y=750, font_size=42)

        scene.add(SketchAnimation(start_time=bert_gpt_start + 0.5, duration=1.5), drawable=split_title)
        
        scene.add(SketchAnimation(start_time=bert_gpt_start + 2.5, duration=1.0), drawable=bert_title)
        scene.add(SketchAnimation(start_time=bert_gpt_start + 3.5, duration=1.0), drawable=bert_box)
        scene.add(SketchAnimation(start_time=bert_gpt_start + 4.5, duration=1.0), drawable=bert_bullet1)
        scene.add(SketchAnimation(start_time=bert_gpt_start + 5.5, duration=1.0), drawable=bert_bullet2)

        scene.add(SketchAnimation(start_time=bert_gpt_start + 7.5, duration=1.0), drawable=gpt_title)
        scene.add(SketchAnimation(start_time=bert_gpt_start + 8.5, duration=1.0), drawable=gpt_box)
        scene.add(SketchAnimation(start_time=bert_gpt_start + 9.5, duration=1.0), drawable=gpt_bullet1)
        scene.add(SketchAnimation(start_time=bert_gpt_start + 10.5, duration=1.0), drawable=gpt_bullet2)

        split_drawables =[
            split_title, bert_title, bert_box, bert_bullet1, bert_bullet2, 
            gpt_title, gpt_box, gpt_bullet1, gpt_bullet2
        ]

        # ---------------------------------------------------------
        # SECTION 4: Outro
        # ---------------------------------------------------------
        make_eraser(split_drawables, start_time=outro_start - 1.5)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now know the deep mechanics of Transformers.", y=600, color=BLACK)

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