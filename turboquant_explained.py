"""
TurboQuant by Google (2026) - Whiteboard Animation
Explains Google's revolutionary AI memory compression algorithm.

OPTIMIZED FOR ULTRA-FAST RENDERING:
- Uses parallel rendering (all CPU cores)
- Reduced sketch roughness for faster drawing
- Optimized animation timing
- Batch rendering enabled
"""
from matplotlib.sphinxext.plot_directive import render_figures

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from handanim import *
from handanim.core import Scene, StrokeStyle, SketchStyle, FillStyle, DrawableGroup
from handanim.primitives import (
    Text,
    Circle,
    Line,
    Arrow,
    Curve,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Ellipse,
    Math,
    MathTex,
)
from handanim.animations import (
    SketchAnimation,
    FadeInAnimation,
    FadeOutAnimation,
    TransformAnimation,
    ReplacementTransformAnimation,
    TranslateToAnimation,
)
from handanim.stylings.color import (
    BLACK,
    WHITE,
    BLUE,
    RED,
    GREEN,
    PASTEL_BLUE,
    PASTEL_RED,
    PASTEL_GREEN,
    PASTEL_YELLOW,
    PASTEL_ORANGE,
    PASTEL_PURPLE,
    GRAY,
    DARK_GRAY,
    NAVY,
    TEAL,
    PURPLE,
    ORANGE,
)
import math

# ============================================================
# Scene Setup - OPTIMIZED FOR SPEED
# ============================================================
# Use lower resolution for faster rendering (upscale later if needed)
scene = Scene(
    width=1280,  # Reduced from 1920 (faster rendering)
    height=720,  # Reduced from 1080
    fps=30,      # Higher FPS for smoother animation
    background_color=WHITE,
    render_quality="fast"  # Fast rendering mode
)

# Common styles - SIMPLIFIED for speed
title_stroke = StrokeStyle(color=NAVY, width=3)
subtitle_stroke = StrokeStyle(color=BLUE, width=2.5)
body_stroke = StrokeStyle(color=BLACK, width=2)
highlight_stroke = StrokeStyle(color=RED, width=3)
green_stroke = StrokeStyle(color=GREEN, width=2.5)
box_stroke = StrokeStyle(color=DARK_GRAY, width=2)
# Reduced roughness = fewer curve calculations = faster rendering
sketch_light = SketchStyle(roughness=0.8, bowing=0.5)  # Was 1.5, 1
sketch_medium = SketchStyle(roughness=1.5, bowing=0.8)  # Was 3, 1.5

# Timeline tracking
t = 0  # current time in seconds

# ============================================================
# SCENE 1: Title Card (0-5s)
# ============================================================

# Main title
main_title = Text(
    text="TurboQuant",
    position=(960, 350),
    font_size=120,
    stroke_style=title_stroke,
    sketch_style=sketch_light,
    glow_dot_hint={"color": NAVY, "radius": 6},
)
scene.add(SketchAnimation(start_time=t, duration=2.5), drawable=main_title)

# Subtitle
subtitle = Text(
    text="Google's Revolutionary AI Compression (2026)",
    position=(960, 480),
    font_size=48,
    stroke_style=subtitle_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 2, duration=2), drawable=subtitle)

# Google logo hint (simple G circle)
google_circle = Circle(
    center=(200, 200),
    radius=50,
    stroke_style=StrokeStyle(color=BLUE, width=3),
    sketch_style=sketch_medium,
)
google_g = Text(
    text="G",
    position=(175, 165),
    font_size=72,
    stroke_style=StrokeStyle(color=RED, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 0.5, duration=1.5), drawable=google_circle)
scene.add(SketchAnimation(start_time=t + 1.5, duration=0.8), drawable=google_g)

# ICLR 2026 badge
badge = RoundedRectangle(
    top_left=(1500, 150),
    width=250,
    height=60,
    border_radius=0.3,
    stroke_style=StrokeStyle(color=PURPLE, width=2),
    fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3),
    sketch_style=sketch_light,
)
badge_text = Text(
    text="ICLR 2026",
    position=(1530, 155),
    font_size=36,
    stroke_style=StrokeStyle(color=PURPLE, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 3.5, duration=1), drawable=badge)
