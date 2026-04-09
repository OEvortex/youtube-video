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
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "model_evaluation"
AUDIO_PATH = OUTPUT_DIR / "eval_deep_dive_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "eval_deep_dive_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome! Let's explore how we evaluate Machine Learning models. "
    "We'll cover Overfitting, Underfitting, the Bias-Variance Tradeoff, and Cross-Validation. "
    
    "<bookmark mark='fit'/> Imagine fitting a curve to data points. "
    "If our model is too simple, it ignores patterns. This is Underfitting. "
    "If it's too complex, it memorizes the noise, hitting every point but failing on new data. This is Overfitting. "
    "We want the 'Goldilocks' zone—a Good Fit! "
    
    "<bookmark mark='tradeoff'/> This brings us to the Bias-Variance Tradeoff. "
    "Underfitting means High Bias: the model makes strong, incorrect assumptions. "
    "Overfitting means High Variance: the model is too sensitive to the training data. "
    "As complexity increases, Bias drops but Variance spikes. "
    "The Total Error forms a U-shape. The lowest point is our Sweet Spot! "
    
    "<bookmark mark='cross_val'/> So, how do we find this sweet spot safely without memorizing our test data? We use Cross-Validation! "
    
    "<bookmark mark='kfold'/> Instead of one train-test split, we divide our data into 'K' equal chunks, or folds. "
    "In 5-fold cross validation, we train our model on 4 folds, and test it on the remaining 1. "
    "Then, we rotate the test fold! We repeat this process until every single fold has been used as the test set. "
    "Averaging these 5 scores gives us a highly reliable measure of true performance. "
    
    "<bookmark mark='outro'/> Mastering the bias-variance tradeoff with cross-validation is the key to building reliable AI models. Thanks for watching!"
)

BOOKMARK_RE = re.compile(r"<bookmark\s+(?:mark|name)\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

async def synthesize_narration(
    audio_path: Path, *, regenerate: bool = False, voice: str = VOICE
) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    if audio_path.exists():
        if audio_path.stat().st_size == 0:
            audio_path.unlink()
        elif not regenerate:
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

def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.2) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)

def draw_graph_axes(origin_x: float, origin_y: float, w: float, h: float) -> list:
    stroke = StrokeStyle(color=BLACK, width=4)
    x_axis = Line(start=(origin_x, origin_y), end=(origin_x + w, origin_y), stroke_style=stroke, sketch_style=SKETCH)
    y_axis = Line(start=(origin_x, origin_y), end=(origin_x, origin_y - h), stroke_style=stroke, sketch_style=SKETCH)
    return [x_axis, y_axis]

def draw_scatter_points(origin_x: float, origin_y: float) -> list:
    pts =[(30, -60), (90, -120), (140, -110), (190, -190), (250, -220)]
    drawables =[]
    fill = FillStyle(color=DARK_GRAY, opacity=1.0)
    stroke = StrokeStyle(color=BLACK, width=2)
    for dx, dy in pts:
        drawables.append(Circle(center=(origin_x + dx, origin_y + dy), radius=8, fill_style=fill, stroke_style=stroke, sketch_style=SKETCH))
    return drawables

scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()

