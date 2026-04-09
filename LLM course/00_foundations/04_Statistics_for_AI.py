"""
Whiteboard explainer: Probability & Statistics for AI

This scene covers the mathematical foundations of statistics used in AI:
Mean, Variance, Standard Deviation, the Normal Distribution, and Bayes' Theorem.
"""

from __future__ import annotations

import asyncio
import os
import re
import math
from pathlib import Path

# Try to import edge-tts for audio generation
try:
    import edge_tts
except ImportError:
    print("Please install edge-tts: pip install edge-tts")
    exit()

from handanim.animations import (
    SketchAnimation,
    FadeInAnimation,
)
from handanim.core import (
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
    VoiceoverTracker,
)
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
AUDIO_PATH = os.path.join(OUTPUT_DIR, "stats_narration.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "stats_whiteboard.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
FONT_NAME = "feasibly"
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> Probability and Statistics are the bedrock of machine learning. "
    "They allow us to quantify uncertainty and find patterns in noisy data. "
    "<bookmark mark='foundation_start'/> We start with the basics of data description: Mean, Variance, and Standard Deviation. "
    "The Mean is the average—the center of gravity for our data points. "
    "Variance measures the spread—how far the numbers are stretched from that center. "
    "The Standard Deviation is simply the square root of variance, bringing the spread back to the original units. "
    "<bookmark mark='dist_start'/> Next, we look at Distributions, specifically the Normal Distribution, or Bell Curve. "
    "Most natural phenomena, from heights to test scores, follow this pattern. "
    "It is defined by its peak at the mean and its width, governed by the standard deviation. "
    "In AI, we often assume our data or errors follow this distribution to simplify calculations. "
    "<bookmark mark='bayes_start'/> Finally, we reach the cornerstone of logical inference: Bayes' Theorem. "
    "It provides a mathematical way to update our beliefs as we gather new evidence. "
    "The probability of A given B depends on the probability of B given A, multiplied by our prior knowledge. "
    "This theorem is the heart of spam filters, medical diagnosis, and autonomous driving. "
    "<bookmark mark='outro'/> From measuring the average to updating our worldview with data, "
    "Statistics is the science of making sense of the world. Thanks for watching."
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
    # 1. Generate Narration
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Construct Scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_found = tracker.bookmark_time("foundation_start")
        t_dist = tracker.bookmark_time("dist_start")
        t_bayes = tracker.bookmark_time("bayes_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRO ---
        title = Text("Probability & Statistics", position=(960, 400), font_size=110, color=BLUE, sketch_style=SKETCH)
        subtitle = Text("The Science of Uncertainty", position=(960, 550), font_size=60, color=DARK_GRAY, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 2.0, duration=2.0), drawable=subtitle)
        
        eraser_intro = Eraser(objects_to_erase=[title, subtitle], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_found - 1.0, duration=1.0), drawable=eraser_intro)

        # --- SECTION 2: MEAN, VARIANCE, STDEV ---
        f_title = Text("1. Describing Data", position=(400, 150), font_size=80, color=RED, sketch_style=SKETCH)
        
        # Mean
        mean_math = Math(r"$\mu = \frac{\sum x_i}{N}$", position=(500, 450), font_size=90, color=BLUE)
        mean_lbl = Text("Mean (Average)", position=(500, 580), font_size=40)
        
        # Variance
        var_math = Math(r"$\sigma^2 = \frac{\sum (x_i - \mu)^2}{N}$", position=(1400, 450), font_size=90, color=RED)
        var_lbl = Text("Variance (Spread)", position=(1400, 580), font_size=40)
        
        # Stdev
        sd_math = Math(r"$\sigma = \sqrt{\sigma^2}$", position=(960, 750), font_size=110, color=PURPLE)
        sd_lbl = Text("Standard Deviation", position=(960, 880), font_size=40)

        scene.add(SketchAnimation(start_time=t_found, duration=1.5), drawable=f_title)
        scene.add(SketchAnimation(start_time=t_found + 1.5, duration=2.0), drawable=mean_math)
        scene.add(SketchAnimation(start_time=t_found + 2.5, duration=1.0), drawable=mean_lbl)
        scene.add(SketchAnimation(start_time=t_found + 4.0, duration=2.0), drawable=var_math)
        scene.add(SketchAnimation(start_time=t_found + 5.0, duration=1.0), drawable=var_lbl)
        scene.add(SketchAnimation(start_time=t_found + 7.0, duration=2.0), drawable=sd_math)
        scene.add(SketchAnimation(start_time=t_found + 8.5, duration=1.0), drawable=sd_lbl)

        eraser_found = Eraser(objects_to_erase=[f_title, mean_math, mean_lbl, var_math, var_lbl, sd_math, sd_lbl], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_dist - 1.0, duration=1.0), drawable=eraser_found)

        # --- SECTION 3: NORMAL DISTRIBUTION ---
        d_title = Text("2. Distributions", position=(400, 150), font_size=80, color=GREEN, sketch_style=SKETCH)
        
        # Draw Bell Curve
        xaxis = Line(start=(400, 850), end=(1520, 850), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        
        # Gaussian curve points
        curve_pts = []
        for x_val in range(-300, 301, 10):
            # y = e^(-x^2 / 2sigma^2)
            y_val = 300 * math.exp(-(x_val**2) / (2 * 100**2))
            curve_pts.append((960 + x_val, 850 - y_val))
        
        bell_curve = LinearPath(points=curve_pts, stroke_style=StrokeStyle(color=BLUE, width=5), sketch_style=SKETCH)
        
        mean_line = Line(start=(960, 850), end=(960, 550), stroke_style=StrokeStyle(color=RED, width=3, opacity=0.8), sketch_style=SKETCH)
        mean_txt = Text("Mean", position=(960, 520), font_size=32, color=RED)
        
        sd_arrow = Arrow(start_point=(960, 700), end_point=(1060, 700), stroke_style=StrokeStyle(color=ORANGE, width=4))
        sd_txt = Text("1 Sigma", position=(1150, 700), font_size=32, color=ORANGE)

        scene.add(SketchAnimation(start_time=t_dist, duration=1.5), drawable=d_title)
        scene.add(SketchAnimation(start_time=t_dist + 1.0, duration=1.0), drawable=xaxis)
        scene.add(SketchAnimation(start_time=t_dist + 2.0, duration=3.0), drawable=bell_curve)
        scene.add(SketchAnimation(start_time=t_dist + 5.5, duration=1.0), drawable=mean_line)
        scene.add(SketchAnimation(start_time=t_dist + 6.0, duration=0.8), drawable=mean_txt)
        scene.add(SketchAnimation(start_time=t_dist + 8.5, duration=1.0), drawable=sd_arrow)
        scene.add(SketchAnimation(start_time=t_dist + 9.0, duration=0.8), drawable=sd_txt)

        eraser_dist = Eraser(objects_to_erase=[d_title, xaxis, bell_curve, mean_line, mean_txt, sd_arrow, sd_txt], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_bayes - 1.0, duration=1.0), drawable=eraser_dist)

        # --- SECTION 4: BAYES' THEOREM ---
        b_title = Text("3. Bayes' Theorem", position=(450, 150), font_size=80, color=ORANGE, sketch_style=SKETCH)
        
        # P(A|B) = P(B|A)P(A) / P(B)
        bayes_formula = Math(r"$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$", position=(960, 500), font_size=130, color=DARK_GRAY)
        
        labels = [
            Text("Posterior", position=(500, 400), font_size=40, color=BLUE),
            Text("Likelihood", position=(1050, 400), font_size=40, color=GREEN),
            Text("Prior", position=(1300, 400), font_size=40, color=ORANGE),
            Text("Evidence", position=(1100, 680), font_size=40, color=PURPLE)
        ]

        scene.add(SketchAnimation(start_time=t_bayes, duration=1.5), drawable=b_title)
        scene.add(SketchAnimation(start_time=t_bayes + 3.0, duration=3.5), drawable=bayes_formula)
        
        scene.add(SketchAnimation(start_time=t_bayes + 7.5, duration=1.0), drawable=labels[0])
        scene.add(SketchAnimation(start_time=t_bayes + 8.5, duration=1.0), drawable=labels[1])
        scene.add(SketchAnimation(start_time=t_bayes + 9.5, duration=1.0), drawable=labels[2])
        scene.add(SketchAnimation(start_time=t_bayes + 10.5, duration=1.0), drawable=labels[3])

        eraser_bayes = Eraser(objects_to_erase=[b_title, bayes_formula, *labels], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=eraser_bayes)

        # --- SECTION 5: OUTRO ---
        outro_msg = Text("Statistics: The Science of Making Sense", position=(960, 540), font_size=80, color=BLUE, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=outro_msg)

    # 3. Final Render
    scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()