scene.add(SketchAnimation(start_time=t + 4, duration=0.8), drawable=badge_text)

t = 6

# ============================================================
# SCENE 2: The Problem - KV Cache Bottleneck (6-16s)
# ============================================================

# Section header
problem_header = Text(
    text="The Problem",
    position=(960, 100),
    font_size=64,
    stroke_style=StrokeStyle(color=RED, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=1.5), drawable=problem_header)

# Left side: LLM diagram
llm_box = RoundedRectangle(
    top_left=(200, 250),
    width=400,
    height=300,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=NAVY, width=3),
    fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.15),
    sketch_style=sketch_medium,
)
llm_text = Text(
    text="Large Language Model",
    position=(260, 300),
    font_size=36,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
llm_sub = Text(
    text="(Gemma, Mistral, etc.)",
    position=(320, 360),
    font_size=28,
    stroke_style=StrokeStyle(color=GRAY, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 1, duration=1.5), drawable=llm_box)
scene.add(SketchAnimation(start_time=t + 2, duration=1.5), drawable=llm_text)
scene.add(SketchAnimation(start_time=t + 3, duration=1), drawable=llm_sub)

# KV Cache box (the bottleneck)
kv_box = RoundedRectangle(
    top_left=(250, 600),
    width=300,
    height=150,
    border_radius=0.15,
    stroke_style=highlight_stroke,
    fill_style=FillStyle(color=PASTEL_RED, opacity=0.3),
    sketch_style=sketch_medium,
)
kv_text = Text(
    text="KV Cache",
    position=(340, 620),
    font_size=42,
    stroke_style=highlight_stroke,
    sketch_style=sketch_light,
)
kv_desc = Text(
    text="Stores key-value pairs\nfor fast retrieval",
    position=(290, 680),
    font_size=24,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 4, duration=1.5), drawable=kv_box)
scene.add(SketchAnimation(start_time=t + 5, duration=1.5), drawable=kv_text)
scene.add(SketchAnimation(start_time=t + 5.5, duration=1.5), drawable=kv_desc)

# Arrow from LLM to KV Cache
arrow1 = Arrow(
    start_point=(400, 550), end_point=(400, 600), stroke_style=StrokeStyle(color=RED, width=3)
)
scene.add(SketchAnimation(start_time=t + 4.5, duration=0.8), drawable=arrow1)

# Right side: Memory problem visualization
mem_header = Text(
    text="Memory Bottleneck",
    position=(1000, 250),
    font_size=48,
    stroke_style=StrokeStyle(color=RED, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 6, duration=1.5), drawable=mem_header)

# Memory bars showing huge consumption
for i in range(5):
    bar = Rectangle(
        top_left=(1000, 350 + i * 80),
        width=600 - i * 50,
        height=50,
        stroke_style=box_stroke,
        fill_style=FillStyle(color=PASTEL_RED, opacity=0.5 - i * 0.08),
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 7 + i * 0.3, duration=0.5), drawable=bar)

mem_label = Text(
    text="High-dimensional vectors consume\nmassive memory!",
    position=(1000, 800),
    font_size=32,
    stroke_style=highlight_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 9, duration=1.5), drawable=mem_label)

t = 17

# ============================================================
# SCENE 3: Traditional Quantization Issues (17-26s)
# ============================================================

# Section header
trad_header = Text(
    text="Traditional Vector Quantization",
    position=(960, 100),
    font_size=56,
    stroke_style=StrokeStyle(color=ORANGE, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=trad_header)

# Left: Traditional approach box
trad_box = RoundedRectangle(
    top_left=(150, 250),
    width=700,
    height=400,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=ORANGE, width=3),
    fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.15),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 1.5, duration=1.5), drawable=trad_box)

trad_title = Text(
    text="Standard Approach",
    position=(300, 280),
    font_size=36,
    stroke_style=StrokeStyle(color=ORANGE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 2.5, duration=1.2), drawable=trad_title)

# Show the overhead problem
overhead_text1 = Text(
    text="Requires storing quantization constants",
    position=(200, 360),
    font_size=28,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
overhead_text2 = Text(
    text="for each data block...",
    position=(300, 410),
    font_size=28,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 3.5, duration=1.5), drawable=overhead_text1)
