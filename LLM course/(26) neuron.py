


import asyncio
import math
import os
import re
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts or uv add --dev edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import ReplacementTransform, SketchAnimation
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, Math, Table
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "neuron"
AUDIO_PATH = OUTPUT_DIR / "neuron_deep_dive_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "neuron_deep_dive_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome! Today we are exploring the fundamental building block of all deep learning: the artificial neuron, also known as a perceptron. "
    "<bookmark mark='structure'/> Let's look inside. A neuron takes in data, called inputs, represented as x1, x2, and x3. "
    "<bookmark mark='weights'/> Each input is multiplied by a 'weight', which determines how important that input is. "
    "<bookmark mark='bias'/> We also add a 'bias' term, which shifts the result up or down independently of the inputs. "
    "<bookmark mark='math'/> The neuron computes the weighted sum of all inputs plus the bias. Let's call this sum 'z'. "
    "<bookmark mark='activation_intro'/> But if we stop here, our network is just a linear model. To solve complex problems, we pass 'z' through an Activation Function. "
    "<bookmark mark='sigmoid'/> First is the Sigmoid function. It squashes any input into a value between 0 and 1, forming an 'S' shaped curve. It's great for predicting probabilities. "
    "<bookmark mark='tanh'/> Next is Tanh. It's similar to Sigmoid, but it squashes values between negative 1 and 1, which helps center the data around zero. "
    "<bookmark mark='relu'/> Finally, we have ReLU, or Rectified Linear Unit. It simply outputs zero if the input is negative, and outputs the raw value if it's positive. "
    "<bookmark mark='relu_modern'/> Despite being so simple, ReLU is the standard activation function in modern neural networks because it trains incredibly fast and prevents vanishing gradients. "
    "<bookmark mark='outro'/> To summarize: weights and biases calculate the signal, and activation functions decide if the neuron fires. Thanks for watching!"
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

def make_eraser(objects_to_erase: list, scene: Scene, *, start_time: float, duration: float = 1.2) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)

