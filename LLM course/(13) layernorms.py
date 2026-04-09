"""
Whiteboard explainer: Layer Normalization & Residual Connections

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It heavily details the vanishing gradient problem, how Residual (Skip) Connections
solve it, how Layer Normalization stabilizes values, and the famous "Add & Norm" block.
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
from handanim.primitives import Arrow, CurvedArrow, FlowchartProcess, Line, LinearPath, Circle
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "architecture"
AUDIO_PATH = OUTPUT_DIR / "residual_layernorm_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "residual_layernorm_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome back! Inside every Transformer block, there are two unsung heroes that make deep AI models possible: "
    "Residual Connections and Layer Normalization. "
    
    "<bookmark mark='problem'/> To understand why we need them, we must look at the biggest problem in deep neural networks. "
    "When you stack dozens of layers on top of each other, data gets multiplied over and over. "
    "Eventually, the numbers either shrink to zero, which is called a Vanishing Gradient, "
    "or explode to infinity, completely destroying the network's ability to learn. "
    
    "<bookmark mark='residual_def'/> Enter the first hero: The Residual Connection, also known as a Skip Connection. "
    "Instead of forcing data to only travel through the complex neural network layer, we build a shortcut. "
    
    "<bookmark mark='residual_vis'/> Mathematically, it is beautifully simple. "
    "The input 'x' flows into the layer to become 'F of x'. "
    "But simultaneously, 'x' takes the bypass lane around the layer. "
    "At the end, they are added together. The output is 'x' plus 'F of x'. "
    "This guarantees that the original information is never lost, no matter how deep the network gets! "
    
    "<bookmark mark='layernorm_def'/> But we still have a problem. "
    "If we keep adding numbers together, they will grow larger and larger, making the network unstable. "
    "This is where Layer Normalization steps in as the great stabilizer. "
    
    "<bookmark mark='layernorm_vis'/> Layer Normalization takes a wild, unbalanced list of numbers and mathematically wrangles them. "
    "It calculates the mean and variance across the layer, and scales the numbers so they always center around zero. "
    "This perfectly balances the flow of data, keeping the network mathematically stable. "
    
    "<bookmark mark='add_and_norm'/> In the famous Transformer diagram, these two concepts are combined into the 'Add & Norm' step. "
    "Data goes through Self-Attention, gets Added to the residual shortcut, and then Normalized. "
    "The same process repeats for the Feed Forward network. "
    
    "<bookmark mark='outro'/> Together, Residual Connections and Layer Normalization are the architectural glue that holds massive AI models together. "
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
        problem_start = tracker.bookmark_time("problem")
        res_def_start = tracker.bookmark_time("residual_def")
        res_vis_start = tracker.bookmark_time("residual_vis")
        ln_def_start = tracker.bookmark_time("layernorm_def")
        ln_vis_start = tracker.bookmark_time("layernorm_vis")
        add_norm_start = tracker.bookmark_time("add_and_norm")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Layer Norm & Residuals", y=350, color=BLUE)
        intro_sub = make_body("The Unsung Heroes of Deep Learning", y=500, color=ORANGE, font_size=72)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 3.0, duration=1.5), drawable=intro_sub)

        intro_drawables =[intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: The Problem (Vanishing/Exploding Gradients)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=problem_start - 1.2)
        prob_drawables =[]

        prob_title = make_title("The Problem with Deep Networks", y=140, color=RED)
        
        # Stacked layers visual
        layer1 = FlowchartProcess("Layer 1", top_left=(300, 350), width=250, height=100, font_size=42, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=box_stroke)
        arr1 = Arrow(start_point=(550, 400), end_point=(650, 400), stroke_style=box_stroke)
        num1 = make_body("1.0", x=600, y=350, font_size=36, color=BLUE)

        layer2 = FlowchartProcess("Layer 2", top_left=(650, 350), width=250, height=100, font_size=42, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=box_stroke)
        arr2 = Arrow(start_point=(900, 400), end_point=(1000, 400), stroke_style=box_stroke)
        num2 = make_body("0.1", x=950, y=350, font_size=36, color=BLUE)

        layer_dots = make_body("• • •", x=1100, y=400, font_size=80)
        
        arr3 = Arrow(start_point=(1200, 400), end_point=(1300, 400), stroke_style=box_stroke)
        num3 = make_body("0.00001", x=1250, y=350, font_size=36, color=BLUE)

        layer99 = FlowchartProcess("Layer 99", top_left=(1300, 350), width=250, height=100, font_size=42, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=box_stroke)

        vanish_text = make_body("Vanishing Gradients!", x=960, y=600, font_size=80, color=RED)
        explode_text = make_body("Or Exploding to Infinity...", x=960, y=750, font_size=64, color=ORANGE)
        
        scene.add(SketchAnimation(start_time=problem_start + 0.5, duration=1.0), drawable=prob_title)
        
        scene.add(SketchAnimation(start_time=problem_start + 4.0, duration=0.8), drawable=layer1)
        scene.add(SketchAnimation(start_time=problem_start + 4.8, duration=0.5), drawable=arr1)
        scene.add(SketchAnimation(start_time=problem_start + 4.8, duration=0.5), drawable=num1)
        
        scene.add(SketchAnimation(start_time=problem_start + 5.5, duration=0.8), drawable=layer2)
        scene.add(SketchAnimation(start_time=problem_start + 6.3, duration=0.5), drawable=arr2)
        scene.add(SketchAnimation(start_time=problem_start + 6.3, duration=0.5), drawable=num2)
        
        scene.add(SketchAnimation(start_time=problem_start + 7.0, duration=0.5), drawable=layer_dots)
        scene.add(SketchAnimation(start_time=problem_start + 7.5, duration=0.5), drawable=arr3)
        scene.add(SketchAnimation(start_time=problem_start + 7.5, duration=0.5), drawable=num3)
        scene.add(SketchAnimation(start_time=problem_start + 8.0, duration=0.8), drawable=layer99)

        scene.add(SketchAnimation(start_time=problem_start + 11.0, duration=1.5), drawable=vanish_text)
        scene.add(SketchAnimation(start_time=problem_start + 14.0, duration=1.5), drawable=explode_text)

        prob_drawables.extend([prob_title, layer1, arr1, num1, layer2, arr2, num2, layer_dots, arr3, num3, layer99, vanish_text, explode_text])

        # ---------------------------------------------------------
        # SECTION 3: Residual Connections
        # ---------------------------------------------------------
        make_eraser(prob_drawables, start_time=res_def_start - 1.2)
        res_drawables =[]

        res_title = make_title("The Residual (Skip) Connection", y=140, color=GREEN)
        
        # Center Layer Block
        nn_layer = FlowchartProcess("Neural Network\nLayer F(x)", top_left=(760, 450), width=400, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=box_stroke)
        
        # Input 'x'
        arr_in = Arrow(start_point=(350, 550), end_point=(760, 550), stroke_style=box_stroke)
        txt_x = make_body("x", x=450, y=500, font_size=64, color=BLUE)

        # Processed Output 'F(x)'
        arr_out = Arrow(start_point=(1160, 550), end_point=(1400, 550), stroke_style=box_stroke)
        txt_fx = make_body("F(x)", x=1280, y=500, font_size=64, color=BLUE)

        # Skip Connection (The Shortcut)
        skip_curve = CurvedArrow(points=[(500, 550), (960, 200), (1450, 490)], stroke_style=StrokeStyle(color=GREEN, width=6.0))
        txt_skip = make_body("Bypass Lane (Shortcut)", x=960, y=180, font_size=48, color=GREEN)

        # Addition Node
        add_node = Circle(center=(1450, 550), radius=50, stroke_style=box_stroke, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.5))
        add_sign = make_body("+", x=1450, y=550, font_size=64, color=BLACK)

        arr_final = Arrow(start_point=(1500, 550), end_point=(1750, 550), stroke_style=box_stroke)
        txt_final = make_body("Output = x + F(x)", x=1625, y=500, font_size=56, color=RED)

        res_note = make_body("Original info flows freely. No gradients lost!", y=850, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=res_def_start + 0.5, duration=1.5), drawable=res_title)
        
        scene.add(SketchAnimation(start_time=res_vis_start + 0.5, duration=0.8), drawable=arr_in)
        scene.add(SketchAnimation(start_time=res_vis_start + 1.0, duration=0.8), drawable=txt_x)
        scene.add(SketchAnimation(start_time=res_vis_start + 1.5, duration=1.0), drawable=nn_layer)
        scene.add(SketchAnimation(start_time=res_vis_start + 2.5, duration=0.8), drawable=arr_out)
        scene.add(SketchAnimation(start_time=res_vis_start + 3.0, duration=0.8), drawable=txt_fx)

        scene.add(SketchAnimation(start_time=res_vis_start + 6.0, duration=1.5), drawable=skip_curve)
        scene.add(SketchAnimation(start_time=res_vis_start + 7.0, duration=1.0), drawable=txt_skip)

        scene.add(SketchAnimation(start_time=res_vis_start + 9.5, duration=0.5), drawable=add_node)
        scene.add(SketchAnimation(start_time=res_vis_start + 9.5, duration=0.5), drawable=add_sign)
        scene.add(SketchAnimation(start_time=res_vis_start + 10.0, duration=0.5), drawable=arr_final)
        scene.add(SketchAnimation(start_time=res_vis_start + 10.5, duration=1.0), drawable=txt_final)

        scene.add(SketchAnimation(start_time=res_vis_start + 13.0, duration=1.5), drawable=res_note)

        res_drawables.extend([res_title, nn_layer, arr_in, txt_x, arr_out, txt_fx, skip_curve, txt_skip, add_node, add_sign, arr_final, txt_final, res_note])

        # ---------------------------------------------------------
        # SECTION 4: Layer Normalization
        # ---------------------------------------------------------
        make_eraser(res_drawables, start_time=ln_def_start - 1.2)
        ln_drawables =[]

        ln_title = make_title("Layer Normalization", y=140, color=PURPLE)
        ln_sub = make_body("The Great Mathematical Stabilizer", y=260, color=DARK_GRAY, font_size=56)

        # Unbalanced input
        bad_array = make_body("[ -452.1,  8900.5,  12.4 ]", x=400, y=480, font_size=64, color=RED)
        bad_label = make_body("Wild, Unbalanced Data", x=400, y=580, font_size=42, color=RED)
        
        arr_norm_in = Arrow(start_point=(750, 480), end_point=(900, 480), stroke_style=box_stroke)

        # LN Box
        ln_box = FlowchartProcess("Layer Norm\n(Mean=0, Std=1)", top_left=(900, 380), width=350, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=box_stroke)

        arr_norm_out = Arrow(start_point=(1250, 480), end_point=(1400, 480), stroke_style=box_stroke)

        # Balanced output
        good_array = make_body("[ -1.21,  1.52,  0.34 ]", x=1650, y=480, font_size=64, color=GREEN)
        good_label = make_body("Stable, Centered Data", x=1650, y=580, font_size=42, color=GREEN)

        ln_note = make_body("Stops the numbers from exploding. Keeps learning stable.", y=850, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=ln_def_start + 0.5, duration=1.0), drawable=ln_title)
        scene.add(SketchAnimation(start_time=ln_def_start + 7.5, duration=1.5), drawable=ln_sub)

        scene.add(SketchAnimation(start_time=ln_vis_start + 0.5, duration=1.0), drawable=bad_array)
        scene.add(SketchAnimation(start_time=ln_vis_start + 1.0, duration=0.8), drawable=bad_label)
        scene.add(SketchAnimation(start_time=ln_vis_start + 2.0, duration=0.5), drawable=arr_norm_in)
        
        scene.add(SketchAnimation(start_time=ln_vis_start + 2.5, duration=1.5), drawable=ln_box)
        
        scene.add(SketchAnimation(start_time=ln_vis_start + 11.0, duration=0.5), drawable=arr_norm_out)
        scene.add(SketchAnimation(start_time=ln_vis_start + 11.5, duration=1.0), drawable=good_array)
        scene.add(SketchAnimation(start_time=ln_vis_start + 12.0, duration=0.8), drawable=good_label)

        scene.add(SketchAnimation(start_time=ln_vis_start + 15.0, duration=1.5), drawable=ln_note)

        ln_drawables.extend([ln_title, ln_sub, bad_array, bad_label, arr_norm_in, ln_box, arr_norm_out, good_array, good_label, ln_note])

        # ---------------------------------------------------------
        # SECTION 5: The "Add & Norm" Block
        # ---------------------------------------------------------
        make_eraser(ln_drawables, start_time=add_norm_start - 1.2)
        an_drawables =[]

        an_title = make_title("The Famous 'Add & Norm' Block", y=140, color=BLUE)

        # Transformer Block Boundary
        trans_bound = Rectangle(top_left=(560, 250), width=800, height=650, stroke_style=StrokeStyle(color=GRAY, width=4.0), sketch_style=SKETCH)
        
        # Self-Attention
        attn_box = FlowchartProcess("Self-Attention", top_left=(760, 350), width=400, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=box_stroke)
        arr_attn_in = Arrow(start_point=(960, 950), end_point=(960, 470), stroke_style=box_stroke)
        txt_input = make_body("Input", x=960, y=980, font_size=42)

        # Skip Connection Line
        add_arr_skip = LinearPath(points=[(960, 800), (600, 800), (600, 280), (910, 280)], stroke_style=StrokeStyle(color=GREEN, width=5.0))
        
        # Add & Norm Node
        arr_attn_out = Arrow(start_point=(960, 350), end_point=(960, 330), stroke_style=box_stroke)
        add_norm_box = FlowchartProcess("Add & Norm", top_left=(760, 220), width=400, height=110, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.4), stroke_style=StrokeStyle(color=PURPLE, width=4.0))

        # Output Arrow
        arr_an_out = Arrow(start_point=(960, 220), end_point=(960, 100), stroke_style=box_stroke)
        txt_to_ffn = make_body("To Feed Forward...", x=960, y=60, font_size=42)

        scene.add(SketchAnimation(start_time=add_norm_start + 0.5, duration=1.0), drawable=an_title)
        
        scene.add(SketchAnimation(start_time=add_norm_start + 1.5, duration=1.0), drawable=trans_bound)
        
        scene.add(SketchAnimation(start_time=add_norm_start + 2.5, duration=0.8), drawable=txt_input)
        scene.add(SketchAnimation(start_time=add_norm_start + 3.0, duration=1.0), drawable=arr_attn_in)
        scene.add(SketchAnimation(start_time=add_norm_start + 4.0, duration=1.5), drawable=attn_box)
        
        scene.add(SketchAnimation(start_time=add_norm_start + 6.0, duration=1.5), drawable=add_arr_skip)
        
        scene.add(SketchAnimation(start_time=add_norm_start + 7.5, duration=0.5), drawable=arr_attn_out)
        scene.add(SketchAnimation(start_time=add_norm_start + 8.0, duration=1.5), drawable=add_norm_box)

        scene.add(SketchAnimation(start_time=add_norm_start + 11.0, duration=0.8), drawable=arr_an_out)
        scene.add(SketchAnimation(start_time=add_norm_start + 12.0, duration=0.8), drawable=txt_to_ffn)

        an_drawables.extend([an_title, trans_bound, txt_input, arr_attn_in, attn_box, add_arr_skip, arr_attn_out, add_norm_box, arr_an_out, txt_to_ffn])

        # ---------------------------------------------------------
        # SECTION 6: Outro
        # ---------------------------------------------------------
        make_eraser(an_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You now understand the glue of modern AI architectures.", y=600, color=BLACK)

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