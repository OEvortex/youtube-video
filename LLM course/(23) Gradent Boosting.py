
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
from handanim.primitives import Arrow, Circle, FlowchartProcess, Line, Table
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "gbms"
AUDIO_PATH = OUTPUT_DIR / "gbm_deep_dive_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "gbm_deep_dive_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome! Today we are exploring Gradient Boosting Machines, "
    "and comparing three absolute titans: XGBoost, LightGBM, and CatBoost. "
    
    "<bookmark mark='core_concept'/> But first, what is Gradient Boosting? "
    "It is an ensemble learning technique. Instead of training one massive model, "
    "it combines many weak learners, which are typically simple decision trees. "
    "<bookmark mark='core_seq'/> Each new tree is trained specifically to correct the errors, or 'gradients', made by the previous trees. "
    "They work together like a team, sequentially improving the final prediction. "
    
    "<bookmark mark='xgboost'/> Let's look at the first titan: XGBoost, or eXtreme Gradient Boosting. "
    "Created by Tianqi Chen in 2014, it quickly became the king of Kaggle competitions. "
    "<bookmark mark='xgb_bullet'/> XGBoost's superpower is its mathematical rigor. It uses second-order gradients and advanced regularization "
    "to aggressively prevent overfitting. It is the gold standard for robust, accurate predictions. "
    
    "<bookmark mark='lightgbm'/> Next up is LightGBM, developed by Microsoft. "
    "As datasets grew massive, XGBoost could be slow. LightGBM solved this by focusing on sheer speed. "
    "<bookmark mark='lgbm_tree'/> Instead of growing trees level-by-level, it grows them leaf-by-leaf. "
    "Combined with histogram-based splitting, LightGBM trains incredibly fast while using much less memory. "
    
    "<bookmark mark='catboost'/> Finally, we have CatBoost, created by Yandex. "
    "In many real-world datasets, we have categorical data, like text labels or IDs, which normally require tedious preprocessing. "
    "<bookmark mark='cat_magic'/> CatBoost handles categories natively, without needing one-hot encoding. "
    "It also uses a brilliant technique called 'ordered boosting' to prevent data leakage, making it incredibly accurate out of the box. "
    
    "<bookmark mark='summary'/> To summarize: use XGBoost for battle-tested robustness, LightGBM for massive datasets and speed, "
    "and CatBoost when dealing with a lot of categorical variables. Thanks for watching!"
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

def make_bullet_list(
    lines: list[str],
    *,
    y_start: float,
    x: float = 300,
    color: tuple[float, float, float] = BLACK,
    y_step: float = 85,
    font_size: float = 50,
) -> list[Text]:
    return[
        Text(
            f"• {line}",
            position=(x, y_start + i * y_step),
            font_size=font_size,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=color, width=3.5),
            sketch_style=SKETCH,
            align="left",
        )
        for i, line in enumerate(lines)
    ]