def make_axes(y_origin: float) -> tuple[Line, Line]:
    x_axis = Line(start=(460, y_origin), end=(1460, y_origin), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
    y_axis = Line(start=(960, 850), end=(960, 250), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
    return x_axis, y_axis

def make_sigmoid_curve() -> Curve:
    pts =[]
    for x in range(460, 1461, 10):
        val = (x - 960) / 100
        y = 750 - 300 * (1 / (1 + math.exp(-val)))
        pts.append((x, y))
    return Curve(points=pts, stroke_style=StrokeStyle(color=BLUE, width=6), sketch_style=SKETCH)

def make_tanh_curve() -> Curve:
    pts =[]
    for x in range(460, 1461, 10):
        val = (x - 960) / 100
        y = 600 - 150 * math.tanh(val)
        pts.append((x, y))
    return Curve(points=pts, stroke_style=StrokeStyle(color=RED, width=6), sketch_style=SKETCH)

def make_relu_curve() -> Curve:
    pts =[]
    for x in range(460, 1461, 10):
        val = (x - 960) / 100
        y = 750 - 100 * max(0, val)
        pts.append((x, y))
    return Curve(points=pts, stroke_style=StrokeStyle(color=GREEN, width=6), sketch_style=SKETCH)


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()

def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        intro_start = tracker.bookmark_time("intro")
        structure_start = tracker.bookmark_time("structure")
        weights_start = tracker.bookmark_time("weights")
        bias_start = tracker.bookmark_time("bias")
        math_start = tracker.bookmark_time("math")
        act_intro_start = tracker.bookmark_time("activation_intro")
        sigmoid_start = tracker.bookmark_time("sigmoid")
        tanh_start = tracker.bookmark_time("tanh")
        relu_start = tracker.bookmark_time("relu")
        relu_modern_start = tracker.bookmark_time("relu_modern")
        outro_start = tracker.bookmark_time("outro")

        stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro & Neuron Structure
        # ---------------------------------------------------------
        intro_title = make_title("The Artificial Neuron", y=120, color=BLUE)
        
        # Inputs
        x1 = Circle(center=(300, 350), radius=50, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        x2 = Circle(center=(300, 550), radius=50, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        x3 = Circle(center=(300, 750), radius=50, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        
        x1_t = Math(r"$x_1$", position=(300, 350), font_size=56, stroke_style=StrokeStyle(color=BLACK, width=2))
        x2_t = Math(r"$x_2$", position=(300, 550), font_size=56, stroke_style=StrokeStyle(color=BLACK, width=2))
        x3_t = Math(r"$x_3$", position=(300, 750), font_size=56, stroke_style=StrokeStyle(color=BLACK, width=2))
        
        # Neuron body
        neuron = Circle(center=(960, 550), radius=180, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), sketch_style=SKETCH)
        neuron_t = Math(r"$\Sigma$", position=(960, 550), font_size=120, stroke_style=StrokeStyle(color=DARK_GRAY, width=3))

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        
        scene.add(SketchAnimation(start_time=structure_start + 0.5, duration=1.0), drawable=neuron)
        scene.add(SketchAnimation(start_time=structure_start + 1.0, duration=0.8), drawable=neuron_t)
        
        scene.add(SketchAnimation(start_time=structure_start + 2.5, duration=0.8), drawable=x1)
        scene.add(SketchAnimation(start_time=structure_start + 2.5, duration=0.5), drawable=x1_t)
        scene.add(SketchAnimation(start_time=structure_start + 3.0, duration=0.8), drawable=x2)
        scene.add(SketchAnimation(start_time=structure_start + 3.0, duration=0.5), drawable=x2_t)
        scene.add(SketchAnimation(start_time=structure_start + 3.5, duration=0.8), drawable=x3)
        scene.add(SketchAnimation(start_time=structure_start + 3.5, duration=0.5), drawable=x3_t)

        # Weights
        a1 = Arrow(start_point=(360, 370), end_point=(790, 500), stroke_style=stroke)
        a2 = Arrow(start_point=(360, 550), end_point=(780, 550), stroke_style=stroke)
        a3 = Arrow(start_point=(360, 730), end_point=(790, 600), stroke_style=stroke)
        
        w1_t = Math(r"$w_1$", position=(550, 380), font_size=48, stroke_style=StrokeStyle(color=ORANGE, width=2))
        w2_t = Math(r"$w_2$", position=(550, 500), font_size=48, stroke_style=StrokeStyle(color=ORANGE, width=2))
        w3_t = Math(r"$w_3$", position=(550, 700), font_size=48, stroke_style=StrokeStyle(color=ORANGE, width=2))

        scene.add(SketchAnimation(start_time=weights_start + 0.5, duration=0.8), drawable=a1)
        scene.add(SketchAnimation(start_time=weights_start + 0.8, duration=0.5), drawable=w1_t)
        scene.add(SketchAnimation(start_time=weights_start + 1.0, duration=0.8), drawable=a2)
        scene.add(SketchAnimation(start_time=weights_start + 1.3, duration=0.5), drawable=w2_t)
        scene.add(SketchAnimation(start_time=weights_start + 1.5, duration=0.8), drawable=a3)
        scene.add(SketchAnimation(start_time=weights_start + 1.8, duration=0.5), drawable=w3_t)

        # Bias
        b_arr = Arrow(start_point=(960, 200), end_point=(960, 370), stroke_style=stroke)
        b_t = Math(r"$+b$", position=(960, 150), font_size=64, stroke_style=StrokeStyle(color=RED, width=3))

        scene.add(SketchAnimation(start_time=bias_start + 0.5, duration=1.0), drawable=b_arr)
        scene.add(SketchAnimation(start_time=bias_start + 1.2, duration=1.0), drawable=b_t)

        # Math Equation
        eq_z = Math(r"$z = w_1 x_1 + w_2 x_2 + w_3 x_3 + b$", position=(960, 850), font_size=72, stroke_style=StrokeStyle(color=BLUE, width=3))
        scene.add(SketchAnimation(start_time=math_start + 0.5, duration=2.5), drawable=eq_z)

        # Activation Intro
        out_arr = Arrow(start_point=(1140, 550), end_point=(1400, 550), stroke_style=stroke)
        act_eq = Math(r"$y = f(z)$", position=(1550, 550), font_size=72, stroke_style=StrokeStyle(color=PURPLE, width=3))
        
        scene.add(SketchAnimation(start_time=act_intro_start + 4.0, duration=1.0), drawable=out_arr)
        scene.add(SketchAnimation(start_time=act_intro_start + 5.0, duration=1.5), drawable=act_eq)

        neuron_group =[
            intro_title, x1, x2, x3, x1_t, x2_t, x3_t, neuron, neuron_t,
            a1, a2, a3, w1_t, w2_t, w3_t, b_arr, b_t, eq_z, out_arr, act_eq
        ]

        # ---------------------------------------------------------
        # SECTION 2: Activation Functions (Graphs)
        # ---------------------------------------------------------
        make_eraser(neuron_group, scene, start_time=sigmoid_start - 1.5)

        # Sigmoid
        sig_title = make_title("Sigmoid Function", y=150, color=BLUE)
        sig_math = Math(r"$\sigma(x) = \frac{1}{1 + e^{-x}}$", position=(960, 950), font_size=72, stroke_style=StrokeStyle(color=BLUE, width=2))
        x_axis_sig, y_axis_sig = make_axes(750)
        sig_curve = make_sigmoid_curve()
        
        scene.add(SketchAnimation(start_time=sigmoid_start + 0.5, duration=1.0), drawable=sig_title)
        scene.add(SketchAnimation(start_time=sigmoid_start + 2.0, duration=1.0), drawable=x_axis_sig)
        scene.add(SketchAnimation(start_time=sigmoid_start + 2.5, duration=1.0), drawable=y_axis_sig)
        scene.add(SketchAnimation(start_time=sigmoid_start + 3.5, duration=2.0), drawable=sig_curve)
        scene.add(SketchAnimation(start_time=sigmoid_start + 4.5, duration=1.5), drawable=sig_math)

        # Tanh
        tanh_title = make_title("Tanh Function", y=150, color=RED)
        tanh_math = Math(r"$\tanh(x)$", position=(960, 950), font_size=72, stroke_style=StrokeStyle(color=RED, width=2))
        x_axis_tanh, y_axis_tanh = make_axes(600)
        tanh_curve = make_tanh_curve()

        scene.add(
            ReplacementTransform(target_drawable=tanh_title, start_time=tanh_start + 0.5, duration=1.0),
            drawable=sig_title,
        )
        scene.add(
            ReplacementTransform(target_drawable=x_axis_tanh, start_time=tanh_start + 1.0, duration=1.0),
            drawable=x_axis_sig,
        )
        scene.add(
            ReplacementTransform(target_drawable=y_axis_tanh, start_time=tanh_start + 1.0, duration=1.0),
            drawable=y_axis_sig,
        )
        scene.add(
            ReplacementTransform(target_drawable=tanh_curve, start_time=tanh_start + 1.0, duration=1.5),
            drawable=sig_curve,
        )
        scene.add(
            ReplacementTransform(target_drawable=tanh_math, start_time=tanh_start + 1.5, duration=1.0),
            drawable=sig_math,
        )

        # ReLU
        relu_title = make_title("ReLU Function", y=150, color=GREEN)
        relu_math = Math(r"$\max(0, x)$", position=(960, 950), font_size=72, stroke_style=StrokeStyle(color=GREEN, width=2))
        x_axis_relu, y_axis_relu = make_axes(750)
        relu_curve = make_relu_curve()

        scene.add(
            ReplacementTransform(target_drawable=relu_title, start_time=relu_start + 0.5, duration=1.0),
            drawable=tanh_title,
        )
        scene.add(
            ReplacementTransform(target_drawable=x_axis_relu, start_time=relu_start + 1.0, duration=1.0),
            drawable=x_axis_tanh,
        )
        scene.add(
            ReplacementTransform(target_drawable=y_axis_relu, start_time=relu_start + 1.0, duration=1.0),
            drawable=y_axis_tanh,
        )
        scene.add(
            ReplacementTransform(target_drawable=relu_curve, start_time=relu_start + 1.0, duration=1.5),
            drawable=tanh_curve,
        )
        scene.add(
            ReplacementTransform(target_drawable=relu_math, start_time=relu_start + 1.5, duration=1.0),
            drawable=tanh_math,
        )

        relu_modern_label = make_body("Fast Training & No Vanishing Gradients!", y=250, color=ORANGE, font_size=48)
        scene.add(SketchAnimation(start_time=relu_modern_start + 2.0, duration=1.5), drawable=relu_modern_label)

        graphs_group =[relu_title, x_axis_relu, y_axis_relu, relu_curve, relu_math, relu_modern_label]

        # ---------------------------------------------------------
        # SECTION 3: Outro
        # ---------------------------------------------------------
        make_eraser(graphs_group, scene, start_time=outro_start - 1.5)

        outro_title = make_title("Summary", y=200, color=BLACK)
        
        sum_box1 = FlowchartProcess("Weights & Biases\n➔\nCalculate the Signal", top_left=(300, 450), width=600, height=250, font_size=56, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        sum_box2 = FlowchartProcess("Activation Function\n➔\nDecides if Neuron Fires", top_left=(1020, 450), width=600, height=250, font_size=56, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=stroke)
        
        outro_text = make_body("Thanks for watching!", y=850, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.0), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 1.5, duration=1.5), drawable=sum_box1)
        scene.add(SketchAnimation(start_time=outro_start + 3.0, duration=1.5), drawable=sum_box2)
        scene.add(SketchAnimation(start_time=tracker.end_time - 3.0, duration=1.5), drawable=outro_text)

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