scene.add(SketchAnimation(start_time=t + 4.5, duration=1.2), drawable=overhead_text2)

# Visual: blocks with overhead
for i in range(4):
    block = Rectangle(
        top_left=(200 + i * 160, 500),
        width=120,
        height=80,
        stroke_style=box_stroke,
        fill_style=FillStyle(color=PASTEL_YELLOW, opacity=0.4),
        sketch_style=sketch_light,
    )
    overhead = Rectangle(
        top_left=(200 + i * 160 + 100, 490),
        width=40,
        height=30,
        stroke_style=highlight_stroke,
        fill_style=FillStyle(color=PASTEL_RED, opacity=0.6),
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 5.5 + i * 0.3, duration=0.4), drawable=block)
    scene.add(SketchAnimation(start_time=t + 5.7 + i * 0.3, duration=0.4), drawable=overhead)

overhead_label = Text(
    text="+1 to +2 bits per number overhead!",
    position=(200, 620),
    font_size=30,
    stroke_style=highlight_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 7, duration=1.5), drawable=overhead_label)

# Right: The solution teaser
solution_box = RoundedRectangle(
    top_left=(1000, 250),
    width=750,
    height=400,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.15),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 8, duration=1.5), drawable=solution_box)

solution_title = Text(
    text="Enter TurboQuant",
    position=(1150, 300),
    font_size=48,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 9, duration=1.5), drawable=solution_title)

solution_desc = Text(
    text="A theoretically-grounded compression algorithm\nthat eliminates memory overhead entirely",
    position=(1050, 380),
    font_size=28,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 10, duration=2), drawable=solution_desc)

# Show the two components
polar_badge = RoundedRectangle(
    top_left=(1050, 500),
    width=300,
    height=60,
    border_radius=0.3,
    stroke_style=StrokeStyle(color=BLUE, width=2.5),
    fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
    sketch_style=sketch_light,
)
polar_text = Text(
    text="1. PolarQuant",
    position=(1110, 505),
    font_size=32,
    stroke_style=StrokeStyle(color=BLUE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 11.5, duration=1), drawable=polar_badge)
scene.add(SketchAnimation(start_time=t + 12, duration=0.8), drawable=polar_text)

qjl_badge = RoundedRectangle(
    top_left=(1400, 500),
    width=300,
    height=60,
    border_radius=0.3,
    stroke_style=StrokeStyle(color=PURPLE, width=2.5),
    fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3),
    sketch_style=sketch_light,
)
qjl_text = Text(
    text="2. QJL (1-bit trick)",
    position=(1430, 505),
    font_size=32,
    stroke_style=StrokeStyle(color=PURPLE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 12.5, duration=1), drawable=qjl_badge)
scene.add(SketchAnimation(start_time=t + 13, duration=0.8), drawable=qjl_text)

t = 28

# ============================================================
# SCENE 4: How PolarQuant Works (28-42s)
# ============================================================

# Section header
polar_header = Text(
    text="PolarQuant: A New Angle on Compression",
    position=(960, 80),
    font_size=52,
    stroke_style=StrokeStyle(color=BLUE, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=polar_header)

# Left: Cartesian coordinates explanation
cart_box = RoundedRectangle(
    top_left=(100, 200),
    width=750,
    height=350,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=GRAY, width=2),
    fill_style=FillStyle(
        color=LIGHT_GRAY if "LIGHT_GRAY" in dir() else (0.9, 0.9, 0.9), opacity=0.3
    ),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 1.5, duration=1.2), drawable=cart_box)

cart_title = Text(
    text="Standard (Cartesian) Coordinates",
    position=(150, 230),
    font_size=32,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 2.5, duration=1.2), drawable=cart_title)

# Draw coordinate axes
x_axis = Arrow(start_point=(200, 450), end_point=(650, 450), stroke_style=body_stroke)
y_axis = Arrow(start_point=(400, 520), end_point=(400, 250), stroke_style=body_stroke)
scene.add(SketchAnimation(start_time=t + 3.5, duration=1), drawable=x_axis)
scene.add(SketchAnimation(start_time=t + 4, duration=1), drawable=y_axis)

