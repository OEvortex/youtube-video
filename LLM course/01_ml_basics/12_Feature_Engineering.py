



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
from handanim.animations import SketchAnimation, TransformAnimation
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, Math
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "feature_engineering"
AUDIO_PATH = OUTPUT_DIR / "feat_eng_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "feat_eng_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome! Today we are looking at Feature Engineering, "
    "specifically Scaling, Normalization, and PCA. "
    
    "<bookmark mark='scaling_problem'/> Let's start with Scaling. "
    "Imagine you have two features: Age, which goes from zero to one hundred, "
    "and Income, which goes up to one hundred thousand dollars. "
    "Machine Learning models can get confused and think Income is vastly more important "
    "just because the raw numbers are bigger! "
    
    "<bookmark mark='scaling_solution'/> Min-Max Scaling fixes this. "
    "It mathematically squishes all values into a tiny, uniform box, forcing everything to sit "
    "exactly between zero and one. Now, Age and Income are on equal footing. "
    
    "<bookmark mark='norm'/> Next up is Normalization, also known as Standardization. "
    "Sometimes your data is spread out wildly with extreme outliers that confuse your model. "
    
    "<bookmark mark='norm_solution'/> Standardization gathers your data and molds it into a beautiful bell curve. "
    "It forces the mean to exactly zero, and the standard deviation to exactly one. "
    "This helps gradient descent converge much faster! "
    
    "<bookmark mark='pca'/> Finally, what if you have too many features? "
    "This causes the Curse of Dimensionality, slowing down training and causing overfitting. "
    
    "<bookmark mark='pca_solution'/> Principal Component Analysis, or PCA, solves this beautifully. "
    "It rotates the perspective of your data to find the path of maximum variance. "
    
    "<bookmark mark='pca_visual'/> We can take a messy two-dimensional scatter plot, find the main axis, "
    "and project it down to a single, one-dimensional line without losing the big picture! "
    
    "<bookmark mark='outro'/> Proper Feature Engineering makes your models faster, smarter, and far more accurate. Thanks for watching!"
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
        font_size=90,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=4.0),
        sketch_style=SKETCH,
    )

def make_body(
    text: str, *, x: float = 960, y: float, color: tuple[float, float, float] = BLACK, align: str = "center", font_size: int = 48
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

scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()

def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.2) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)