def draw_mini_tree(root_x: float, root_y: float, style: str, color_fill: FillStyle) -> list:
    drawables =[]
    stroke = StrokeStyle(color=BLACK, width=3)
    
    c1 = Circle(center=(root_x, root_y), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
    
    c2 = Circle(center=(root_x - 100, root_y + 100), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
    c3 = Circle(center=(root_x + 100, root_y + 100), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
    
    l1 = Line(start=(root_x, root_y+25), end=(root_x - 100, root_y + 75), stroke_style=stroke, sketch_style=SKETCH)
    l2 = Line(start=(root_x, root_y+25), end=(root_x + 100, root_y + 75), stroke_style=stroke, sketch_style=SKETCH)
    
    drawables.extend([l1, l2, c1, c2, c3])
    
    if style == "level":
        c4 = Circle(center=(root_x - 150, root_y + 200), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        c5 = Circle(center=(root_x - 50, root_y + 200), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        l3 = Line(start=(root_x - 100, root_y+125), end=(root_x - 150, root_y + 175), stroke_style=stroke, sketch_style=SKETCH)
        l4 = Line(start=(root_x - 100, root_y+125), end=(root_x - 50, root_y + 175), stroke_style=stroke, sketch_style=SKETCH)
        
        c6 = Circle(center=(root_x + 50, root_y + 200), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        c7 = Circle(center=(root_x + 150, root_y + 200), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        l5 = Line(start=(root_x + 100, root_y+125), end=(root_x + 50, root_y + 175), stroke_style=stroke, sketch_style=SKETCH)
        l6 = Line(start=(root_x + 100, root_y+125), end=(root_x + 150, root_y + 175), stroke_style=stroke, sketch_style=SKETCH)
        
        drawables.extend([l3, l4, l5, l6, c4, c5, c6, c7])
        
    elif style == "leaf":
        c4 = Circle(center=(root_x - 150, root_y + 200), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        c5 = Circle(center=(root_x - 50, root_y + 200), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        l3 = Line(start=(root_x - 100, root_y+125), end=(root_x - 150, root_y + 175), stroke_style=stroke, sketch_style=SKETCH)
        l4 = Line(start=(root_x - 100, root_y+125), end=(root_x - 50, root_y + 175), stroke_style=stroke, sketch_style=SKETCH)
        
        c6 = Circle(center=(root_x - 100, root_y + 300), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        c7 = Circle(center=(root_x, root_y + 300), radius=25, fill_style=color_fill, stroke_style=stroke, sketch_style=SKETCH)
        l5 = Line(start=(root_x - 50, root_y+225), end=(root_x - 100, root_y + 275), stroke_style=stroke, sketch_style=SKETCH)
        l6 = Line(start=(root_x - 50, root_y+225), end=(root_x, root_y + 275), stroke_style=stroke, sketch_style=SKETCH)
        
        drawables.extend([l3, l4, l5, l6, c4, c5, c6, c7])
        
    return drawables

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
        core_start = tracker.bookmark_time("core_concept")
        core_seq_start = tracker.bookmark_time("core_seq")
        xgb_start = tracker.bookmark_time("xgboost")
        xgb_bullet_start = tracker.bookmark_time("xgb_bullet")
        lgbm_start = tracker.bookmark_time("lightgbm")
        lgbm_tree_start = tracker.bookmark_time("lgbm_tree")
        cat_start = tracker.bookmark_time("catboost")
        cat_magic_start = tracker.bookmark_time("cat_magic")
        summary_start = tracker.bookmark_time("summary")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Gradient Boosting Machines", y=400, color=BLUE)
        intro_sub = make_body("XGBoost vs LightGBM vs CatBoost", y=550, color=ORANGE, font_size=64)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 3.0, duration=1.5), drawable=intro_sub)
        
        intro_drawables =[intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Core Concept
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=core_start - 1.2)
        core_drawables =[]

        core_title = make_title("What is Gradient Boosting?", y=150, color=GREEN)
        
        tree1 = FlowchartProcess("Tree 1\n(Weak)", top_left=(200, 450), width=300, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=box_stroke)
        
        arr1 = Arrow(start_point=(500, 540), end_point=(750, 540), stroke_style=box_stroke)
        res1 = make_body("- Residuals", x=625, y=490, font_size=40, color=RED)
        tree2 = FlowchartProcess("Tree 2\n(Fixes Tree 1)", top_left=(750, 450), width=380, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=box_stroke)
        
        arr2 = Arrow(start_point=(1130, 540), end_point=(1380, 540), stroke_style=box_stroke)
        res2 = make_body("- Residuals", x=1255, y=490, font_size=40, color=RED)
        tree3 = FlowchartProcess("Tree 3\n(Fixes Tree 2)", top_left=(1380, 450), width=380, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)
        
        seq_label = make_body("Sequential Error Correction", x=960, y=800, font_size=64, color=BLUE)

        scene.add(SketchAnimation(start_time=core_start + 0.5, duration=1.0), drawable=core_title)
        scene.add(SketchAnimation(start_time=core_start + 3.0, duration=1.5), drawable=tree1)
        
        scene.add(SketchAnimation(start_time=core_seq_start + 0.5, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=core_seq_start + 1.0, duration=0.8), drawable=res1)
        scene.add(SketchAnimation(start_time=core_seq_start + 1.5, duration=1.5), drawable=tree2)
        
        scene.add(SketchAnimation(start_time=core_seq_start + 3.0, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=core_seq_start + 3.5, duration=0.8), drawable=res2)
        scene.add(SketchAnimation(start_time=core_seq_start + 4.0, duration=1.5), drawable=tree3)
        
        scene.add(SketchAnimation(start_time=core_seq_start + 6.0, duration=1.5), drawable=seq_label)

        core_drawables.extend([core_title, tree1, arr1, res1, tree2, arr2, res2, tree3, seq_label])

        # ---------------------------------------------------------
        # SECTION 3: XGBoost
        # ---------------------------------------------------------
        make_eraser(core_drawables, start_time=xgb_start - 1.2)
        xgb_drawables =[]

        xgb_title = make_title("XGBoost (2014)", y=150, color=RED)
        xgb_box = FlowchartProcess("eXtreme Gradient Boosting", top_left=(660, 250), width=600, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.2), stroke_style=box_stroke)
        
        xgb_bullets = make_bullet_list([
            "King of Kaggle Competitions",
            "Second-Order Gradients (Newton-Raphson)",
            "Advanced L1 & L2 Regularization",
            "Gold Standard for Robustness"
        ], y_start=500, x=450, font_size=56, y_step=100)

        scene.add(SketchAnimation(start_time=xgb_start + 0.5, duration=1.0), drawable=xgb_title)
        scene.add(SketchAnimation(start_time=xgb_start + 2.0, duration=1.5), drawable=xgb_box)
        
        for i, b in enumerate(xgb_bullets):
            scene.add(SketchAnimation(start_time=xgb_bullet_start + (i * 2.0), duration=1.5), drawable=b)

        xgb_drawables.extend([xgb_title, xgb_box] + xgb_bullets)

        # ---------------------------------------------------------
        # SECTION 4: LightGBM
        # ---------------------------------------------------------
        make_eraser(xgb_drawables, start_time=lgbm_start - 1.2)
        lgbm_drawables =[]

        lgbm_title = make_title("LightGBM (Microsoft)", y=120, color=BLUE)
        lgbm_sub = make_body("Built for Sheer Speed & Massive Data", y=220, color=DARK_GRAY, font_size=56)
        
        level_label = make_body("Level-Wise Growth\n(XGBoost)", x=500, y=380, font_size=48, color=BLACK)
        level_tree = draw_mini_tree(500, 500, "level", FillStyle(color=PASTEL_BLUE, opacity=0.8))
        
        leaf_label = make_body("Leaf-Wise Growth\n(LightGBM)", x=1400, y=380, font_size=48, color=ORANGE)
        leaf_tree = draw_mini_tree(1400, 500, "leaf", FillStyle(color=PASTEL_ORANGE, opacity=0.8))

        lgbm_bullets = make_bullet_list([
            "Grows trees leaf-by-leaf (lower loss)",
            "Histogram-based binning for speed",
            "Extremely low memory usage"
        ], y_start=800, x=500, font_size=56, y_step=90)

        scene.add(SketchAnimation(start_time=lgbm_start + 0.5, duration=1.0), drawable=lgbm_title)
        scene.add(SketchAnimation(start_time=lgbm_start + 2.0, duration=1.5), drawable=lgbm_sub)
        
        scene.add(SketchAnimation(start_time=lgbm_tree_start + 0.5, duration=1.0), drawable=level_label)
        for i, td in enumerate(level_tree):
            scene.add(SketchAnimation(start_time=lgbm_tree_start + 1.5 + (i * 0.15), duration=0.8), drawable=td)
            
        scene.add(SketchAnimation(start_time=lgbm_tree_start + 3.0, duration=1.0), drawable=leaf_label)
        for i, td in enumerate(leaf_tree):
            scene.add(SketchAnimation(start_time=lgbm_tree_start + 4.0 + (i * 0.15), duration=0.8), drawable=td)

        for i, b in enumerate(lgbm_bullets):
            scene.add(SketchAnimation(start_time=lgbm_tree_start + 6.5 + (i * 2.0), duration=1.5), drawable=b)

        lgbm_drawables.extend([lgbm_title, lgbm_sub, level_label, leaf_label] + level_tree + leaf_tree + lgbm_bullets)

        # ---------------------------------------------------------
        # SECTION 5: CatBoost
        # ---------------------------------------------------------
        make_eraser(lgbm_drawables, start_time=cat_start - 1.2)
        cat_drawables =[]

        cat_title = make_title("CatBoost (Yandex)", y=150, color=PURPLE)
        cat_sub = make_body("Categorical Data Mastery", y=250, color=DARK_GRAY, font_size=56)
        
        cat_table = Table(
            data=[
                ["ID", "City", "Price"],["1", "Paris", "$150"],
                ["2", "Tokyo", "$120"],["3", "Paris", "$200"]
            ],
            top_left=(250, 400),
            col_widths=[150, 250, 200],
            row_heights=[80, 80, 80, 80],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.5),
            fill_style=FillStyle(color=WHITE),
            stroke_style=box_stroke,
            sketch_style=SKETCH
        )
        
        arr_cat = Arrow(start_point=(900, 560), end_point=(1150, 560), stroke_style=box_stroke)
        cat_magic_box = FlowchartProcess("Native Processing!\n(No One-Hot Encoding)", top_left=(1150, 480), width=500, height=160, font_size=42, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)

        cat_bullets = make_bullet_list([
            "Handles categorical features automatically",
            "Uses 'Ordered Boosting' to prevent data leakage",
            "Highly accurate out-of-the-box"
        ], y_start=750, x=350, font_size=56, y_step=90)

        scene.add(SketchAnimation(start_time=cat_start + 0.5, duration=1.0), drawable=cat_title)
        scene.add(SketchAnimation(start_time=cat_start + 2.0, duration=1.5), drawable=cat_sub)
        scene.add(SketchAnimation(start_time=cat_start + 3.5, duration=2.0), drawable=cat_table)
        
        scene.add(SketchAnimation(start_time=cat_magic_start + 0.5, duration=1.0), drawable=arr_cat)
        scene.add(SketchAnimation(start_time=cat_magic_start + 1.5, duration=1.5), drawable=cat_magic_box)
        
        for i, b in enumerate(cat_bullets):
            scene.add(SketchAnimation(start_time=cat_magic_start + 3.5 + (i * 2.0), duration=1.5), drawable=b)

        cat_drawables.extend([cat_title, cat_sub, cat_table, arr_cat, cat_magic_box] + cat_bullets)

        # ---------------------------------------------------------
        # SECTION 6: Summary
        # ---------------------------------------------------------
        make_eraser(cat_drawables, start_time=summary_start - 1.2)
        sum_drawables =[]

        sum_title = make_title("The Ultimate Trio", y=150, color=BLACK)
        
        sum_table = Table(
            data=[
                ["Framework", "Core Philosophy", "Key Feature"],["XGBoost", "Robust & Battle-Tested", "2nd-Order Gradients"],["LightGBM", "Lightning Fast", "Leaf-Wise Growth"],
                ["CatBoost", "Categorical Master", "Ordered Boosting"]
            ],
            top_left=(200, 350),
            col_widths=[350, 550, 600],
            row_heights=[100, 120, 120, 120],
            font_size=48,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=box_stroke,
            sketch_style=SKETCH
        )
        
        outro_text = make_body("Thanks for watching!", y=950, color=BLUE, font_size=64)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 2.0, duration=3.0), drawable=sum_table)
        scene.add(SketchAnimation(start_time=tracker.end_time - 3.0, duration=1.5), drawable=outro_text)

        sum_drawables.extend([sum_title, sum_table, outro_text])

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