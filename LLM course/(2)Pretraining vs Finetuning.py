"""
Whiteboard explainer: Pretraining vs Fine-tuning

This scene is designed for a whiteboard animation style with edge-tts narration,
handwritten fonts, and progressive sketch animations.
"""

from __future__ import annotations

import asyncio
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
from handanim.stylings.color import BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE


WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = ROOT / "output"
AUDIO_PATH = OUTPUT_DIR / "pretrain_vs_finetune_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "pretrain_vs_finetune_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.0, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='hook'/> What is the difference between pretraining and fine-tuning? "
    "These are the two main phases of building a modern AI model. "
    "<bookmark mark='overview'/> Think of pretraining as general education, "
    "and fine-tuning as specialized training for a specific job. "
    "<bookmark mark='pretrain_def'/> Pretraining is where the model learns from massive amounts of data. "
    "It reads billions of words from the internet, books, and articles. "
    "The goal is to learn language patterns, grammar, facts, and reasoning skills. "
    "<bookmark mark='pretrain_cost'/> Pretraining is expensive. "
    "It requires thousands of GPUs running for weeks or months. "
    "The result is a base model that knows a lot, but is not yet specialized. "
    "<bookmark mark='finetune_def'/> Fine-tuning takes that base model and adapts it. "
    "You train it on a smaller, focused dataset for a specific task. "
    "This could be medical diagnosis, legal document review, or customer support. "
    "<bookmark mark='finetune_cost'/> Fine-tuning is much cheaper and faster. "
    "It might take just a few hours on a single GPU. "
    "The model keeps its general knowledge but becomes expert at one thing. "
    "<bookmark mark='analogy'/> Here is a simple analogy. "
    "Pretraining is like going to medical school for four years. "
    "Fine-tuning is like doing a one-year residency in cardiology. "
    "You already know medicine, now you specialize. "
    "<bookmark mark='comparison'/> Let us compare them side by side. "
    "Pretraining uses huge general datasets. Fine-tuning uses small focused datasets. "
    "Pretraining takes weeks on many GPUs. Fine-tuning takes hours on one GPU. "
    "Pretraining builds general knowledge. Fine-tuning builds task expertise. "
    "<bookmark mark='why_both'/> Why do we need both? "
    "Without pretraining, the model starts from zero and knows nothing. "
    "Without fine-tuning, the model is too general and may not follow instructions well. "
    "Together, they create a model that is both knowledgeable and useful. "
    "<bookmark mark='modern_approach'/> In modern AI, there is often a third step called alignment. "
    "This uses techniques like reinforcement learning to make the model helpful, honest, and harmless. "
    "But pretraining and fine-tuning remain the foundation. "
    "<bookmark mark='takeaway'/> So remember: pretraining gives the model its brain, "
    "and fine-tuning gives it its job. "
    "<bookmark mark='outro'/> Thanks for watching! "
    "Next video: How transformers actually work under the hood."
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
        font_size=110,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=4.0),
        sketch_style=SKETCH,
    )


def make_subtitle(text: str, *, y: float, color: tuple[float, float, float] = BLACK) -> Text:
    return Text(
        text,
        position=(960, y),
        font_size=64,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=3.5),
        sketch_style=SKETCH,
    )


def make_body(
    text: str, *, y: float, color: tuple[float, float, float] = BLACK, align: str = "center"
) -> Text:
    return Text(
        text,
        position=(960, y),
        font_size=56,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=3.5),
        sketch_style=SKETCH,
        align=align,
        line_spacing=1.3,
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
    return [
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


def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.5) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.6, 0.6, 0.6), "radius": 10},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()


