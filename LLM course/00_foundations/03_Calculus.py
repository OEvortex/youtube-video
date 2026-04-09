import asyncio
import os
import re
import math
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("Please install edge-tts: pip install edge-tts")
    exit()

from handanim.animations import (
    FadeInAnimation,
    SketchAnimation,
    TransformAnimation,
)
from handanim.core import (
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
)
from handanim.primitives import (
    Arrow,
    Circle,
    Line,
    Math,
    Rectangle,
    Text,
    LinearPath,
    Eraser,
)
from handanim.stylings.color import (
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    WHITE,
    GRAY,
    DARK_GRAY,
    PASTEL_BLUE,
    PASTEL_GREEN,
    PASTEL_ORANGE,
    PASTEL_RED,
)

# --- Configuration ---
WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "calculus_narration.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "calculus_whiteboard.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
FONT_NAME = "feasibly"
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> Calculus is the mathematical study of continuous change. "
    "While algebra gives us static snapshots, calculus provides the movie of how things move and evolve. "
    "<bookmark mark='derivative_start'/> We begin with the Derivative. "
    "Geometrically, it is the slope of a curve at a single point. "
    "Imagine a function like f of x equals x squared. "
    "The derivative, written as f prime, tells us the instantaneous rate of change. "
    "For x squared, the power rule tells us the derivative is simply two x. "
    "<bookmark mark='chain_start'/> But functions are often nested inside each other. "
    "This is where the Chain Rule becomes essential. "
    "It allows us to differentiate a function of a function, like f of g of x. "
    "We multiply the derivative of the outer function by the derivative of the inner function. "
    "In deep learning, the chain rule is the secret engine behind backpropagation. "
    "<bookmark mark='partial_start'/> Finally, when we deal with multiple dimensions, we use Partial Derivatives. "
    "Imagine a surface defined by x and y. "
    "A partial derivative with respect to x measures how the function changes as we move along x, "
    "while holding the variable y completely constant. "
    "This concept allows AI to optimize high-dimensional cost functions through gradient descent. "
    "<bookmark mark='outro'/> From simple slopes to complex optimization, calculus is the language of optimization. "
    "Thanks for watching."
)

