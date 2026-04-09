"""
Whiteboard explainer: Python for AI (NumPy, Pandas, and Matplotlib)

This scene provides a detailed 5-minute animation covering the foundational
Python libraries for AI: NumPy for numerical computing, Pandas for data manipulation,
and Matplotlib for data visualization.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

# Ensure we can import edge_tts for narration
try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts)."
    raise SystemExit(msg) from exc

from handanim.animations import (
    FadeInAnimation,
    FadeOutAnimation,
    SketchAnimation,
    TransformAnimation,
)
from handanim.core import (
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
    DrawableGroup,
)
from handanim.primitives import (
    Arrow,
    Circle,
    Eraser,
    Line,
    LinearPath,
    Math,
    Rectangle,
    Table,
    Text,
)
from handanim.stylings.color import (
    BLACK,
    BLUE,
    CYAN,
    DARK_GRAY,
    GREEN,
    ORANGE,
    PASTEL_BLUE,
    PASTEL_GREEN,
    PASTEL_ORANGE,
    PURPLE,
    RED,
    WHITE,
)

# --- Configuration ---
WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "python_ai_narration.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "python_ai_whiteboard.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
FONT_NAME = "feasibly"  # Standard handanim handwriting font
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script with Bookmarks ---
NARRATION = (
    "<bookmark mark='intro'/> Python is the undisputed king of Artificial Intelligence. "
    "But Python alone isn't enough. Its true power comes from the 'Holy Trinity' of Data Science: "
    "NumPy, Pandas, and Matplotlib. Together, they form the toolkit of every AI engineer. "
    "<bookmark mark='numpy_start'/> We begin with NumPy, the foundation. "
    "Standard Python lists are slow. NumPy introduces the 'ndarray', which is a high-performance, "
    "C-based array structure. It allows for vectorization—performing math on entire blocks of data "
    "simultaneously without writing slow loops. In AI, weights and biases are almost always stored as NumPy arrays. "
    "<bookmark mark='pandas_start'/> Next is Pandas, the Swiss Army Knife of data manipulation. "
    "It takes the raw power of NumPy and wraps it in a user-friendly structure called the 'DataFrame'. "
    "Think of a DataFrame as an Excel spreadsheet on steroids. "
    "It allows you to clean messy data, handle missing values, and merge massive datasets with just a few lines of code. "
    "It is where 80 percent of an AI project's time is spent: preparing the data for the model. "
    "<bookmark mark='matplotlib_start'/> Finally, we have Matplotlib, the eyes of your project. "
    "Data in a table is hard to read. Matplotlib allows us to visualize trends, outliers, and distributions. "
    "From simple line plots to complex heatmaps, it helps us verify that our data is correct "
    "and that our AI model is actually learning. "
    "<bookmark mark='integration_start'/> In a real AI pipeline, these three work in perfect harmony. "
    "You use Pandas to load and clean your data, NumPy to convert it into mathematical tensors for the model, "
    "and Matplotlib to plot the training loss and accuracy. "
    "<bookmark mark='outro'/> Mastering these libraries is the first step toward building the future with AI. "
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
    # 1. Generate audio
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Construct the scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_numpy = tracker.bookmark_time("numpy_start")
        t_pandas = tracker.bookmark_time("pandas_start")
        t_plt = tracker.bookmark_time("matplotlib_start")
        t_integration = tracker.bookmark_time("integration_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRODUCTION ---
        title = Text("Python for AI", position=(960, 400), font_size=120, color=BLUE, sketch_style=SKETCH)
        sub_title = Text("The Holy Trinity: NumPy, Pandas, Matplotlib", position=(960, 550), font_size=60, color=DARK_GRAY, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 2.5, duration=2.5), drawable=sub_title)
        
        # Erase Intro
        e_intro = Eraser(objects_to_erase=[title, sub_title], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_numpy - 1.0, duration=1.0), drawable=e_intro)

        # --- SECTION 2: NUMPY (THE FOUNDATION) ---
        np_title = Text("1. NumPy (Numerical Python)", position=(500, 150), font_size=80, color=BLUE, sketch_style=SKETCH)
        np_formula = Math(r"$\vec{y} = \mathbf{W} \cdot \vec{x} + \vec{b}$", position=(1400, 450), font_size=100, color=BLUE)
        
        # Draw a 3x3 Array representation
        array_grid = Table(
            data=[["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]],
            top_left=(300, 350),
            col_widths=[120, 120, 120],
            row_heights=[100, 100, 100],
            font_size=50,
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            stroke_style=StrokeStyle(color=BLUE, width=3)
        )
        np_label = Text("ndarray: High-Speed Math", position=(500, 750), font_size=50, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=t_numpy, duration=1.5), drawable=np_title)
        scene.add(SketchAnimation(start_time=t_numpy + 2.0, duration=2.5), drawable=array_grid)
        scene.add(SketchAnimation(start_time=t_numpy + 5.0, duration=1.5), drawable=np_label)
        scene.add(SketchAnimation(start_time=t_numpy + 8.0, duration=2.5), drawable=np_formula)

        e_np = Eraser(objects_to_erase=[np_title, array_grid, np_label, np_formula], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_pandas - 1.0, duration=1.0), drawable=e_np)

        # --- SECTION 3: PANDAS (DATA MANIPULATION) ---
        pd_title = Text("2. Pandas (DataFrames)", position=(500, 150), font_size=80, color=GREEN, sketch_style=SKETCH)
        
        # Draw a DataFrame table
        df_table = Table(
            data=[["ID", "Name", "Age"], ["101", "Alice", "25"], ["102", "Bob", "30"], ["103", "Eve", "22"]],
            top_left=(400, 350),
            col_widths=[120, 250, 120],
            row_heights=[90, 90, 90, 90],
            font_size=40,
            header_fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.5),
            stroke_style=StrokeStyle(color=GREEN, width=3)
        )
        
        pd_func1 = Text("df.read_csv('data.csv')", position=(1400, 450), font_size=42, color=DARK_GRAY)
        pd_func2 = Text("df.dropna().groupby('Age')", position=(1400, 600), font_size=42, color=DARK_GRAY)
        
        scene.add(SketchAnimation(start_time=t_pandas, duration=1.5), drawable=pd_title)
        scene.add(SketchAnimation(start_time=t_pandas + 2.0, duration=3.0), drawable=df_table)
        scene.add(SketchAnimation(start_time=t_pandas + 6.0, duration=1.5), drawable=pd_func1)
        scene.add(SketchAnimation(start_time=t_pandas + 8.0, duration=1.5), drawable=pd_func2)

        e_pd = Eraser(objects_to_erase=[pd_title, df_table, pd_func1, pd_func2], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_plt - 1.0, duration=1.0), drawable=e_pd)

        # --- SECTION 4: MATPLOTLIB (VISUALIZATION) ---
        plt_title = Text("3. Matplotlib (Visualization)", position=(550, 150), font_size=80, color=ORANGE, sketch_style=SKETCH)
        
        # Simple Graph Visualization
        ax_x = Line(start=(400, 800), end=(1100, 800), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        ax_y = Line(start=(400, 400), end=(400, 800), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        
        # Graph points (Loss Curve)
        pts = [(400, 450), (550, 650), (750, 720), (950, 780), (1100, 795)]
        loss_curve = LinearPath(points=pts, stroke_style=StrokeStyle(color=ORANGE, width=5), sketch_style=SKETCH)
        loss_label = Text("Training Loss", position=(750, 400), font_size=40, color=ORANGE)
        
        plt_cmd = Text("plt.plot(history)", position=(1400, 500), font_size=50, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=t_plt, duration=1.5), drawable=plt_title)
        scene.add(SketchAnimation(start_time=t_plt + 2.0, duration=1.0), drawable=ax_x)
        scene.add(SketchAnimation(start_time=t_plt + 2.0, duration=1.0), drawable=ax_y)
        scene.add(SketchAnimation(start_time=t_plt + 4.0, duration=3.0), drawable=loss_curve)
        scene.add(SketchAnimation(start_time=t_plt + 7.0, duration=1.0), drawable=loss_label)
        scene.add(SketchAnimation(start_time=t_plt + 9.0, duration=1.5), drawable=plt_cmd)

        e_plt = Eraser(objects_to_erase=[plt_title, ax_x, ax_y, loss_curve, loss_label, plt_cmd], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_integration - 1.0, duration=1.0), drawable=e_plt)

        # --- SECTION 5: INTEGRATION (PIPELINE) ---
        integ_title = Text("AI Data Pipeline", position=(960, 150), font_size=80, color=PURPLE, sketch_style=SKETCH)
        
        # Box flow
        box_pd = Rectangle(top_left=(250, 450), width=300, height=150, stroke_style=StrokeStyle(color=GREEN, width=4), fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.2), sketch_style=SKETCH)
        txt_pd = Text("Load & Clean\n(Pandas)", position=(400, 525), font_size=36)
        
        arr1 = Arrow(start_point=(550, 525), end_point=(810, 525), stroke_style=StrokeStyle(color=BLACK, width=3))
        
        box_np = Rectangle(top_left=(810, 450), width=300, height=150, stroke_style=StrokeStyle(color=BLUE, width=4), fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.2), sketch_style=SKETCH)
        txt_np = Text("Compute\n(NumPy)", position=(960, 525), font_size=36)
        
        arr2 = Arrow(start_point=(1110, 525), end_point=(1370, 525), stroke_style=StrokeStyle(color=BLACK, width=3))
        
        box_plt = Rectangle(top_left=(1370, 450), width=300, height=150, stroke_style=StrokeStyle(color=ORANGE, width=4), fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.2), sketch_style=SKETCH)
        txt_plt = Text("Visualize\n(Matplotlib)", position=(1520, 525), font_size=36)
        
        scene.add(SketchAnimation(start_time=t_integration, duration=1.5), drawable=integ_title)
        scene.add(SketchAnimation(start_time=t_integration + 2.5, duration=1.5), drawable=box_pd)
        scene.add(SketchAnimation(start_time=t_integration + 2.5, duration=1.5), drawable=txt_pd)
        scene.add(SketchAnimation(start_time=t_integration + 5.0, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=t_integration + 6.0, duration=1.5), drawable=box_np)
        scene.add(SketchAnimation(start_time=t_integration + 6.0, duration=1.5), drawable=txt_np)
        scene.add(SketchAnimation(start_time=t_integration + 8.5, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=t_integration + 9.5, duration=1.5), drawable=box_plt)
        scene.add(SketchAnimation(start_time=t_integration + 9.5, duration=1.5), drawable=txt_plt)

        e_pipeline = Eraser(objects_to_erase=[integ_title, box_pd, txt_pd, arr1, box_np, txt_np, arr2, box_plt, txt_plt], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=e_pipeline)

        # --- SECTION 6: OUTRO ---
        final_msg = Text("The Foundation for AI Mastery", position=(960, 540), font_size=90, color=BLUE, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=final_msg)

    # 3. Final Render
    scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()