def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        hook_start = tracker.bookmark_time("hook")
        overview_start = tracker.bookmark_time("overview")
        pretrain_def_start = tracker.bookmark_time("pretrain_def")
        pretrain_cost_start = tracker.bookmark_time("pretrain_cost")
        finetune_def_start = tracker.bookmark_time("finetune_def")
        finetune_cost_start = tracker.bookmark_time("finetune_cost")
        analogy_start = tracker.bookmark_time("analogy")
        comparison_start = tracker.bookmark_time("comparison")
        why_both_start = tracker.bookmark_time("why_both")
        modern_start = tracker.bookmark_time("modern_approach")
        takeaway_start = tracker.bookmark_time("takeaway")
        outro_start = tracker.bookmark_time("outro")

        # --- Section 1: Hook ---
        hook_title = make_title("Pretraining vs Fine-tuning", y=180, color=BLUE)
        hook_subtitle = make_subtitle(
            "The two phases of building an AI model", y=340, color=BLACK
        )
        hook_note = make_body("One builds knowledge. The other builds expertise.", y=520, color=ORANGE)

        scene.add(SketchAnimation(start_time=hook_start, duration=2.0), drawable=hook_title)
        scene.add(
            SketchAnimation(start_time=hook_start + 1.5, duration=1.8), drawable=hook_subtitle
        )
        scene.add(SketchAnimation(start_time=hook_start + 2.8, duration=1.2), drawable=hook_note)

        hook_drawables = [hook_title, hook_subtitle, hook_note]

        # --- Section 2: Overview ---
        make_eraser(hook_drawables, start_time=overview_start - 0.3, duration=1.2)

        over_title = make_title("The Big Picture", y=160, color=BLUE)
        over_left_title = Text(
            "Pretraining",
            position=(480, 320),
            font_size=72,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=GREEN, width=4.0),
            sketch_style=SKETCH,
        )
        over_left_body = Text(
            "General Education",
            position=(480, 400),
            font_size=52,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=BLACK, width=3.0),
            sketch_style=SKETCH,
        )
        over_right_title = Text(
            "Fine-tuning",
            position=(1440, 320),
            font_size=72,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=RED, width=4.0),
            sketch_style=SKETCH,
        )
        over_right_body = Text(
            "Specialized Training",
            position=(1440, 400),
            font_size=52,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=BLACK, width=3.0),
            sketch_style=SKETCH,
        )
        over_arrow = Text(
            "→",
            position=(960, 360),
            font_size=80,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=ORANGE, width=4.0),
            sketch_style=SKETCH,
        )
        over_note = make_body(
            "First learn broadly, then specialize.", y=560, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=overview_start + 0.5, duration=1.5), drawable=over_title)
        scene.add(SketchAnimation(start_time=overview_start + 1.5, duration=1.2), drawable=over_left_title)
        scene.add(SketchAnimation(start_time=overview_start + 2.2, duration=1.0), drawable=over_left_body)
        scene.add(SketchAnimation(start_time=overview_start + 2.8, duration=0.8), drawable=over_arrow)
        scene.add(SketchAnimation(start_time=overview_start + 3.2, duration=1.2), drawable=over_right_title)
        scene.add(SketchAnimation(start_time=overview_start + 3.8, duration=1.0), drawable=over_right_body)
        scene.add(SketchAnimation(start_time=overview_start + 4.5, duration=1.2), drawable=over_note)

        over_drawables = [over_title, over_left_title, over_left_body, over_arrow, over_right_title, over_right_body, over_note]

        # --- Section 3: Pretraining Definition ---
        make_eraser(over_drawables, start_time=pretrain_def_start - 0.3, duration=1.2)

        pt_title = make_title("Pretraining: Learning from Data", y=160, color=GREEN)
        pt_bullets = make_bullet_list(
            [
                "reads billions of words from the internet",
                "learns grammar, facts, and reasoning",
                "predicts the next word in a sentence",
                "builds a general understanding of language",
            ],
            y_start=300,
            color=BLACK,
        )
        pt_note = make_body(
            "The model learns patterns, not memorization.", y=620, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=pretrain_def_start + 0.5, duration=1.5), drawable=pt_title)
        for i, bullet in enumerate(pt_bullets):
            scene.add(
                SketchAnimation(start_time=pretrain_def_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=pretrain_def_start + 4.5, duration=1.2), drawable=pt_note)

        pt_drawables = [pt_title] + pt_bullets + [pt_note]

        # --- Section 4: Pretraining Cost ---
        make_eraser(pt_drawables, start_time=pretrain_cost_start - 0.3, duration=1.2)

        ptc_title = make_title("Pretraining is Expensive", y=160, color=RED)
        ptc_bullets = make_bullet_list(
            [
                "thousands of GPUs running for weeks",
                "terabytes of training data",
                "costs millions of dollars",
                "only a few companies can afford it",
            ],
            y_start=300,
            color=BLACK,
        )
        ptc_note = make_body(
            "The result is a base model — smart but not specialized.", y=620, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=pretrain_cost_start + 0.5, duration=1.5), drawable=ptc_title)
        for i, bullet in enumerate(ptc_bullets):
            scene.add(
                SketchAnimation(start_time=pretrain_cost_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=pretrain_cost_start + 4.5, duration=1.2), drawable=ptc_note)

        ptc_drawables = [ptc_title] + ptc_bullets + [ptc_note]

        # --- Section 5: Fine-tuning Definition ---
        make_eraser(ptc_drawables, start_time=finetune_def_start - 0.3, duration=1.2)

        ft_title = make_title("Fine-tuning: Specializing", y=160, color=RED)
        ft_bullets = make_bullet_list(
            [
                "takes a pretrained base model",
                "trains on a small focused dataset",
                "adapts to a specific task or domain",
                "keeps general knowledge, gains expertise",
            ],
            y_start=300,
            color=BLACK,
        )
        ft_note = make_body(
            "Examples: medical AI, legal assistant, coding helper.", y=620, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=finetune_def_start + 0.5, duration=1.5), drawable=ft_title)
        for i, bullet in enumerate(ft_bullets):
            scene.add(
                SketchAnimation(start_time=finetune_def_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=finetune_def_start + 4.5, duration=1.2), drawable=ft_note)

        ft_drawables = [ft_title] + ft_bullets + [ft_note]

        # --- Section 6: Fine-tuning Cost ---
        make_eraser(ft_drawables, start_time=finetune_cost_start - 0.3, duration=1.2)

        ftc_title = make_title("Fine-tuning is Affordable", y=160, color=GREEN)
        ftc_bullets = make_bullet_list(
            [
                "hours on a single GPU",
                "thousands of examples, not billions",
                "costs dollars to hundreds of dollars",
                "anyone with a dataset can do it",
            ],
            y_start=300,
            color=BLACK,
        )
        ftc_note = make_body(
            "This is how most custom AI applications are built.", y=620, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=finetune_cost_start + 0.5, duration=1.5), drawable=ftc_title)
        for i, bullet in enumerate(ftc_bullets):
            scene.add(
                SketchAnimation(start_time=finetune_cost_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=finetune_cost_start + 4.5, duration=1.2), drawable=ftc_note)

        ftc_drawables = [ftc_title] + ftc_bullets + [ftc_note]

        # --- Section 7: Analogy ---
        make_eraser(ftc_drawables, start_time=analogy_start - 0.3, duration=1.2)

        ana_title = make_title("A Simple Analogy", y=160, color=BLUE)
        ana_left_title = Text(
            "Medical School",
            position=(480, 300),
            font_size=68,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=GREEN, width=4.0),
            sketch_style=SKETCH,
        )
        ana_left_body = Text(
            "4 years of general medicine",
            position=(480, 380),
            font_size=48,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=BLACK, width=3.0),
            sketch_style=SKETCH,
        )
        ana_right_title = Text(
            "Cardiology Residency",
            position=(1440, 300),
            font_size=68,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=RED, width=4.0),
            sketch_style=SKETCH,
        )
        ana_right_body = Text(
            "1 year of heart specialization",
            position=(1440, 380),
            font_size=48,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=BLACK, width=3.0),
            sketch_style=SKETCH,
        )
        ana_arrow = Text(
            "→",
            position=(960, 340),
            font_size=72,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=ORANGE, width=4.0),
            sketch_style=SKETCH,
        )
        ana_note = make_body(
            "You already know medicine. Now you specialize.", y=540, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=analogy_start + 0.5, duration=1.5), drawable=ana_title)
        scene.add(SketchAnimation(start_time=analogy_start + 1.5, duration=1.2), drawable=ana_left_title)
        scene.add(SketchAnimation(start_time=analogy_start + 2.2, duration=1.0), drawable=ana_left_body)
        scene.add(SketchAnimation(start_time=analogy_start + 2.8, duration=0.8), drawable=ana_arrow)
        scene.add(SketchAnimation(start_time=analogy_start + 3.2, duration=1.2), drawable=ana_right_title)
        scene.add(SketchAnimation(start_time=analogy_start + 3.8, duration=1.0), drawable=ana_right_body)
        scene.add(SketchAnimation(start_time=analogy_start + 4.5, duration=1.2), drawable=ana_note)

        ana_drawables = [ana_title, ana_left_title, ana_left_body, ana_arrow, ana_right_title, ana_right_body, ana_note]

        # --- Section 8: Side-by-Side Comparison ---
        make_eraser(ana_drawables, start_time=comparison_start - 0.3, duration=1.2)

        comp_title = make_title("Side by Side", y=120, color=BLUE)

        comp_left_title = Text(
            "Pretraining",
            position=(480, 220),
            font_size=64,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=GREEN, width=4.0),
            sketch_style=SKETCH,
        )
        comp_right_title = Text(
            "Fine-tuning",
            position=(1440, 220),
            font_size=64,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=RED, width=4.0),
            sketch_style=SKETCH,
        )

        comp_rows = [
            ("Huge general dataset", "Small focused dataset"),
            ("Thousands of GPUs", "Single GPU"),
            ("Weeks to months", "Hours to days"),
            ("Millions of dollars", "Dollars to hundreds"),
            ("General knowledge", "Task expertise"),
        ]

        comp_drawables = [comp_title, comp_left_title, comp_right_title]

        for i, (left, right) in enumerate(comp_rows):
            y_pos = 320 + i * 100
            left_text = Text(
                left,
                position=(480, y_pos),
                font_size=44,
                font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=BLACK, width=3.0),
                sketch_style=SKETCH,
            )
            right_text = Text(
                right,
                position=(1440, y_pos),
                font_size=44,
                font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=BLACK, width=3.0),
                sketch_style=SKETCH,
            )
            scene.add(
                SketchAnimation(start_time=comparison_start + 1.0 + i * 0.7, duration=0.8),
                drawable=left_text,
            )
            scene.add(
                SketchAnimation(start_time=comparison_start + 1.3 + i * 0.7, duration=0.8),
                drawable=right_text,
            )
            comp_drawables.extend([left_text, right_text])

        comp_note = make_body(
            "Different scale, different purpose, same foundation.", y=840, color=ORANGE
        )
        scene.add(SketchAnimation(start_time=comparison_start + 5.0, duration=1.2), drawable=comp_note)
        comp_drawables.append(comp_note)

        # --- Section 9: Why Both ---
        make_eraser(comp_drawables, start_time=why_both_start - 0.3, duration=1.2)

        why_title = make_title("Why Do We Need Both?", y=160, color=BLUE)
        why_bullets = make_bullet_list(
            [
                "Without pretraining: the model knows nothing",
                "Without fine-tuning: the model is too general",
                "Together: knowledgeable AND useful",
            ],
            y_start=300,
            color=BLACK,
        )
        why_note = make_body(
            "Pretraining builds the brain. Fine-tuning gives it a job.", y=600, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=why_both_start + 0.5, duration=1.5), drawable=why_title)
        for i, bullet in enumerate(why_bullets):
            scene.add(
                SketchAnimation(start_time=why_both_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=why_both_start + 4.0, duration=1.2), drawable=why_note)

        why_drawables = [why_title] + why_bullets + [why_note]

        # --- Section 10: Modern Approach (Alignment) ---
        make_eraser(why_drawables, start_time=modern_start - 0.3, duration=1.2)

        mod_title = make_title("The Modern Pipeline", y=160, color=BLUE)
        mod_step1 = Text(
            "1. Pretraining → General knowledge",
            position=(960, 300),
            font_size=56,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=GREEN, width=3.5),
            sketch_style=SKETCH,
        )
        mod_step2 = Text(
            "2. Fine-tuning → Task expertise",
            position=(960, 400),
            font_size=56,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=RED, width=3.5),
            sketch_style=SKETCH,
        )
        mod_step3 = Text(
            "3. Alignment → Helpful, honest, harmless",
            position=(960, 500),
            font_size=56,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=PURPLE, width=3.5),
            sketch_style=SKETCH,
        )
        mod_note = make_body(
            "Pretraining and fine-tuning remain the foundation.", y=640, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=modern_start + 0.5, duration=1.5), drawable=mod_title)
        scene.add(SketchAnimation(start_time=modern_start + 1.5, duration=1.0), drawable=mod_step1)
        scene.add(SketchAnimation(start_time=modern_start + 2.5, duration=1.0), drawable=mod_step2)
        scene.add(SketchAnimation(start_time=modern_start + 3.5, duration=1.0), drawable=mod_step3)
        scene.add(SketchAnimation(start_time=modern_start + 4.5, duration=1.2), drawable=mod_note)

        mod_drawables = [mod_title, mod_step1, mod_step2, mod_step3, mod_note]

        # --- Section 11: Takeaway ---
        make_eraser(mod_drawables, start_time=takeaway_start - 0.3, duration=1.2)

        take_title = make_title("Key Takeaway", y=200, color=BLUE)
        take_line1 = make_body(
            "Pretraining gives the model its brain.", y=360, color=GREEN
        )
        take_line2 = make_body(
            "Fine-tuning gives the model its job.", y=460, color=RED
        )
        take_note = make_body(
            "Both are essential for building useful AI.", y=600, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=takeaway_start + 0.5, duration=1.5), drawable=take_title)
        scene.add(SketchAnimation(start_time=takeaway_start + 1.5, duration=1.2), drawable=take_line1)
        scene.add(SketchAnimation(start_time=takeaway_start + 2.8, duration=1.2), drawable=take_line2)
        scene.add(SketchAnimation(start_time=takeaway_start + 4.0, duration=1.2), drawable=take_note)

        take_drawables = [take_title, take_line1, take_line2, take_note]

        # --- Section 12: Outro ---
        make_eraser(take_drawables, start_time=outro_start - 0.3, duration=1.2)

        outro_title = make_title("Thanks for watching!", y=300, color=BLUE)
        outro_body = make_body(
            "Next video: How transformers work under the hood", y=480, color=BLACK
        )

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.5), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 1.8, duration=1.5), drawable=outro_body)

        return tracker.end_time + 0.8


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")


if __name__ == "__main__":
    main()