def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        intro_start = tracker.bookmark_time("intro")
        scale_prob_start = tracker.bookmark_time("scaling_problem")
        scale_sol_start = tracker.bookmark_time("scaling_solution")
        norm_start = tracker.bookmark_time("norm")
        norm_sol_start = tracker.bookmark_time("norm_solution")
        pca_start = tracker.bookmark_time("pca")
        pca_sol_start = tracker.bookmark_time("pca_solution")
        pca_vis_start = tracker.bookmark_time("pca_visual")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Feature Engineering", y=400, color=BLUE)
        intro_sub = make_body("Scaling, Normalization, and PCA", y=550, color=ORANGE, font_size=64)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        
        intro_drawables = [intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Min-Max Scaling
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=scale_prob_start - 1.2)
        scale_drawables =[]

        scale_title = make_title("1. Min-Max Scaling", y=150, color=GREEN)
        
        # Unscaled versions
        age_label = make_body("Age (0 - 100):", x=400, y=350, color=BLACK, font_size=48, align="right")
        age_line_unscaled = Line(start=(600, 350), end=(800, 350), stroke_style=StrokeStyle(color=BLUE, width=8.0), sketch_style=SKETCH)
        
        inc_label = make_body("Income (0 - 100k):", x=400, y=500, color=BLACK, font_size=48, align="right")
        inc_line_unscaled = Line(start=(600, 500), end=(1700, 500), stroke_style=StrokeStyle(color=RED, width=8.0), sketch_style=SKETCH)

        problem_text = make_body("Model Bias: 'Income is more important!'", x=960, y=650, color=RED, font_size=56)

        # Scaled versions
        scale_box = FlowchartProcess("Squish to[0, 1]", top_left=(760, 720), width=400, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=box_stroke)
        
        age_line_scaled = Line(start=(600, 350), end=(1200, 350), stroke_style=StrokeStyle(color=BLUE, width=8.0), sketch_style=SKETCH)
        inc_line_scaled = Line(start=(600, 500), end=(1200, 500), stroke_style=StrokeStyle(color=RED, width=8.0), sketch_style=SKETCH)

        # Ticks for scaled
        tick_0 = make_body("0", x=600, y=580, color=DARK_GRAY)
        tick_1 = make_body("1", x=1200, y=580, color=DARK_GRAY)
        tick_line_0 = Line(start=(600, 300), end=(600, 550), stroke_style=StrokeStyle(color=DARK_GRAY, width=2.0), sketch_style=SKETCH)
        tick_line_1 = Line(start=(1200, 300), end=(1200, 550), stroke_style=StrokeStyle(color=DARK_GRAY, width=2.0), sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=scale_prob_start + 0.5, duration=1.0), drawable=scale_title)
        scene.add(SketchAnimation(start_time=scale_prob_start + 3.0, duration=0.8), drawable=age_label)
        scene.add(SketchAnimation(start_time=scale_prob_start + 3.5, duration=0.8), drawable=age_line_unscaled)
        scene.add(SketchAnimation(start_time=scale_prob_start + 5.0, duration=0.8), drawable=inc_label)
        scene.add(SketchAnimation(start_time=scale_prob_start + 5.5, duration=1.5), drawable=inc_line_unscaled)
        scene.add(SketchAnimation(start_time=scale_prob_start + 7.5, duration=1.5), drawable=problem_text)

        # Eraser for problem text
        erase_prob = Eraser([problem_text], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=scale_sol_start, duration=1.0), drawable=erase_prob)

        scene.add(SketchAnimation(start_time=scale_sol_start + 1.0, duration=1.0), drawable=scale_box)
        
        scene.add(TransformAnimation(target_drawable=age_line_scaled, start_time=scale_sol_start + 3.0, duration=1.5), age_line_unscaled)
        scene.add(TransformAnimation(target_drawable=inc_line_scaled, start_time=scale_sol_start + 3.0, duration=1.5), inc_line_unscaled)
        
        scene.add(SketchAnimation(start_time=scale_sol_start + 4.5, duration=0.5), drawable=tick_line_0)
        scene.add(SketchAnimation(start_time=scale_sol_start + 4.5, duration=0.5), drawable=tick_line_1)
        scene.add(SketchAnimation(start_time=scale_sol_start + 5.0, duration=0.5), drawable=tick_0)
        scene.add(SketchAnimation(start_time=scale_sol_start + 5.0, duration=0.5), drawable=tick_1)

        scale_drawables.extend([scale_title, age_label, age_line_scaled, inc_label, inc_line_scaled, scale_box, tick_0, tick_1, tick_line_0, tick_line_1])

        # ---------------------------------------------------------
        # SECTION 3: Normalization / Standardization
        # ---------------------------------------------------------
        make_eraser(scale_drawables, start_time=norm_start - 1.2)
        norm_drawables =[]

        norm_title = make_title("2. Normalization (Standardization)", y=150, color=PURPLE)
        
        # Outlier points
        p1 = Circle(center=(300, 800), radius=10, fill_style=FillStyle(color=RED, opacity=1.0), stroke_style=StrokeStyle(color=BLACK), sketch_style=SKETCH)
        p2 = Circle(center=(1600, 800), radius=10, fill_style=FillStyle(color=RED, opacity=1.0), stroke_style=StrokeStyle(color=BLACK), sketch_style=SKETCH)
        p3 = Circle(center=(800, 800), radius=10, fill_style=FillStyle(color=RED, opacity=1.0), stroke_style=StrokeStyle(color=BLACK), sketch_style=SKETCH)
        outlier_text = make_body("Wildly spread data + outliers", x=960, y=900, color=RED, font_size=48)

        # Bell Curve
        bell = Curve(
            points=[(400, 800), (600, 780), (750, 600), (960, 300), (1170, 600), (1320, 780), (1520, 800)],
            stroke_style=StrokeStyle(color=BLUE, width=6.0),
            sketch_style=SKETCH
        )
        base_line = Line(start=(350, 800), end=(1570, 800), stroke_style=StrokeStyle(color=BLACK, width=4.0), sketch_style=SKETCH)
        
        mean_line = Line(start=(960, 300), end=(960, 800), stroke_style=StrokeStyle(color=DARK_GRAY, width=3.0, dash_length=10, dash_gap=10), sketch_style=SKETCH)
        math_mu = Math(tex_expression=r"$\mu = 0$", position=(960, 860), font_size=80, stroke_style=StrokeStyle(color=PURPLE, width=2.0), font_name=FONT_NAME)
        math_sigma = Math(tex_expression=r"$\sigma = 1$", position=(1150, 500), font_size=80, stroke_style=StrokeStyle(color=ORANGE, width=2.0), font_name=FONT_NAME)
        
        sigma_arrow = Arrow(start_point=(960, 550), end_point=(1100, 550), stroke_style=StrokeStyle(color=ORANGE, width=3.0))

        scene.add(SketchAnimation(start_time=norm_start + 0.5, duration=1.0), drawable=norm_title)
        scene.add(SketchAnimation(start_time=norm_start + 4.0, duration=0.5), drawable=p1)
        scene.add(SketchAnimation(start_time=norm_start + 4.2, duration=0.5), drawable=p2)
        scene.add(SketchAnimation(start_time=norm_start + 4.4, duration=0.5), drawable=p3)
        scene.add(SketchAnimation(start_time=norm_start + 5.0, duration=1.0), drawable=outlier_text)

        erase_outliers = Eraser([p1, p2, p3, outlier_text], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=norm_sol_start - 0.5, duration=1.0), drawable=erase_outliers)

        scene.add(SketchAnimation(start_time=norm_sol_start + 0.5, duration=1.0), drawable=base_line)
        scene.add(SketchAnimation(start_time=norm_sol_start + 1.5, duration=2.0), drawable=bell)
        scene.add(SketchAnimation(start_time=norm_sol_start + 4.0, duration=0.8), drawable=mean_line)
        scene.add(SketchAnimation(start_time=norm_sol_start + 5.0, duration=1.0), drawable=math_mu)
        scene.add(SketchAnimation(start_time=norm_sol_start + 6.5, duration=0.8), drawable=sigma_arrow)
        scene.add(SketchAnimation(start_time=norm_sol_start + 7.5, duration=1.0), drawable=math_sigma)

        norm_drawables.extend([norm_title, base_line, bell, mean_line, math_mu, sigma_arrow, math_sigma])

        # ---------------------------------------------------------
        # SECTION 4: PCA
        # ---------------------------------------------------------
        make_eraser(norm_drawables, start_time=pca_start - 1.2)
        pca_drawables =[]

        pca_title = make_title("3. Principal Component Analysis (PCA)", y=150, color=ORANGE)
        
        pca_prob = make_body("Curse of Dimensionality", x=960, y=250, color=RED, font_size=56)
        
        # PCA Graph setup
        ax_x = Line(start=(500, 850), end=(1400, 850), stroke_style=StrokeStyle(color=BLACK, width=4.0), sketch_style=SKETCH)
        ax_y = Line(start=(500, 850), end=(500, 300), stroke_style=StrokeStyle(color=BLACK, width=4.0), sketch_style=SKETCH)

        # Scatter points (2D blob diagonally)
        pts_coords =[(600, 750), (650, 780), (700, 680), (750, 700), (800, 650), (850, 600),
                      (900, 620), (950, 520), (1000, 550), (1050, 480), (1100, 500), (1150, 420),
                      (1200, 450), (1250, 380)]
        pts =[]
        fill = FillStyle(color=DARK_GRAY, opacity=1.0)
        for px, py in pts_coords:
            pts.append(Circle(center=(px, py), radius=10, fill_style=fill, stroke_style=StrokeStyle(color=BLACK), sketch_style=SKETCH))
        
        # PC1 Line
        pc1_line = Line(start=(550, 800), end=(1300, 350), stroke_style=StrokeStyle(color=BLUE, width=6.0), sketch_style=SKETCH)
        pc1_label = make_body("Principal Component 1", x=1350, y=300, color=BLUE, font_size=42)

        # Projections
        projections =[]
        # Slope of pc1 is roughly (350-800)/(1300-550) = -450/750 = -0.6
        for px, py in pts_coords:
            # Drop a small line onto the PC1 line visually
            proj_y = py + 30
            proj_x = px + 18
            proj = Line(start=(px, py), end=(proj_x, proj_y), stroke_style=StrokeStyle(color=RED, width=2.0, dash_length=5, dash_gap=5), sketch_style=SKETCH)
            projections.append(proj)

        one_d_text = make_body("2D projected perfectly to 1D!", x=960, y=950, color=GREEN, font_size=56)

        scene.add(SketchAnimation(start_time=pca_start + 0.5, duration=1.0), drawable=pca_title)
        scene.add(SketchAnimation(start_time=pca_start + 2.0, duration=1.0), drawable=pca_prob)
        
        scene.add(SketchAnimation(start_time=pca_sol_start + 0.5, duration=0.8), drawable=ax_x)
        scene.add(SketchAnimation(start_time=pca_sol_start + 0.5, duration=0.8), drawable=ax_y)
        
        for p in pts:
            scene.add(SketchAnimation(start_time=pca_sol_start + 2.0, duration=0.3), drawable=p)
            
        scene.add(SketchAnimation(start_time=pca_sol_start + 5.0, duration=1.5), drawable=pc1_line)
        scene.add(SketchAnimation(start_time=pca_sol_start + 6.5, duration=1.0), drawable=pc1_label)
        
        for proj in projections:
            scene.add(SketchAnimation(start_time=pca_vis_start + 1.0, duration=0.5), drawable=proj)
            
        scene.add(SketchAnimation(start_time=pca_vis_start + 4.0, duration=1.5), drawable=one_d_text)

        pca_drawables.extend([pca_title, pca_prob, ax_x, ax_y, pc1_line, pc1_label, one_d_text] + pts + projections)

        # ---------------------------------------------------------
        # SECTION 5: Outro
        # ---------------------------------------------------------
        make_eraser(pca_drawables, start_time=outro_start - 1.2)
        
        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("Better features = Better models.", y=600, color=BLACK, font_size=64)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.5), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 3.0, duration=1.5), drawable=outro_body)

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