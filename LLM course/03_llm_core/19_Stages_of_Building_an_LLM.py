"""
Whiteboard explainer: The 4 Stages of Building an LLM from Scratch

This scene is designed for a 1920x1080 landscape whiteboard animation 
with edge-tts narration, handwritten fonts, and progressive sketch animations. 
It heavily details the full pipeline: Data Collection, Pre-training, SFT, and Alignment (RLHF).
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts or uv add --dev edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, CurvedArrow, FlowchartProcess, Line
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output"
AUDIO_PATH = OUTPUT_DIR / "stages_of_llm_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "stages_of_llm_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> How do companies actually build a Large Language Model from scratch? "
    "Building a modern AI assistant is a massive engineering feat that happens in four major stages. "
    
    "<bookmark mark='stage1'/> Stage 1 is Data Collection and Preparation. "
    "First, you scrape trillions of words from the public internet, books, and code repositories. "
    "Then, you clean the data to remove spam and toxic content. "
    "Finally, you chop the text into numerical pieces called tokens. "
    
    "<bookmark mark='stage2'/> Stage 2 is Pre-training. This is the hardest and most expensive phase. "
    "Using thousands of GPUs running for months, the model simply learns to predict the next token. "
    "The result is a 'Base Model'. It has a massive brain full of world knowledge, but it doesn't know how to chat yet. "
    
    "<bookmark mark='stage3'/> Stage 3 is Supervised Fine-Tuning, or SFT. "
    "Now, we show the Base Model thousands of high-quality Question and Answer pairs written by humans. "
    "This teaches the model how to follow instructions, act as an assistant, and format its text properly. "
    
    "<bookmark mark='stage4'/> Stage 4 is Alignment, often done using RLHF—Reinforcement Learning from Human Feedback. "
    "Humans grade the model's answers, giving a thumbs up to good responses and a thumbs down to bad ones. "
    "This final polish makes the model Helpful, Honest, and Harmless. "
    
    "<bookmark mark='summary'/> To summarize: We gather data, pre-train a base model, fine-tune it for instructions, and align it with human values. "
    
    "<bookmark mark='outro'/> That is the complete pipeline to build an LLM. Thanks for watching!"
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

def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.2) -> None:
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
        stage1_start = tracker.bookmark_time("stage1")
        stage2_start = tracker.bookmark_time("stage2")
        stage3_start = tracker.bookmark_time("stage3")
        stage4_start = tracker.bookmark_time("stage4")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        box_stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Building an LLM from Scratch", y=350, color=BLUE)
        intro_sub = make_body("The 4 Major Stages", y=500, color=ORANGE, font_size=72)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)

        intro_drawables = [intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Stage 1 - Data
        # ---------------------------------------------------------
        make_eraser(intro_drawables, start_time=stage1_start - 1.2)
        stage1_drawables =[]

        s1_title = make_title("Stage 1: Data Collection", y=140, color=BLUE)
        
        # Pipeline Flow
        raw_data = FlowchartProcess("Raw Internet\nData", top_left=(200, 350), width=350, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        arr1 = Arrow(start_point=(550, 440), end_point=(780, 440), stroke_style=box_stroke)
        
        clean_data = FlowchartProcess("Data Cleaning\n(Remove Spam)", top_left=(780, 350), width=350, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        arr2 = Arrow(start_point=(1130, 440), end_point=(1360, 440), stroke_style=box_stroke)
        
        tokens = FlowchartProcess("Tokenization", top_left=(1360, 350), width=350, height=180, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)

        s1_bullets = make_bullet_list([
            "Scrape trillions of words (web, books, code)",
            "Filter out toxic and duplicate content",
            "Convert words into numerical tokens"
        ], y_start=650, x=450, font_size=48)

        scene.add(SketchAnimation(start_time=stage1_start + 0.5, duration=1.0), drawable=s1_title)
        
        scene.add(SketchAnimation(start_time=stage1_start + 2.0, duration=1.0), drawable=raw_data)
        scene.add(SketchAnimation(start_time=stage1_start + 5.5, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=stage1_start + 6.5, duration=1.0), drawable=clean_data)
        scene.add(SketchAnimation(start_time=stage1_start + 8.5, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=stage1_start + 9.5, duration=1.0), drawable=tokens)

        for i, b in enumerate(s1_bullets):
            scene.add(SketchAnimation(start_time=stage1_start + 11.0 + (i * 1.0), duration=0.8), drawable=b)

        stage1_drawables.extend([s1_title, raw_data, arr1, clean_data, arr2, tokens] + s1_bullets)

        # ---------------------------------------------------------
        # SECTION 3: Stage 2 - Pre-training
        # ---------------------------------------------------------
        make_eraser(stage1_drawables, start_time=stage2_start - 1.2)
        stage2_drawables =[]

        s2_title = make_title("Stage 2: Pre-Training", y=140, color=ORANGE)
        s2_sub = make_body("The hardest and most expensive phase.", y=260, color=DARK_GRAY, font_size=48)

        # GPU / Compute
        gpu_box = FlowchartProcess("Thousands of GPUs", top_left=(300, 350), width=350, height=120, font_size=40, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        time_box = FlowchartProcess("Months of Training", top_left=(1270, 350), width=350, height=120, font_size=40, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)

        arr_in_l = Arrow(start_point=(650, 410), end_point=(800, 480), stroke_style=box_stroke)
        arr_in_r = Arrow(start_point=(1270, 410), end_point=(1120, 480), stroke_style=box_stroke)

        # Core Task
        task_box = FlowchartProcess("Task: Predict the\nNext Token", top_left=(800, 450), width=320, height=160, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        
        arr_out = Arrow(start_point=(960, 610), end_point=(960, 700), stroke_style=StrokeStyle(color=ORANGE, width=6.0))

        # Output
        base_model = FlowchartProcess("THE BASE MODEL", top_left=(710, 700), width=500, height=150, font_size=56, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4, hachure_gap=8), stroke_style=StrokeStyle(color=GREEN, width=4.0))
        base_desc = make_body("Huge knowledge base, but cannot act as an assistant yet.", y=900, color=GREEN, font_size=46)

        scene.add(SketchAnimation(start_time=stage2_start + 0.5, duration=1.0), drawable=s2_title)
        scene.add(SketchAnimation(start_time=stage2_start + 1.5, duration=1.0), drawable=s2_sub)
        
        scene.add(SketchAnimation(start_time=stage2_start + 3.0, duration=1.0), drawable=gpu_box)
        scene.add(SketchAnimation(start_time=stage2_start + 4.0, duration=1.0), drawable=time_box)
        
        scene.add(SketchAnimation(start_time=stage2_start + 6.0, duration=0.5), drawable=arr_in_l)
        scene.add(SketchAnimation(start_time=stage2_start + 6.0, duration=0.5), drawable=arr_in_r)
        scene.add(SketchAnimation(start_time=stage2_start + 6.5, duration=1.5), drawable=task_box)

        scene.add(SketchAnimation(start_time=stage2_start + 9.0, duration=0.8), drawable=arr_out)
        scene.add(SketchAnimation(start_time=stage2_start + 10.0, duration=1.5), drawable=base_model)
        scene.add(SketchAnimation(start_time=stage2_start + 11.5, duration=1.0), drawable=base_desc)

        stage2_drawables.extend([s2_title, s2_sub, gpu_box, time_box, arr_in_l, arr_in_r, task_box, arr_out, base_model, base_desc])

        # ---------------------------------------------------------
        # SECTION 4: Stage 3 - SFT
        # ---------------------------------------------------------
        make_eraser(stage2_drawables, start_time=stage3_start - 1.2)
        stage3_drawables =[]

        s3_title = make_title("Stage 3: Supervised Fine-Tuning", y=140, color=GREEN)
        s3_sub = make_body("Teaching it to be an Assistant", y=260, color=DARK_GRAY, font_size=48)

        # Merge visual
        base_box = FlowchartProcess("Base Model", top_left=(400, 380), width=300, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        plus_sign = make_body("+", x=800, y=440, font_size=100)
        qa_box = FlowchartProcess("Human Q&A\nExamples", top_left=(900, 380), width=300, height=120, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)

        arr_merge1 = Arrow(start_point=(550, 500), end_point=(780, 650), stroke_style=box_stroke)
        arr_merge2 = Arrow(start_point=(1050, 500), end_point=(820, 650), stroke_style=box_stroke)

        ast_model = FlowchartProcess("ASSISTANT MODEL", top_left=(550, 650), width=500, height=150, font_size=56, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.4, hachure_gap=8), stroke_style=StrokeStyle(color=ORANGE, width=4.0))

        s3_desc = make_body("Now it knows how to follow instructions and format answers.", y=880, color=ORANGE, font_size=46)

        scene.add(SketchAnimation(start_time=stage3_start + 0.5, duration=1.0), drawable=s3_title)
        scene.add(SketchAnimation(start_time=stage3_start + 1.5, duration=1.0), drawable=s3_sub)

        scene.add(SketchAnimation(start_time=stage3_start + 3.0, duration=1.0), drawable=base_box)
        scene.add(SketchAnimation(start_time=stage3_start + 4.5, duration=0.5), drawable=plus_sign)
        scene.add(SketchAnimation(start_time=stage3_start + 5.5, duration=1.0), drawable=qa_box)

        scene.add(SketchAnimation(start_time=stage3_start + 7.5, duration=0.8), drawable=arr_merge1)
        scene.add(SketchAnimation(start_time=stage3_start + 7.5, duration=0.8), drawable=arr_merge2)
        scene.add(SketchAnimation(start_time=stage3_start + 8.5, duration=1.5), drawable=ast_model)
        
        scene.add(SketchAnimation(start_time=stage3_start + 10.5, duration=1.0), drawable=s3_desc)

        stage3_drawables.extend([s3_title, s3_sub, base_box, plus_sign, qa_box, arr_merge1, arr_merge2, ast_model, s3_desc])

        # ---------------------------------------------------------
        # SECTION 5: Stage 4 - Alignment
        # ---------------------------------------------------------
        make_eraser(stage3_drawables, start_time=stage4_start - 1.2)
        stage4_drawables =[]

        s4_title = make_title("Stage 4: Alignment (RLHF)", y=140, color=PURPLE)
        s4_sub = make_body("Reinforcement Learning from Human Feedback", y=260, color=DARK_GRAY, font_size=48)

        # Feedback loop
        ast_box = FlowchartProcess("Assistant Model", top_left=(400, 450), width=350, height=120, font_size=42, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        
        arr_right = Arrow(start_point=(750, 510), end_point=(1150, 510), stroke_style=box_stroke)
        
        feedback_box = FlowchartProcess("Human Grading", top_left=(1150, 450), width=350, height=120, font_size=42, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3, hachure_gap=8), stroke_style=box_stroke)
        
        thumbs = make_body("👍 Good    👎 Bad", x=1325, y=620, font_size=48, color=RED)
        
        arr_back = CurvedArrow(points=[(1325, 450), (950, 300), (575, 450)], stroke_style=StrokeStyle(color=PURPLE, width=4.0))
        punish_reward = make_body("Reward / Punish", x=950, y=280, font_size=42, color=PURPLE)

        final_desc = make_body("The Final Polish: Helpful, Honest, and Harmless", y=800, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=stage4_start + 0.5, duration=1.0), drawable=s4_title)
        scene.add(SketchAnimation(start_time=stage4_start + 1.5, duration=1.0), drawable=s4_sub)

        scene.add(SketchAnimation(start_time=stage4_start + 3.0, duration=1.0), drawable=ast_box)
        scene.add(SketchAnimation(start_time=stage4_start + 4.0, duration=0.8), drawable=arr_right)
        scene.add(SketchAnimation(start_time=stage4_start + 5.0, duration=1.0), drawable=feedback_box)
        scene.add(SketchAnimation(start_time=stage4_start + 6.0, duration=1.0), drawable=thumbs)
        
        scene.add(SketchAnimation(start_time=stage4_start + 7.5, duration=1.0), drawable=arr_back)
        scene.add(SketchAnimation(start_time=stage4_start + 8.0, duration=0.8), drawable=punish_reward)

        scene.add(SketchAnimation(start_time=stage4_start + 11.5, duration=1.5), drawable=final_desc)

        stage4_drawables.extend([s4_title, s4_sub, ast_box, arr_right, feedback_box, thumbs, arr_back, punish_reward, final_desc])

        # ---------------------------------------------------------
        # SECTION 6: Summary & Outro
        # ---------------------------------------------------------
        make_eraser(stage4_drawables, start_time=summary_start - 1.2)
        sum_drawables =[]

        sum_title = make_title("The Complete Pipeline", y=200, color=BLUE)

        b1 = FlowchartProcess("1. Data", top_left=(150, 450), width=300, height=120, font_size=52, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=box_stroke)
        a1 = Arrow(start_point=(450, 510), end_point=(560, 510), stroke_style=box_stroke)
        
        b2 = FlowchartProcess("2. Pre-Train", top_left=(560, 450), width=320, height=120, font_size=52, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=box_stroke)
        a2 = Arrow(start_point=(880, 510), end_point=(990, 510), stroke_style=box_stroke)

        b3 = FlowchartProcess("3. Fine-Tune", top_left=(990, 450), width=340, height=120, font_size=52, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=box_stroke)
        a3 = Arrow(start_point=(1330, 510), end_point=(1440, 510), stroke_style=box_stroke)

        b4 = FlowchartProcess("4. Align", top_left=(1440, 450), width=300, height=120, font_size=52, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=box_stroke)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        
        scene.add(SketchAnimation(start_time=summary_start + 1.5, duration=0.8), drawable=b1)
        scene.add(SketchAnimation(start_time=summary_start + 2.5, duration=0.5), drawable=a1)
        
        scene.add(SketchAnimation(start_time=summary_start + 3.0, duration=0.8), drawable=b2)
        scene.add(SketchAnimation(start_time=summary_start + 4.0, duration=0.5), drawable=a2)
        
        scene.add(SketchAnimation(start_time=summary_start + 4.5, duration=0.8), drawable=b3)
        scene.add(SketchAnimation(start_time=summary_start + 6.0, duration=0.5), drawable=a3)
        
        scene.add(SketchAnimation(start_time=summary_start + 6.5, duration=0.8), drawable=b4)

        sum_drawables.extend([sum_title, b1, a1, b2, a2, b3, a3, b4])

        make_eraser(sum_drawables, start_time=outro_start - 1.2)

        outro_title = make_title("Thanks for watching!", y=450, color=BLUE)
        outro_body = make_body("Now you know how AI models are built.", y=600, color=BLACK)

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
    print(VIDEO_PATH)


if __name__ == "__main__":
    main()