# Point and coordinates
point = Circle(
    center=(550, 300),
    radius=8,
    stroke_style=highlight_stroke,
    fill_style=FillStyle(color=PASTEL_RED, opacity=0.8),
)
x_line = Line(start=(550, 300), end=(550, 450), stroke_style=StrokeStyle(color=BLUE, width=2))
y_line = Line(start=(550, 300), end=(400, 300), stroke_style=StrokeStyle(color=GREEN, width=2))
scene.add(SketchAnimation(start_time=t + 5, duration=0.5), drawable=point)
scene.add(SketchAnimation(start_time=t + 5.3, duration=0.8), drawable=x_line)
scene.add(SketchAnimation(start_time=t + 5.6, duration=0.8), drawable=y_line)

x_label = Text(
    text="X = 3 blocks East",
    position=(560, 380),
    font_size=22,
    stroke_style=StrokeStyle(color=BLUE, width=2),
    sketch_style=sketch_light,
)
y_label = Text(
    text="Y = 4 blocks North",
    position=(420, 280),
    font_size=22,
    stroke_style=StrokeStyle(color=GREEN, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 6.5, duration=1), drawable=x_label)
scene.add(SketchAnimation(start_time=t + 7, duration=1), drawable=y_label)

cart_desc = Text(
    text='"Go 3 blocks East, 4 blocks North"',
    position=(150, 520),
    font_size=24,
    stroke_style=StrokeStyle(color=GRAY, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 8, duration=1.2), drawable=cart_desc)

# Right: Polar coordinates
polar_box = RoundedRectangle(
    top_left=(950, 200),
    width=800,
    height=350,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=BLUE, width=3),
    fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.15),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 9, duration=1.5), drawable=polar_box)

polar_title = Text(
    text="Polar Coordinates",
    position=(1150, 230),
    font_size=36,
    stroke_style=StrokeStyle(color=BLUE, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 10, duration=1.2), drawable=polar_title)

# Draw polar visualization
polar_x_axis = Arrow(start_point=(1050, 450), end_point=(1500, 450), stroke_style=body_stroke)
polar_y_axis = Arrow(start_point=(1250, 520), end_point=(1250, 250), stroke_style=body_stroke)
scene.add(SketchAnimation(start_time=t + 11, duration=1), drawable=polar_x_axis)
scene.add(SketchAnimation(start_time=t + 11.5, duration=1), drawable=polar_y_axis)

# Arc and radius
polar_point = Circle(
    center=(1400, 300),
    radius=8,
    stroke_style=highlight_stroke,
    fill_style=FillStyle(color=PASTEL_RED, opacity=0.8),
)
radius_line = Line(start=(1250, 450), end=(1400, 300), stroke_style=StrokeStyle(color=RED, width=3))
scene.add(SketchAnimation(start_time=t + 12.5, duration=0.5), drawable=polar_point)
scene.add(SketchAnimation(start_time=t + 12.8, duration=0.8), drawable=radius_line)

# Arc (approximate with curve)
arc_points = [(1350, 450), (1380, 420), (1400, 380), (1400, 340), (1400, 308)]
arc = Curve(points=arc_points, stroke_style=StrokeStyle(color=GREEN, width=2.5))
scene.add(SketchAnimation(start_time=t + 13.5, duration=0.8), drawable=arc)

r_label = Text(
    text="r = 5 (strength)",
    position=(1300, 360),
    font_size=22,
    stroke_style=StrokeStyle(color=RED, width=2.5),
    sketch_style=sketch_light,
)
angle_label = Text(
    text="theta = 37 deg (direction)",
    position=(1350, 460),
    font_size=22,
    stroke_style=StrokeStyle(color=GREEN, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 14.5, duration=1), drawable=r_label)
scene.add(SketchAnimation(start_time=t + 15, duration=1), drawable=angle_label)

polar_desc = Text(
    text='"Go 5 blocks at 37 degree angle"',
    position=(1000, 520),
    font_size=24,
    stroke_style=StrokeStyle(color=BLUE, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 16, duration=1.2), drawable=polar_desc)