BOOKMARK_RE = re.compile(r"<bookmark\s+(?:mark|name)\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

async def synthesize_narration(audio_path: str, text: str) -> None:
    if os.path.exists(audio_path):
        return
    communicate = edge_tts.Communicate(strip_bookmarks(text), VOICE, rate=VOICE_RATE)
    await communicate.save(audio_path)

def main():
    # 1. Synthesize audio
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Setup Scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_deriv = tracker.bookmark_time("derivative_start")
        t_chain = tracker.bookmark_time("chain_start")
        t_partial = tracker.bookmark_time("partial_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRO ---
        title = Text("Calculus", position=(960, 400), font_size=120, color=BLUE, sketch_style=SKETCH)
        subtitle = Text("The Mathematics of Change", position=(960, 550), font_size=60, color=DARK_GRAY, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 2.0, duration=2.0), drawable=subtitle)
        
        eraser_intro = Eraser(objects_to_erase=[title, subtitle], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_deriv - 1.0, duration=1.0), drawable=eraser_intro)

        # --- SECTION 2: DERIVATIVES ---
        d_title = Text("1. The Derivative", position=(400, 150), font_size=80, color=RED, sketch_style=SKETCH)
        
        # Parabola Graph
        xaxis = Line(start=(300, 800), end=(1000, 800), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        yaxis = Line(start=(650, 400), end=(650, 900), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        
        # Draw a simple x^2 curve
        points = []
        for x_val in range(-150, 151, 10):
            points.append((650 + x_val, 800 - (x_val**2 / 100)))
        parabola = LinearPath(points=points, stroke_style=StrokeStyle(color=BLUE, width=4), sketch_style=SKETCH)
        
        # Tangent line at x=100
        point_on_curve = (750, 700)
        tangent = Line(start=(700, 800), end=(800, 600), stroke_style=StrokeStyle(color=ORANGE, width=6), sketch_style=SKETCH)
        dot = Circle(center=point_on_curve, radius=10, fill_style=FillStyle(color=RED))
        
        # Formulas
        f_x = Math(r"$f(x) = x^2$", position=(1300, 450), font_size=90, color=BLUE)
        df_x = Math(r"$f'(x) = 2x$", position=(1300, 650), font_size=110, color=RED)
        
        scene.add(SketchAnimation(start_time=t_deriv, duration=1.5), drawable=d_title)
        scene.add(SketchAnimation(start_time=t_deriv + 1.0, duration=1.0), drawable=xaxis)
        scene.add(SketchAnimation(start_time=t_deriv + 1.0, duration=1.0), drawable=yaxis)
        scene.add(SketchAnimation(start_time=t_deriv + 2.0, duration=2.5), drawable=parabola)
        scene.add(SketchAnimation(start_time=t_deriv + 4.5, duration=1.0), drawable=dot)
        scene.add(SketchAnimation(start_time=t_deriv + 5.0, duration=1.5), drawable=tangent)
        scene.add(SketchAnimation(start_time=t_deriv + 7.0, duration=1.5), drawable=f_x)
        scene.add(SketchAnimation(start_time=t_deriv + 9.0, duration=1.5), drawable=df_x)

        eraser_deriv = Eraser(objects_to_erase=[d_title, xaxis, yaxis, parabola, tangent, dot, f_x, df_x], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_chain - 1.0, duration=1.0), drawable=eraser_deriv)

        # --- SECTION 3: CHAIN RULE ---
        c_title = Text("2. The Chain Rule", position=(400, 150), font_size=80, color=GREEN, sketch_style=SKETCH)
        composite = Math(r"$y = f(g(x))$", position=(960, 400), font_size=100, color=DARK_GRAY)
        
        chain_formula = Math(r"$\frac{dy}{dx} = f'(g(x)) \cdot g'(x)$", position=(960, 600), font_size=130, color=GREEN)
        ai_note = Text("Used in Neural Network Backpropagation", position=(960, 800), font_size=50, color=PASTEL_RED, sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=t_chain, duration=1.5), drawable=c_title)
        scene.add(SketchAnimation(start_time=t_chain + 2.0, duration=2.0), drawable=composite)
        scene.add(SketchAnimation(start_time=t_chain + 5.0, duration=3.0), drawable=chain_formula)
        scene.add(SketchAnimation(start_time=t_chain + 9.0, duration=2.0), drawable=ai_note)

        eraser_chain = Eraser(objects_to_erase=[c_title, composite, chain_formula, ai_note], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_partial - 1.0, duration=1.0), drawable=eraser_chain)

        # --- SECTION 4: PARTIAL DERIVATIVES ---
        p_title = Text("3. Partial Derivatives", position=(500, 150), font_size=80, color=PURPLE, sketch_style=SKETCH)
        surface_math = Math(r"$f(x, y)$", position=(400, 450), font_size=100)
        
        # Visualization of holding constant
        box_x = Rectangle(top_left=(800, 350), width=400, height=150, stroke_style=StrokeStyle(color=PURPLE, width=4), fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        txt_x = Text("Change x", position=(1000, 425), font_size=40)
        
        box_y = Rectangle(top_left=(800, 550), width=400, height=150, stroke_style=StrokeStyle(color=DARK_GRAY, width=4), fill_style=FillStyle(color=WHITE, opacity=0.5), sketch_style=SKETCH)
        txt_y = Text("y is constant", position=(1000, 625), font_size=40)
        
        partial_math = Math(r"$\frac{\partial f}{\partial x}$", position=(1450, 500), font_size=140, color=PURPLE)
        gradient_note = Text("Essential for Gradient Descent", position=(960, 850), font_size=54, color=ORANGE, sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=t_partial, duration=1.5), drawable=p_title)
        scene.add(SketchAnimation(start_time=t_partial + 2.0, duration=1.5), drawable=surface_math)
        scene.add(SketchAnimation(start_time=t_partial + 4.5, duration=1.5), drawable=box_x)
        scene.add(SketchAnimation(start_time=t_partial + 4.5, duration=1.5), drawable=txt_x)
        scene.add(SketchAnimation(start_time=t_partial + 7.0, duration=1.5), drawable=box_y)
        scene.add(SketchAnimation(start_time=t_partial + 7.0, duration=1.5), drawable=txt_y)
        scene.add(SketchAnimation(start_time=t_partial + 10.0, duration=2.5), drawable=partial_math)
        scene.add(SketchAnimation(start_time=t_partial + 13.0, duration=2.0), drawable=gradient_note)

        eraser_partial = Eraser(objects_to_erase=[p_title, surface_math, box_x, txt_x, box_y, txt_y, partial_math, gradient_note], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=eraser_partial)

        # --- SECTION 5: OUTRO ---
        outro_msg = Text("Calculus: The Language of Optimization", position=(960, 540), font_size=80, color=BLUE, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=outro_msg)

        # 3. Render
        scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()