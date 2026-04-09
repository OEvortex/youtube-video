import asyncio
import os
import re
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts or uv add --dev edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Circle, Curve, Ellipse, FlowchartProcess, LinearPath, Math, Table
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, ORANGE, RED, WHITE,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "optimizers"
AUDIO_PATH = OUTPUT_DIR / "optimizers_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "optimizers_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome! Today we explore the engines that power deep learning: Optimizers. We will compare three heavyweights: Stochastic Gradient Descent, RMSprop, and Adam. "
    "<bookmark mark='sgd'/> Let's start with Stochastic Gradient Descent, or SGD. Imagine navigating a hilly landscape blindfolded. You feel the slope and take a step downhill. "
    "<bookmark mark='sgd_path'/> SGD calculates the gradient on a mini-batch of data. But in narrow ravines, SGD bounces back and forth erratically, making very slow progress toward the minimum. "
    "<bookmark mark='rmsprop'/> To fix this, researchers introduced RMSprop. Instead of a single global learning rate, RMSprop adapts the step size for every single parameter. "
    "<bookmark mark='rmsprop_path'/> It divides the learning rate by a moving average of squared gradients. This dampens the steep oscillations and accelerates progress along flat directions, smoothing out the journey. "
    "<bookmark mark='adam'/> Finally, we have Adam, which stands for Adaptive Moment Estimation. Adam combines the best of both worlds. "
    "<bookmark mark='adam_path'/> It uses the adaptive learning rates from RMSprop, and adds Momentum, which remembers previous steps to build up speed in consistent directions. This allows Adam to glide smoothly and quickly to the minimum. "
    "<bookmark mark='summary'/> In summary: SGD is simple but can be slow. RMSprop is great at taming erratic gradients. Adam combines momentum and adaptability, making it the robust, go-to default for modern AI. Thanks for watching!"
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


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()