# Bottom: Key insight
insight_box = RoundedRectangle(
    top_left=(200, 650),
    width=1500,
    height=200,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.2),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 17, duration=1.5), drawable=insight_box)

insight_title = Text(
    text="Key Insight:",
    position=(300, 680),
    font_size=36,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 18, duration=1), drawable=insight_title)

insight_text = Text(
    text="Angles follow a predictable pattern -> No expensive normalization needed!\nMaps data onto a fixed circular grid instead of a changing square grid.\nThis eliminates the memory overhead traditional methods must carry.",
    position=(300, 740),
    font_size=28,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 18.5, duration=2.5), drawable=insight_text)

t = 44

# ============================================================
# SCENE 5: How QJL Works (44-56s)
# ============================================================

# Section header
qjl_header = Text(
    text="QJL: The Zero-Overhead 1-Bit Trick",
    position=(960, 80),
    font_size=52,
    stroke_style=StrokeStyle(color=PURPLE, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=qjl_header)

# QJL explanation box
qjl_box = RoundedRectangle(
    top_left=(200, 200),
    width=1500,
    height=300,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=PURPLE, width=3),
    fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.15),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 1.5, duration=1.5), drawable=qjl_box)

qjl_desc1 = Text(
    text="Uses the Johnson-Lindenstrauss Transform to shrink high-dimensional data",
    position=(250, 240),
    font_size=30,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 2.5, duration=1.5), drawable=qjl_desc1)

qjl_desc2 = Text(
    text="while preserving distances between data points.",
    position=(400, 290),
    font_size=30,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 3.5, duration=1.2), drawable=qjl_desc2)

# Visual: High-dim -> 1-bit
high_dim_box = Rectangle(
    top_left=(300, 400),
    width=250,
    height=100,
    stroke_style=StrokeStyle(color=RED, width=2.5),
    fill_style=FillStyle(color=PASTEL_RED, opacity=0.3),
    sketch_style=sketch_light,
)
high_dim_text = Text(
    text="Complex Vector\n[0.23, -1.45, 3.21, ...]",
    position=(310, 410),
    font_size=24,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 5, duration=1.2), drawable=high_dim_box)
scene.add(SketchAnimation(start_time=t + 5.5, duration=1.2), drawable=high_dim_text)

# Arrow
transform_arrow = Arrow(
    start_point=(580, 440), end_point=(750, 440), stroke_style=StrokeStyle(color=PURPLE, width=3)
)
scene.add(SketchAnimation(start_time=t + 6.5, duration=0.8), drawable=transform_arrow)

arrow_label = Text(
    text="QJL Transform",
    position=(600, 410),
    font_size=24,
    stroke_style=StrokeStyle(color=PURPLE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 7, duration=1), drawable=arrow_label)

# 1-bit result
onebit_box = Rectangle(
    top_left=(800, 400),
    width=200,
    height=100,
    stroke_style=StrokeStyle(color=GREEN, width=2.5),
    fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
    sketch_style=sketch_light,
)
onebit_text = Text(
    text="1-Bit Result\n[+1, -1, +1, ...]",
    position=(820, 410),
    font_size=28,
    stroke_style=StrokeStyle(color=GREEN, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 8, duration=1.2), drawable=onebit_box)
scene.add(SketchAnimation(start_time=t + 8.5, duration=1.2), drawable=onebit_text)

# Key properties
props_box = RoundedRectangle(
    top_left=(200, 580),
    width=1500,
    height=350,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=TEAL, width=3),
    fill_style=FillStyle(color=(0.2, 0.8, 0.8), opacity=0.1),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 10, duration=1.5), drawable=props_box)