def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        intro_start = tracker.bookmark_time("intro")
        fit_start = tracker.bookmark_time("fit")
        tradeoff_start = tracker.bookmark_time("tradeoff")
        cv_start = tracker.bookmark_time("cross_val")
        kfold_start = tracker.bookmark_time("kfold")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Model Evaluation Deep Dive", y=400, color=BLUE)
        intro_sub = make_body("Overfitting, Bias-Variance & Cross-Validation", y=550, color=ORANGE, font_size=56)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 3.0, duration=1.5), drawable=intro_sub)
        
        intro_drawables =[intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Overfitting vs Underfitting
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=fit_start - 1.2)
        fit_drawables =[]

        fit_title = make_title("The 'Fit' of a Model", y=120, color=GREEN)
        
        # Underfit Graph
        ax1 = draw_graph_axes(200, 750, 350, 350)
        pts1 = draw_scatter_points(200, 750)
        under_curve = Line(start=(220, 680), end=(520, 500), stroke_style=StrokeStyle(color=RED, width=5.0), sketch_style=SKETCH)
        under_label = make_body("Underfitting", x=375, y=820, color=RED, font_size=56)
        under_sub = make_body("Too Simple", x=375, y=880, color=DARK_GRAY, font_size=40)

        # Good Fit Graph
        ax2 = draw_graph_axes(780, 750, 350, 350)
        pts2 = draw_scatter_points(780, 750)
        good_curve = Curve(points=[(800, 710), (870, 620), (950, 570), (1030, 520), (1100, 500)], stroke_style=StrokeStyle(color=BLUE, width=5.0), sketch_style=SKETCH)
        good_label = make_body("Good Fit", x=955, y=820, color=BLUE, font_size=56)
        good_sub = make_body("Just Right", x=955, y=880, color=DARK_GRAY, font_size=40)

        # Overfit Graph
        ax3 = draw_graph_axes(1360, 750, 350, 350)
        pts3 = draw_scatter_points(1360, 750)
        over_curve = Curve(points=[(1380, 680), (1390, 690), (1420, 500), (1450, 630), (1500, 640), (1530, 480), (1550, 560), (1610, 530), (1680, 400)], stroke_style=StrokeStyle(color=ORANGE, width=5.0), sketch_style=SKETCH)
        over_label = make_body("Overfitting", x=1535, y=820, color=ORANGE, font_size=56)
        over_sub = make_body("Memorizes Noise", x=1535, y=880, color=DARK_GRAY, font_size=40)

        scene.add(SketchAnimation(start_time=fit_start + 0.5, duration=1.0), drawable=fit_title)
        
        # Animate Underfit
        for a in ax1: scene.add(SketchAnimation(start_time=fit_start + 1.5, duration=0.5), drawable=a)
        for p in pts1: scene.add(SketchAnimation(start_time=fit_start + 2.0, duration=0.5), drawable=p)
        scene.add(SketchAnimation(start_time=fit_start + 2.5, duration=1.0), drawable=under_curve)
        scene.add(SketchAnimation(start_time=fit_start + 3.5, duration=0.8), drawable=under_label)
        scene.add(SketchAnimation(start_time=fit_start + 4.0, duration=0.5), drawable=under_sub)

        # Animate Overfit
        for a in ax3: scene.add(SketchAnimation(start_time=fit_start + 6.0, duration=0.5), drawable=a)
        for p in pts3: scene.add(SketchAnimation(start_time=fit_start + 6.5, duration=0.5), drawable=p)
        scene.add(SketchAnimation(start_time=fit_start + 7.0, duration=1.5), drawable=over_curve)
        scene.add(SketchAnimation(start_time=fit_start + 8.5, duration=0.8), drawable=over_label)
        scene.add(SketchAnimation(start_time=fit_start + 9.0, duration=0.5), drawable=over_sub)

        # Animate Good Fit
        for a in ax2: scene.add(SketchAnimation(start_time=fit_start + 11.5, duration=0.5), drawable=a)
        for p in pts2: scene.add(SketchAnimation(start_time=fit_start + 12.0, duration=0.5), drawable=p)
        scene.add(SketchAnimation(start_time=fit_start + 12.5, duration=1.0), drawable=good_curve)
        scene.add(SketchAnimation(start_time=fit_start + 13.5, duration=0.8), drawable=good_label)
        scene.add(SketchAnimation(start_time=fit_start + 14.0, duration=0.5), drawable=good_sub)

        fit_drawables.extend([fit_title, under_curve, under_label, under_sub, good_curve, good_label, good_sub, over_curve, over_label, over_sub] + ax1 + ax2 + ax3 + pts1 + pts2 + pts3)

        # ---------------------------------------------------------
        # SECTION 3: Bias-Variance Tradeoff
        # ---------------------------------------------------------
        make_eraser(fit_drawables, start_time=tradeoff_start - 1.2)
        bv_drawables =[]

        bv_title = make_title("Bias-Variance Tradeoff", y=120, color=PURPLE)
        
        ax_bv = draw_graph_axes(560, 850, 800, 500)
        x_label = make_body("Model Complexity", x=960, y=920, color=BLACK, font_size=48)
        y_label = make_body("Error", x=480, y=600, color=BLACK, font_size=48)

        # Bias curve
        bias_curve = Curve(points=[(600, 400), (960, 750), (1300, 800)], stroke_style=StrokeStyle(color=BLUE, width=6.0), sketch_style=SKETCH)
        bias_label = make_body("Bias (Underfitting)", x=750, y=420, color=BLUE, font_size=42)

        # Variance curve
        var_curve = Curve(points=[(600, 800), (960, 750), (1300, 400)], stroke_style=StrokeStyle(color=RED, width=6.0), sketch_style=SKETCH)
        var_label = make_body("Variance (Overfitting)", x=1180, y=420, color=RED, font_size=42)

        # Total Error curve
        total_curve = Curve(points=[(600, 350), (750, 480), (960, 550), (1150, 480), (1300, 350)], stroke_style=StrokeStyle(color=PURPLE, width=8.0), sketch_style=SKETCH)
        total_label = make_body("Total Error", x=960, y=320, color=PURPLE, font_size=52)
        
        # Sweet Spot
        sweet_spot_line = Line(start=(960, 850), end=(960, 550), stroke_style=StrokeStyle(color=GREEN, width=4.0), sketch_style=SKETCH)
        sweet_label = FlowchartProcess("Sweet Spot", top_left=(860, 450), width=200, height=80, font_size=36, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.8), stroke_style=box_stroke)

        scene.add(SketchAnimation(start_time=tradeoff_start + 0.5, duration=1.0), drawable=bv_title)
        for a in ax_bv: scene.add(SketchAnimation(start_time=tradeoff_start + 1.5, duration=0.5), drawable=a)
        scene.add(SketchAnimation(start_time=tradeoff_start + 2.0, duration=0.5), drawable=x_label)
        scene.add(SketchAnimation(start_time=tradeoff_start + 2.0, duration=0.5), drawable=y_label)

        scene.add(SketchAnimation(start_time=tradeoff_start + 4.0, duration=1.5), drawable=bias_curve)
        scene.add(SketchAnimation(start_time=tradeoff_start + 5.5, duration=0.8), drawable=bias_label)
        
        scene.add(SketchAnimation(start_time=tradeoff_start + 8.5, duration=1.5), drawable=var_curve)
        scene.add(SketchAnimation(start_time=tradeoff_start + 10.0, duration=0.8), drawable=var_label)
        
        scene.add(SketchAnimation(start_time=tradeoff_start + 15.0, duration=2.0), drawable=total_curve)
        scene.add(SketchAnimation(start_time=tradeoff_start + 17.0, duration=1.0), drawable=total_label)

        scene.add(SketchAnimation(start_time=tradeoff_start + 19.0, duration=1.0), drawable=sweet_spot_line)
        scene.add(SketchAnimation(start_time=tradeoff_start + 20.0, duration=1.0), drawable=sweet_label)

        bv_drawables.extend([bv_title, x_label, y_label, bias_curve, bias_label, var_curve, var_label, total_curve, total_label, sweet_spot_line, sweet_label] + ax_bv)

        # ---------------------------------------------------------
        # SECTION 4: Cross-Validation
        # ---------------------------------------------------------
        make_eraser(bv_drawables, start_time=cv_start - 1.2)
        cv_drawables =[]

        cv_title = make_title("K-Fold Cross-Validation", y=120, color=ORANGE)
        
        # Folds layout
        box_w = 220
        box_h = 100
        start_x = 350
        start_y = 400
        gap = 20
        
        # Header
        col_labels =[make_body(f"Fold {i}", x=start_x + (i-1)*(box_w+gap) + box_w/2, y=320, font_size=40, color=DARK_GRAY) for i in range(1, 6)]
        
        def make_cv_row(row_idx, test_idx, label_text):
            row_y = start_y + row_idx * (box_h + gap + 30)
            lbl = make_body(label_text, x=200, y=row_y + box_h/2, color=BLACK, font_size=42, align="left")
            boxes =[]
            for col in range(5):
                is_test = (col == test_idx)
                f_color = PASTEL_ORANGE if is_test else PASTEL_BLUE
                t_color = ORANGE if is_test else BLUE
                t_text = "TEST" if is_test else "TRAIN"
                
                rect = Rectangle(top_left=(start_x + col*(box_w+gap), row_y), width=box_w, height=box_h, stroke_style=box_stroke, fill_style=FillStyle(color=f_color, opacity=0.5), sketch_style=SKETCH)
                txt = make_body(t_text, x=start_x + col*(box_w+gap) + box_w/2, y=row_y + box_h/2, color=t_color, font_size=40)
                boxes.extend([rect, txt])
            return lbl, boxes

        lbl1, boxes1 = make_cv_row(0, 4, "Iteration 1:")
        lbl2, boxes2 = make_cv_row(1, 3, "Iteration 2:")
        lbl3, boxes3 = make_cv_row(2, 2, "Iteration 3:")
        
        dots = make_body("...", x=960, y=880, color=BLACK, font_size=80)
        avg_text = make_body("Average all scores for true model performance!", x=960, y=950, color=GREEN, font_size=56)

        scene.add(SketchAnimation(start_time=cv_start + 0.5, duration=1.0), drawable=cv_title)
        
        for cl in col_labels:
            scene.add(SketchAnimation(start_time=kfold_start + 0.5, duration=0.5), drawable=cl)
            
        scene.add(SketchAnimation(start_time=kfold_start + 2.0, duration=0.5), drawable=lbl1)
        for b in boxes1:
            scene.add(SketchAnimation(start_time=kfold_start + 3.0, duration=1.0), drawable=b)
            
        scene.add(SketchAnimation(start_time=kfold_start + 7.5, duration=0.5), drawable=lbl2)
        for b in boxes2:
            scene.add(SketchAnimation(start_time=kfold_start + 8.5, duration=1.0), drawable=b)
            
        scene.add(SketchAnimation(start_time=kfold_start + 11.0, duration=0.5), drawable=lbl3)
        for b in boxes3:
            scene.add(SketchAnimation(start_time=kfold_start + 11.5, duration=1.0), drawable=b)
            
        scene.add(SketchAnimation(start_time=kfold_start + 12.5, duration=1.0), drawable=dots)
        scene.add(SketchAnimation(start_time=kfold_start + 15.0, duration=1.5), drawable=avg_text)

        cv_drawables.extend([cv_title, lbl1, lbl2, lbl3, dots, avg_text] + col_labels + boxes1 + boxes2 + boxes3)

        # ---------------------------------------------------------
        # SECTION 5: Outro
        # ---------------------------------------------------------
        make_eraser(cv_drawables, start_time=outro_start - 1.2)
        
        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("You've mastered Model Evaluation.", y=600, color=BLACK, font_size=64)

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
    print(f"Video saved to: {VIDEO_PATH}")
if __name__ == "__main__":
    main()