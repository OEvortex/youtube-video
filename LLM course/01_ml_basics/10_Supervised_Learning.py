import os
import asyncio
import re
import math
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("Please install edge-tts: pip install edge-tts")
    exit()

from handanim.animations import (
    SketchAnimation,
    FadeInAnimation,
    FadeOutAnimation,
    TransformAnimation,
    TranslateToAnimation,
)
from handanim.core import (
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
)
from handanim.core.styles import StrokePressure
from handanim.primitives import (
    Arrow,
    Circle,
    Line,
    LinearPath,
    Math,
    Rectangle,
    Text,
    Eraser,
)
from handanim.core import DrawableGroup
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
HEIGHT = 1088
FONT_NAME = "cabin_sketch"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "supervised_learning.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "supervised_learning.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> Supervised Learning is the most common form of machine learning. "
    "It is like learning with a teacher. We provide the model with input data and the correct answers, called labels. "
    "<bookmark mark='linear_start'/> The first major algorithm is Linear Regression. "
    "We use it when we want to predict a continuous number, like the price of a house based on its size. "
    "The goal is to find the 'Line of Best Fit' that minimizes the distance between the line and our data points. "
    "The formula is simple: Y equals weight times X plus bias. "
    "<bookmark mark='logistic_start'/> But what if we want to classify things? That is where Logistic Regression comes in. "
    "Despite the name, it is used for classification, like determining if an email is Spam or Not Spam. "
    "Instead of a straight line, it uses the Sigmoid function to squash any value into a probability between zero and one. "
    "If the probability is above point five, we classify it as one; otherwise, it is zero. "
    "<bookmark mark='outro'/> Whether predicting prices or classifying emails, these two algorithms are the foundation of supervised learning. "
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
    # 1. Synthesize Audio
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Setup Scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_linear = tracker.bookmark_time("linear_start")
        t_logistic = tracker.bookmark_time("logistic_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRO ---
        title = Text("Supervised Learning", position=(960, 400), font_size=120, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        subtitle = Text("Learning with Labeled Data", position=(960, 550), font_size=60, color=DARK_GRAY, font_name=FONT_NAME, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 2.0, duration=2.0), drawable=subtitle)
        
        # Mapping visual: X -> [Model] -> Y
        input_box = Rectangle(top_left=(400, 700), width=200, height=100, stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        input_txt = Text("Input (X)", position=(500, 750), font_size=40, font_name=FONT_NAME)
        arrow1 = Arrow(start_point=(600, 750), end_point=(850, 750), stroke_style=StrokeStyle(color=BLACK, width=3))
        model_box = Rectangle(top_left=(850, 650), width=220, height=200, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        model_txt = Text("Model", position=(960, 750), font_size=40, font_name=FONT_NAME)
        arrow2 = Arrow(start_point=(1070, 750), end_point=(1320, 750), stroke_style=StrokeStyle(color=BLACK, width=3))
        output_box = Rectangle(top_left=(1320, 700), width=200, height=100, stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        output_txt = Text("Label (Y)", position=(1420, 750), font_size=40, font_name=FONT_NAME)

        scene.add(SketchAnimation(start_time=t_intro + 4.5, duration=1.0), drawable=input_box)
        scene.add(SketchAnimation(start_time=t_intro + 4.5, duration=1.0), drawable=input_txt)
        scene.add(SketchAnimation(start_time=t_intro + 5.5, duration=0.5), drawable=arrow1)
        scene.add(SketchAnimation(start_time=t_intro + 6.0, duration=1.0), drawable=model_box)
        scene.add(SketchAnimation(start_time=t_intro + 6.0, duration=1.0), drawable=model_txt)
        scene.add(SketchAnimation(start_time=t_intro + 7.0, duration=0.5), drawable=arrow2)
        scene.add(SketchAnimation(start_time=t_intro + 7.5, duration=1.0), drawable=output_box)
        scene.add(SketchAnimation(start_time=t_intro + 7.5, duration=1.0), drawable=output_txt)

        # Erase Intro
        eraser_intro = Eraser(objects_to_erase=[title, subtitle, input_box, input_txt, arrow1, model_box, model_txt, arrow2, output_box, output_txt], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_linear - 1.0, duration=1.0), drawable=eraser_intro)

        # --- SECTION 2: LINEAR REGRESSION ---
        lin_title = Text("1. Linear Regression", position=(450, 150), font_size=80, color=RED, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Coordinate Plane
        xaxis = Line(start=(300, 850), end=(1000, 850), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        yaxis = Line(start=(400, 450), end=(400, 950), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        x_lbl = Text("Size", position=(1050, 850), font_size=30, font_name=FONT_NAME)
        y_lbl = Text("Price", position=(400, 420), font_size=30, font_name=FONT_NAME)

        # Scatter points
        points = [(450, 800), (520, 750), (600, 780), (680, 680), (750, 620), (820, 650), (900, 550)]
        dots = [Circle(center=p, radius=8, fill_style=FillStyle(color=BLUE)) for p in points]
        
        # Regression Line
        reg_line = Line(start=(400, 850), end=(950, 500), stroke_style=StrokeStyle(color=RED, width=6), sketch_style=SKETCH)
        
        # Formula
        lin_math = Math(r"$y = wx + b$", position=(1400, 550), font_size=120, color=RED)
        lin_desc = Text("Predicts Continuous Values", position=(1400, 700), font_size=50, font_name=FONT_NAME, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=t_linear, duration=1.5), drawable=lin_title)
        scene.add(SketchAnimation(start_time=t_linear + 1.5, duration=1.0), drawable=xaxis)
        scene.add(SketchAnimation(start_time=t_linear + 1.5, duration=1.0), drawable=yaxis)
        scene.add(SketchAnimation(start_time=t_linear + 2.5, duration=0.5), drawable=x_lbl)
        scene.add(SketchAnimation(start_time=t_linear + 2.5, duration=0.5), drawable=y_lbl)
        
        for i, dot in enumerate(dots):
            scene.add(SketchAnimation(start_time=t_linear + 3.5 + i*0.3, duration=0.5), drawable=dot)
            
        scene.add(SketchAnimation(start_time=t_linear + 6.5, duration=2.0), drawable=reg_line)
        scene.add(SketchAnimation(start_time=t_linear + 9.0, duration=2.0), drawable=lin_math)
        scene.add(SketchAnimation(start_time=t_linear + 11.0, duration=1.5), drawable=lin_desc)

        # Erase Linear
        eraser_linear = Eraser(objects_to_erase=[lin_title, xaxis, yaxis, x_lbl, y_lbl, reg_line, lin_math, lin_desc, *dots], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_logistic - 1.0, duration=1.0), drawable=eraser_linear)

        # --- SECTION 3: LOGISTIC REGRESSION ---
        log_title = Text("2. Logistic Regression", position=(450, 150), font_size=80, color=GREEN, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Sigmoid Graph
        lxaxis = Line(start=(300, 800), end=(1000, 800), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        lyaxis = Line(start=(650, 400), end=(650, 900), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        
        # Sigmoid curve points
        sig_pts = []
        for x_val in range(-300, 301, 10):
            # y = 1 / (1 + e^-x)
            # Map x_val to a smaller range for the curve
            norm_x = x_val / 50
            y_val = 1 / (1 + math.exp(-norm_x))
            # Map y_val (0 to 1) to screen coordinates (800 to 500)
            screen_y = 800 - (y_val * 300)
            sig_pts.append((650 + x_val, screen_y))
        
        sigmoid_curve = LinearPath(points=sig_pts, stroke_style=StrokeStyle(color=GREEN, width=5), sketch_style=SKETCH)
        
        # Threshold line
        thresh_line = Line(start=(350, 650), end=(950, 650), stroke_style=StrokeStyle(color=ORANGE, width=2, opacity=0.6), sketch_style=SKETCH)
        thresh_txt = Text("Threshold 0.5", position=(1100, 650), font_size=30, font_name=FONT_NAME, color=ORANGE)

        # Formula
        log_math = Math(r"$\sigma(z) = \frac{1}{1 + e^{-z}}$", position=(1450, 500), font_size=100, color=GREEN)
        log_desc = Text("Classification (0 or 1)", position=(1450, 650), font_size=50, font_name=FONT_NAME, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=t_logistic, duration=1.5), drawable=log_title)
        scene.add(SketchAnimation(start_time=t_logistic + 1.5, duration=1.0), drawable=lxaxis)
        scene.add(SketchAnimation(start_time=t_logistic + 1.5, duration=1.0), drawable=lyaxis)
        scene.add(SketchAnimation(start_time=t_logistic + 3.0, duration=3.0), drawable=sigmoid_curve)
        scene.add(SketchAnimation(start_time=t_logistic + 6.5, duration=1.0), drawable=thresh_line)
        scene.add(SketchAnimation(start_time=t_logistic + 7.0, duration=1.0), drawable=thresh_txt)
        scene.add(SketchAnimation(start_time=t_logistic + 9.0, duration=2.0), drawable=log_math)
        scene.add(SketchAnimation(start_time=t_logistic + 11.0, duration=1.5), drawable=log_desc)

        # Erase Logistic
        eraser_log = Eraser(objects_to_erase=[log_title, lxaxis, lyaxis, sigmoid_curve, thresh_line, thresh_txt, log_math, log_desc], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=eraser_log)

        # --- SECTION 4: OUTRO ---
        outro_msg = Text("The Foundations of AI", position=(960, 540), font_size=90, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=outro_msg)

    # 3. Render
    scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()