prop1 = Text(
    text="ZERO memory overhead - just sign bits (+1 or -1)",
    position=(250, 620),
    font_size=32,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    sketch_style=sketch_light,
)
prop2 = Text(
    text="Creates high-speed shorthand for data",
    position=(250, 690),
    font_size=32,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
prop3 = Text(
    text="Special estimator balances precision with simplicity",
    position=(250, 760),
    font_size=32,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
prop4 = Text(
    text="Eliminates bias -> more accurate attention scores",
    position=(250, 830),
    font_size=32,
    stroke_style=StrokeStyle(color=BLUE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 11, duration=1), drawable=prop1)
scene.add(SketchAnimation(start_time=t + 11.5, duration=1), drawable=prop2)
scene.add(SketchAnimation(start_time=t + 12, duration=1), drawable=prop3)
scene.add(SketchAnimation(start_time=t + 12.5, duration=1), drawable=prop4)

t = 58

# ============================================================
# SCENE 6: How TurboQuant Combines Both (58-70s)
# ============================================================

# Section header
combo_header = Text(
    text="TurboQuant: Two-Step Compression",
    position=(960, 80),
    font_size=52,
    stroke_style=StrokeStyle(color=NAVY, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=combo_header)

# Step 1 box
step1_box = RoundedRectangle(
    top_left=(100, 200),
    width=800,
    height=400,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=BLUE, width=3),
    fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.15),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 1.5, duration=1.5), drawable=step1_box)

step1_num = Text(
    text="Step 1",
    position=(350, 220),
    font_size=48,
    stroke_style=StrokeStyle(color=BLUE, width=3),
    sketch_style=sketch_light,
)
step1_title = Text(
    text="PolarQuant: High-Quality Compression",
    position=(180, 290),
    font_size=32,
    stroke_style=StrokeStyle(color=BLUE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 2.5, duration=1), drawable=step1_num)
scene.add(SketchAnimation(start_time=t + 3, duration=1.2), drawable=step1_title)

step1_desc = Text(
    text="1. Randomly rotate data vectors\n2. Simplifies data geometry\n3. Apply standard quantizer to each part\n4. Uses MOST bits to capture main concept",
    position=(150, 360),
    font_size=26,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 4, duration=2), drawable=step1_desc)

step1_result = Text(
    text="Result: Captures vector's core meaning & strength",
    position=(150, 550),
    font_size=24,
    stroke_style=StrokeStyle(color=GREEN, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 6, duration=1.2), drawable=step1_result)

# Step 2 box
step2_box = RoundedRectangle(
    top_left=(1000, 200),
    width=800,
    height=400,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=PURPLE, width=3),
    fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.15),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 7, duration=1.5), drawable=step2_box)

step2_num = Text(
    text="Step 2",
    position=(1250, 220),
    font_size=48,
    stroke_style=StrokeStyle(color=PURPLE, width=3),
    sketch_style=sketch_light,
)
step2_title = Text(
    text="QJL: Eliminate Hidden Errors",
    position=(1100, 290),
    font_size=32,
    stroke_style=StrokeStyle(color=PURPLE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 8, duration=1), drawable=step2_num)
scene.add(SketchAnimation(start_time=t + 8.5, duration=1.2), drawable=step2_title)

step2_desc = Text(
    text="1. Takes tiny residual error from Step 1\n2. Applies QJL with just 1 bit\n3. Acts as mathematical error-checker\n4. Eliminates bias in attention scores",
    position=(1050, 360),
    font_size=26,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 9.5, duration=2), drawable=step2_desc)

step2_result = Text(
    text="Result: Zero overhead, perfect accuracy",
    position=(1050, 550),
    font_size=24,
    stroke_style=StrokeStyle(color=GREEN, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 11.5, duration=1.2), drawable=step2_result)

# Bottom summary
summary_box = RoundedRectangle(
    top_left=(200, 700),
    width=1500,
    height=200,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.2),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 12.5, duration=1.5), drawable=summary_box)

summary_text = Text(
    text="TurboQuant = PolarQuant (compression) + QJL (error correction)\nTogether they achieve optimal distortion with near-zero overhead",
    position=(300, 740),
    font_size=32,
    stroke_style=StrokeStyle(color=DARK_GRAY, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 13.5, duration=2), drawable=summary_text)

t = 72

# ============================================================
# SCENE 7: Results & Benchmarks (72-88s)
# ============================================================

# Section header
results_header = Text(
    text="Experimental Results",
    position=(960, 80),
    font_size=56,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=results_header)

