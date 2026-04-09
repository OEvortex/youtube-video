


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

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, FlowchartProcess, Math
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GREEN, ORANGE, PURPLE, RED, WHITE,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_ORANGE, PASTEL_PURPLE
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "muon_optimizer"
AUDIO_PATH = OUTPUT_DIR / "muon_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "muon_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Have you heard of the Muon optimizer? It is a brand new algorithm that is setting speed records in training Large Language Models. "
    "<bookmark mark='problem'/> Traditionally, optimizers like AdamW treat all parameters the same. But neural networks contain massive 2D weight matrices in their hidden layers. "
    "<bookmark mark='muon_core'/> Muon, which stands for Momentum Orthogonalized by Newton-Schulz, treats these 2D matrices differently. "
    "<bookmark mark='orthogonal'/> Instead of a standard update, it applies a Newton-Schulz iteration. This forces the momentum update to become orthogonal, making each training step highly efficient. "
    "<bookmark mark='hybrid'/> In practice, it is a hybrid approach. You use Muon strictly for the heavy 2D hidden weights, and keep standard AdamW for the 1D biases and embeddings. "
    "<bookmark mark='outro'/> By perfectly tuning updates for matrices, Muon trains models faster and cheaper. Thanks for watching!"
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
        problem_start = tracker.bookmark_time("problem")
        muon_core_start = tracker.bookmark_time("muon_core")
        orthogonal_start = tracker.bookmark_time("orthogonal")
        hybrid_start = tracker.bookmark_time("hybrid")
        outro_start = tracker.bookmark_time("outro")

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("The Muon Optimizer", y=400, color=BLUE)
        intro_sub = make_body("Momentum Orthogonalized by Newton-Schulz", y=550, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        intro_drawables = [intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: The Problem
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=problem_start - 1.0)
        
        prob_title = make_title("The Parameter Problem", y=150, color=RED)
        
        layer_box = Rectangle(top_left=(710, 300), width=500, height=350, stroke_style=StrokeStyle(color=ORANGE, width=3), fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.2), sketch_style=SKETCH)
        w_math = Math(r"Weight Matrix $W$ (2D)", position=(960, 400), font_size=56, stroke_style=StrokeStyle(color=BLACK, width=2))
        b_math = Math(r"Bias Vector $b$ (1D)", position=(960, 550), font_size=56, stroke_style=StrokeStyle(color=BLACK, width=2))
        
        adam_label = make_body("AdamW usually optimizes BOTH exactly the same way.", y=800, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=problem_start + 0.5, duration=1.0), drawable=prob_title)
        scene.add(SketchAnimation(start_time=problem_start + 1.5, duration=1.0), drawable=layer_box)
        scene.add(SketchAnimation(start_time=problem_start + 2.5, duration=1.0), drawable=w_math)
        scene.add(SketchAnimation(start_time=problem_start + 3.0, duration=1.0), drawable=b_math)
        scene.add(SketchAnimation(start_time=problem_start + 4.5, duration=1.5), drawable=adam_label)

        prob_drawables =[prob_title, layer_box, w_math, b_math, adam_label]

        # ---------------------------------------------------------
        # SECTION 3: Muon Core & Orthogonalization
        # ---------------------------------------------------------
        make_eraser(prob_drawables, scene, start_time=muon_core_start - 1.0)
        
        core_title = make_title("Momentum Orthogonalization", y=120, color=BLUE)

        m_math = Math(r"1. Momentum: $M_t = \mu M_{t-1} + \nabla L$", position=(960, 280), font_size=64, stroke_style=StrokeStyle(color=BLACK, width=2))
        ns_math = Math(r"2. Newton-Schulz: $O_t = \mathrm{NS}(M_t)$", position=(960, 430), font_size=64, stroke_style=StrokeStyle(color=BLUE, width=3))
        update_math = Math(r"3. Update: $W_t = W_{t-1} - \eta O_t$", position=(960, 580), font_size=64, stroke_style=StrokeStyle(color=GREEN, width=3))

        scene.add(SketchAnimation(start_time=muon_core_start + 0.5, duration=1.0), drawable=core_title)
        scene.add(SketchAnimation(start_time=muon_core_start + 2.0, duration=1.5), drawable=m_math)
        
        scene.add(SketchAnimation(start_time=orthogonal_start + 0.5, duration=1.5), drawable=ns_math)
        scene.add(SketchAnimation(start_time=orthogonal_start + 4.0, duration=1.5), drawable=update_math)

        # Vector Visuals
        arr1 = Arrow(start_point=(400, 950), end_point=(500, 800), stroke_style=StrokeStyle(color=RED, width=5), sketch_style=SKETCH)
        arr2 = Arrow(start_point=(400, 950), end_point=(580, 890), stroke_style=StrokeStyle(color=RED, width=5), sketch_style=SKETCH)
        messy_label = make_body("Standard Update", x=490, y=1020, font_size=40, color=RED)

        arrow_transform = Arrow(start_point=(750, 880), end_point=(900, 880), stroke_style=StrokeStyle(color=BLACK, width=5), sketch_style=SKETCH)

        arr3 = Arrow(start_point=(1200, 950), end_point=(1200, 750), stroke_style=StrokeStyle(color=GREEN, width=5), sketch_style=SKETCH)
        arr4 = Arrow(start_point=(1200, 950), end_point=(1400, 950), stroke_style=StrokeStyle(color=GREEN, width=5), sketch_style=SKETCH)
        orth_label = make_body("Orthogonal Update", x=1300, y=1020, font_size=40, color=GREEN)

        scene.add(SketchAnimation(start_time=orthogonal_start + 5.5, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=orthogonal_start + 5.5, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=orthogonal_start + 6.0, duration=0.5), drawable=messy_label)

        scene.add(SketchAnimation(start_time=orthogonal_start + 6.5, duration=0.5), drawable=arrow_transform)

        scene.add(SketchAnimation(start_time=orthogonal_start + 7.0, duration=0.8), drawable=arr3)
        scene.add(SketchAnimation(start_time=orthogonal_start + 7.0, duration=0.8), drawable=arr4)
        scene.add(SketchAnimation(start_time=orthogonal_start + 7.5, duration=0.5), drawable=orth_label)

        orth_drawables =[core_title, m_math, ns_math, update_math, arr1, arr2, messy_label, arrow_transform, arr3, arr4, orth_label]

        # ---------------------------------------------------------
        # SECTION 4: Hybrid Optimization
        # ---------------------------------------------------------
        make_eraser(orth_drawables, scene, start_time=hybrid_start - 1.0)
        
        hybrid_title = make_title("Hybrid Optimization Strategy", y=150, color=BLACK)

        box_muon = FlowchartProcess("Muon\n(2D Hidden Weights)", top_left=(300, 400), width=550, height=200, font_size=56, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=StrokeStyle(color=BLUE, width=3), sketch_style=SKETCH)
        box_adam = FlowchartProcess("AdamW\n(1D Biases & Embeddings)", top_left=(1050, 400), width=550, height=200, font_size=56, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=StrokeStyle(color=GREEN, width=3), sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=hybrid_start + 0.5, duration=1.0), drawable=hybrid_title)
        scene.add(SketchAnimation(start_time=hybrid_start + 2.0, duration=1.5), drawable=box_muon)
        scene.add(SketchAnimation(start_time=hybrid_start + 4.5, duration=1.5), drawable=box_adam)

        hybrid_drawables =[hybrid_title, box_muon, box_adam]

        # ---------------------------------------------------------
        # SECTION 5: Outro
        # ---------------------------------------------------------
        make_eraser(hybrid_drawables, scene, start_time=outro_start - 1.0)
        
        outro_title = make_title("Why use Muon?", y=200, color=BLACK)
        
        b1 = FlowchartProcess("Trains LLMs Faster\n(e.g., Moonlight MoE)", top_left=(300, 400), width=550, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=StrokeStyle(color=ORANGE, width=3), sketch_style=SKETCH)
        b2 = FlowchartProcess("NanoGPT & CIFAR-10\nSpeed Records", top_left=(1050, 400), width=550, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=StrokeStyle(color=PURPLE, width=3), sketch_style=SKETCH)
        
        outro_text = make_body("Thanks for watching!", y=800, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.0), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 1.5, duration=1.5), drawable=b1)
        scene.add(SketchAnimation(start_time=outro_start + 2.5, duration=1.5), drawable=b2)
        scene.add(SketchAnimation(start_time=tracker.end_time - 2.5, duration=1.5), drawable=outro_text)

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