def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        intro_start = tracker.bookmark_time("intro")
        sgd_start = tracker.bookmark_time("sgd")
        sgd_path_start = tracker.bookmark_time("sgd_path")
        rmsprop_start = tracker.bookmark_time("rmsprop")
        rmsprop_path_start = tracker.bookmark_time("rmsprop_path")
        adam_start = tracker.bookmark_time("adam")
        adam_path_start = tracker.bookmark_time("adam_path")
        summary_start = tracker.bookmark_time("summary")

        # ---------------------------------------------------------
        # SECTION 1: Intro (The Three Optimizers)
        # ---------------------------------------------------------
        intro_title = make_title("Optimizers: SGD, RMSprop & Adam", y=200, color=BLACK)
        
        sgd_box = FlowchartProcess("SGD\n(Stochastic\nGradient Descent)", top_left=(260, 450), width=350, height=200, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=StrokeStyle(color=BLUE, width=3), sketch_style=SKETCH)
        rms_box = FlowchartProcess("RMSprop\n(Root Mean Square\nPropagation)", top_left=(785, 450), width=350, height=200, font_size=42, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=StrokeStyle(color=GREEN, width=3), sketch_style=SKETCH)
        adam_box = FlowchartProcess("Adam\n(Adaptive Moment\nEstimation)", top_left=(1310, 450), width=350, height=200, font_size=42, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=StrokeStyle(color=RED, width=3), sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.0, duration=1.0), drawable=sgd_box)
        scene.add(SketchAnimation(start_time=intro_start + 3.0, duration=1.0), drawable=rms_box)
        scene.add(SketchAnimation(start_time=intro_start + 4.0, duration=1.0), drawable=adam_box)
        
        intro_drawables =[intro_title, sgd_box, rms_box, adam_box]

        # ---------------------------------------------------------
        # SECTION 2: Loss Landscape & Paths
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=sgd_start - 1.2)
        
        landscape_title = make_title("Loss Landscape (Ravine)", y=100, color=BLACK)
        
        e1 = Ellipse(center=(960, 750), width=1200, height=400, stroke_style=StrokeStyle(color=LIGHT_GRAY, width=3), sketch_style=SKETCH)
        e2 = Ellipse(center=(960, 750), width=700, height=220, stroke_style=StrokeStyle(color=GRAY, width=3), sketch_style=SKETCH)
        e3 = Ellipse(center=(960, 750), width=250, height=80, stroke_style=StrokeStyle(color=DARK_GRAY, width=3), sketch_style=SKETCH)
        target = Circle(center=(960, 750), radius=12, fill_style=FillStyle(color=BLACK), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=sgd_start + 0.5, duration=1.0), drawable=landscape_title)
        scene.add(SketchAnimation(start_time=sgd_start + 1.0, duration=1.0), drawable=e1)
        scene.add(SketchAnimation(start_time=sgd_start + 1.3, duration=0.8), drawable=e2)
        scene.add(SketchAnimation(start_time=sgd_start + 1.6, duration=0.6), drawable=e3)
        scene.add(SketchAnimation(start_time=sgd_start + 2.0, duration=0.5), drawable=target)
        
        # SGD
        sgd_math = Math(r"SGD: $w \leftarrow w - \alpha \nabla L$", position=(960, 200), font_size=56, stroke_style=StrokeStyle(color=BLUE, width=3))
        sgd_path = LinearPath(
            points=[(400, 600), (480, 920), (580, 630), (680, 880), (780, 680), (860, 820), (920, 720), (960, 750)],
            stroke_style=StrokeStyle(color=BLUE, width=5),
            sketch_style=SKETCH,
            glow_dot_hint={"color": BLUE, "radius": 15}
        )
        
        scene.add(SketchAnimation(start_time=sgd_start + 2.5, duration=1.5), drawable=sgd_math)
        scene.add(SketchAnimation(start_time=sgd_path_start + 0.5, duration=3.5), drawable=sgd_path)

        # RMSprop
        rms_math = Math(r"RMSprop: $w \leftarrow w - \frac{\alpha}{\sqrt{v}} \nabla L$", position=(960, 300), font_size=56, stroke_style=StrokeStyle(color=GREEN, width=3))
        rms_path = Curve(
            points=[(400, 600), (550, 710), (700, 800), (850, 770), (960, 750)],
            stroke_style=StrokeStyle(color=GREEN, width=5),
            sketch_style=SKETCH,
            glow_dot_hint={"color": GREEN, "radius": 15}
        )

        scene.add(SketchAnimation(start_time=rmsprop_start + 0.5, duration=1.5), drawable=rms_math)
        scene.add(SketchAnimation(start_time=rmsprop_path_start + 0.5, duration=3.0), drawable=rms_path)

        # Adam
        adam_math = Math(r"Adam: $w \leftarrow w - \frac{\alpha}{\sqrt{v}} m$", position=(960, 400), font_size=56, stroke_style=StrokeStyle(color=RED, width=3))
        adam_path = Curve(
            points=[(400, 600), (600, 780), (850, 850), (1050, 720), (960, 750)],
            stroke_style=StrokeStyle(color=RED, width=5),
            sketch_style=SKETCH,
            glow_dot_hint={"color": RED, "radius": 15}
        )

        scene.add(SketchAnimation(start_time=adam_start + 0.5, duration=1.5), drawable=adam_math)
        scene.add(SketchAnimation(start_time=adam_path_start + 0.5, duration=3.0), drawable=adam_path)

        landscape_drawables =[landscape_title, e1, e2, e3, target, sgd_math, sgd_path, rms_math, rms_path, adam_math, adam_path]

        # ---------------------------------------------------------
        # SECTION 3: Summary Table
        # ---------------------------------------------------------
        make_eraser(landscape_drawables, scene, start_time=summary_start - 1.2)
        
        sum_title = make_title("Summary", y=150, color=BLACK)
        
        sum_table = Table(
            data=[
                ["Optimizer", "Key Mechanism", "Best Use Case"],
                ["SGD", "Constant Learning Rate", "Fine-tuning / Flat Minima"],["RMSprop", "Adaptive Learning Rate", "RNNs / Erratic Gradients"],["Adam", "Momentum + Adaptive LR", "Default for Deep Learning"]
            ],
            top_left=(200, 350),
            col_widths=[350, 550, 600],
            row_heights=[100, 120, 120, 120],
            font_size=46,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=StrokeStyle(color=BLACK, width=3.0),
            sketch_style=SKETCH
        )
        
        outro_text = make_body("Thanks for watching!", y=950, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 1.5, duration=3.0), drawable=sum_table)
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