# Results grid - 4 boxes
results = [
    ("6x", "KV Cache\nReduction", PASTEL_BLUE, BLUE),
    ("8x", "Speedup on\nH100 GPUs", PASTEL_GREEN, GREEN),
    ("3-bit", "Quantization\n(no training!)", PASTEL_YELLOW, ORANGE),
    ("50%+", "Cost\nReduction", PASTEL_PURPLE, PURPLE),
]

for i, (value, label, bg_color, text_color) in enumerate(results):
    x = 150 + (i % 2) * 850
    y = 200 + (i // 2) * 350

    result_box = RoundedRectangle(
        top_left=(x, y),
        width=700,
        height=280,
        border_radius=0.15,
        stroke_style=StrokeStyle(color=text_color, width=3),
        fill_style=FillStyle(color=bg_color, opacity=0.3),
        sketch_style=sketch_medium,
    )
    scene.add(SketchAnimation(start_time=t + 1.5 + i * 0.5, duration=1.2), drawable=result_box)

    value_text = Text(
        text=value,
        position=(x + 250, y + 60),
        font_size=80,
        stroke_style=StrokeStyle(color=text_color, width=3),
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 2 + i * 0.5, duration=0.8), drawable=value_text)

    label_text = Text(
        text=label,
        position=(x + 150, y + 160),
        font_size=36,
        stroke_style=body_stroke,
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 2.5 + i * 0.5, duration=1), drawable=label_text)

# Benchmarks tested
bench_box = RoundedRectangle(
    top_left=(200, 850),
    width=1500,
    height=150,
    border_radius=0.15,
    stroke_style=box_stroke,
    fill_style=FillStyle(color=(0.95, 0.95, 0.95), opacity=0.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 5, duration=1.2), drawable=bench_box)

bench_title = Text(
    text="Tested on: LongBench, Needle In A Haystack, ZeroSCROLLS, RULER, L-Eval",
    position=(220, 880),
    font_size=28,
    stroke_style=body_stroke,
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 5.5, duration=1.5), drawable=bench_title)

bench_models = Text(
    text="Models: Gemma, Mistral, Llama-3.1-8B-Instruct",
    position=(400, 940),
    font_size=26,
    stroke_style=StrokeStyle(color=GRAY, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 6.5, duration=1.2), drawable=bench_models)

t = 89

# ============================================================
# SCENE 8: Applications & Impact (89-102s)
# ============================================================

# Section header
apps_header = Text(
    text="Applications & Impact",
    position=(960, 80),
    font_size=56,
    stroke_style=StrokeStyle(color=TEAL, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=apps_header)

# Application boxes
applications = [
    ("LLM Inference", "Faster inference with\nless memory", PASTEL_BLUE, BLUE),
    ("Vector Search", "Build & query billion-\nsize indices faster", PASTEL_GREEN, GREEN),
    ("Semantic Search", "Google-scale meaning-\nbased search", PASTEL_YELLOW, ORANGE),
    ("Cost Savings", "50%+ reduction in\nAI infrastructure costs", PASTEL_PURPLE, PURPLE),
]

for i, (title, desc, bg_color, text_color) in enumerate(applications):
    x = 150 + i * 420

    app_box = RoundedRectangle(
        top_left=(x, 200),
        width=360,
        height=400,
        border_radius=0.15,
        stroke_style=StrokeStyle(color=text_color, width=2.5),
        fill_style=FillStyle(color=bg_color, opacity=0.2),
        sketch_style=sketch_medium,
    )
    scene.add(SketchAnimation(start_time=t + 1.5 + i * 0.4, duration=1), drawable=app_box)

    app_title = Text(
        text=title,
        position=(x + 30, y + 30) if False else (x + 40, 230),
        font_size=32,
        stroke_style=StrokeStyle(color=text_color, width=2.5),
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 2 + i * 0.4, duration=0.8), drawable=app_title)

    app_desc = Text(
        text=desc,
        position=(x + 30, 300),
        font_size=24,
        stroke_style=body_stroke,
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 2.5 + i * 0.4, duration=1), drawable=app_desc)

# Gemini mention
gemini_box = RoundedRectangle(
    top_left=(300, 700),
    width=1300,
    height=150,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=NAVY, width=3),
    fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.2),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 5, duration=1.2), drawable=gemini_box)

gemini_text = Text(
    text="Major application: Solving the KV cache bottleneck in models like Gemini",
    position=(350, 730),
    font_size=32,
    stroke_style=StrokeStyle(color=NAVY, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 5.5, duration=1.5), drawable=gemini_text)

t = 103

# ============================================================
# SCENE 9: Summary & Conclusion (103-118s)
# ============================================================

# Section header
summary_header = Text(
    text="Summary",
    position=(960, 100),
    font_size=72,
    stroke_style=StrokeStyle(color=NAVY, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=1.5), drawable=summary_header)

# Key takeaways
takeaways = [
    "TurboQuant compresses LLM memory by 6x with ZERO accuracy loss",
    "Combines PolarQuant (polar coordinates) + QJL (1-bit error correction)",
    "Achieves 8x speedup on H100 GPUs, 50%+ cost reduction",
    "No training or fine-tuning required - works out of the box",
    "Published at ICLR 2026 by Google Research",
]

for i, takeaway in enumerate(takeaways):
    y_pos = 220 + i * 120

    # Bullet point
    bullet = Circle(
        center=(250, y_pos),
        radius=10,
        stroke_style=StrokeStyle(color=GREEN, width=2.5),
        fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.5),
    )
    scene.add(SketchAnimation(start_time=t + 1 + i * 0.3, duration=0.3), drawable=bullet)

    takeaway_text = Text(
        text=takeaway,
        position=(300, y_pos - 20),
        font_size=30,
        stroke_style=body_stroke,
        sketch_style=sketch_light,
    )
    scene.add(SketchAnimation(start_time=t + 1.2 + i * 0.3, duration=1.2), drawable=takeaway_text)

# Final callout
final_box = RoundedRectangle(
    top_left=(300, 850),
    width=1300,
    height=150,
    border_radius=0.15,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.25),
    sketch_style=sketch_medium,
)
scene.add(SketchAnimation(start_time=t + 3, duration=1.5), drawable=final_box)

final_text = Text(
    text="TurboQuant = Theoretical rigor + Practical efficiency for AI at scale",
    position=(350, 880),
    font_size=36,
    stroke_style=StrokeStyle(color=GREEN, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 4, duration=2), drawable=final_text)

t = 119

# ============================================================
# SCENE 10: End Card (119-125s)
# ============================================================

end_title = Text(
    text="Thanks for Watching!",
    position=(960, 400),
    font_size=80,
    stroke_style=StrokeStyle(color=NAVY, width=3),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t, duration=2), drawable=end_title)

end_sub = Text(
    text="TurboQuant: Redefining AI Efficiency with Extreme Compression",
    position=(960, 520),
    font_size=36,
    stroke_style=StrokeStyle(color=BLUE, width=2.5),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 1.5, duration=1.5), drawable=end_sub)

end_links = Text(
    text="arxiv.org/abs/2504.19874  |  ICLR 2026",
    position=(960, 620),
    font_size=28,
    stroke_style=StrokeStyle(color=GRAY, width=2),
    sketch_style=sketch_light,
)
scene.add(SketchAnimation(start_time=t + 2.5, duration=1.5), drawable=end_links)

# ============================================================
# Render - ULTRA-FAST MODE
# ============================================================
print("="*60)
print("Rendering TurboQuant whiteboard animation...")
print("="*60)
print("OPTIMIZATIONS ENABLED:")
print("  ✓ Resolution: 1280x720 (upscale later if needed)")
print("  ✓ FPS: 30 (smooth animation)")
print("  ✓ Parallel rendering: Using all CPU cores")
print("  ✓ Batch rendering: Enabled")
print("  ✓ Sketch roughness: Reduced for speed")
print("="*60)

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "turboquant_explained.mp4")

# ULTRA-FAST RENDERING: Use parallel=True for massive speedup
# This will use ALL your CPU cores simultaneously
scene.render(
    output_path, 
    max_length=130,
    parallel=True,           # Use all CPU cores (2-8x faster!)
    use_batch_rendering=True # Batch frame writing (10x faster)
)

print("="*60)
print(f"✓ Done! Output saved to: {output_path}")
print("="*60)
