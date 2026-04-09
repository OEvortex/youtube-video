"""
Whiteboard explainer: What is a Large Language Model?

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
from handanim.stylings.color import BLACK, BLUE, ORANGE, RED, WHITE


WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = ROOT / "output"
AUDIO_PATH = OUTPUT_DIR / "llm_explained_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "llm_explained_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.0, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='hook'/> What is a large language model? "
    "It is an AI system trained on huge amounts of text. "
    "<bookmark mark='definition'/> It learns patterns, then predicts the next token or word. "
    "That is how it can draft, summarize, and answer in plain language. "
    "<bookmark mark='large'/> The large part refers to scale. "
    "More parameters give the model more capacity to store relationships. "
    "<bookmark mark='language'/> The language part means context matters. "
    "It works with words, sentences, and nearby clues to stay coherent. "
    "<bookmark mark='takeaway'/> Put together, it is a fast text assistant, not a human mind. "
    "<bookmark mark='outro'/> But it can still be very useful for writing and learning."
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
        font_size=120,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=4.0),
        sketch_style=SKETCH,
    )


def make_body(
    text: str, *, y: float, color: tuple[float, float, float] = BLACK, align: str = "center"
) -> Text:
    return Text(
        text,
        position=(960, y),
        font_size=60,
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
    y_step: float = 90,
) -> list[Text]:
    return [
        Text(
            f"• {line}",
            position=(x, y_start + i * y_step),
            font_size=52,
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
        definition_start = tracker.bookmark_time("definition")
        large_start = tracker.bookmark_time("large")
        language_start = tracker.bookmark_time("language")
        takeaway_start = tracker.bookmark_time("takeaway")
        outro_start = tracker.bookmark_time("outro")

        # --- Section 1: Hook ---
        hook_title = make_title("What is a Large Language Model?", y=200, color=BLUE)
        hook_subtitle = make_body(
            "An AI system trained on huge amounts of text", y=340, color=BLACK
        )
        hook_note = make_body("Short answer: text in, useful language out.", y=500, color=ORANGE)

        scene.add(SketchAnimation(start_time=hook_start, duration=2.0), drawable=hook_title)
        scene.add(
            SketchAnimation(start_time=hook_start + 1.5, duration=1.8), drawable=hook_subtitle
        )
        scene.add(SketchAnimation(start_time=hook_start + 2.8, duration=1.2), drawable=hook_note)

        hook_drawables = [hook_title, hook_subtitle, hook_note]

        # --- Section 2: Definition ---
        make_eraser(hook_drawables, start_time=definition_start - 0.3, duration=1.2)

        def_title = make_title("It Learns Patterns", y=180, color=BLUE)
        def_bullets = make_bullet_list(
            [
                "trained on massive text data",
                "predicts the next token or word",
                "turns patterns into language",
            ],
            y_start=320,
            color=BLACK,
        )
        def_note = make_body(
            "That is how it can draft, summarize, and answer.", y=580, color=ORANGE
        )

        scene.add(
            SketchAnimation(start_time=definition_start + 0.5, duration=1.5), drawable=def_title
        )
        for i, bullet in enumerate(def_bullets):
            scene.add(
                SketchAnimation(start_time=definition_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(
            SketchAnimation(start_time=definition_start + 4.0, duration=1.2), drawable=def_note
        )

        def_drawables = [def_title] + def_bullets + [def_note]

        # --- Section 3: Large = Scale ---
        make_eraser(def_drawables, start_time=large_start - 0.3, duration=1.2)

        large_title = make_title("Large = Scale", y=180, color=BLUE)
        large_bullets = make_bullet_list(
            [
                "more parameters = more capacity",
                "more capacity = richer relationships",
                "more scale = more room to learn",
            ],
            y_start=320,
            color=BLACK,
        )
        large_note = make_body(
            "The model gets wider in knowledge, not in the frame.", y=580, color=ORANGE
        )

        scene.add(SketchAnimation(start_time=large_start + 0.5, duration=1.5), drawable=large_title)
        for i, bullet in enumerate(large_bullets):
            scene.add(
                SketchAnimation(start_time=large_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=large_start + 4.0, duration=1.2), drawable=large_note)

        large_drawables = [large_title] + large_bullets + [large_note]

        # --- Section 4: Language = Context ---
        make_eraser(large_drawables, start_time=language_start - 0.3, duration=1.2)

        lang_title = make_title("Language = Context", y=180, color=BLUE)
        lang_bullets = make_bullet_list(
            [
                "reads words and nearby clues",
                "keeps sentences coherent",
                "generates natural language",
            ],
            y_start=320,
            color=BLACK,
        )
        lang_note = make_body("Context is what keeps the response on track.", y=580, color=ORANGE)

        scene.add(
            SketchAnimation(start_time=language_start + 0.5, duration=1.5), drawable=lang_title
        )
        for i, bullet in enumerate(lang_bullets):
            scene.add(
                SketchAnimation(start_time=language_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(
            SketchAnimation(start_time=language_start + 4.0, duration=1.2), drawable=lang_note
        )

        lang_drawables = [lang_title] + lang_bullets + [lang_note]

        # --- Section 5: Takeaway ---
        make_eraser(lang_drawables, start_time=takeaway_start - 0.3, duration=1.2)

        take_title = make_title("Put Together", y=180, color=BLUE)
        take_bullets = make_bullet_list(
            [
                "a fast text assistant",
                "not human, but very useful",
                "ideal for writing and learning",
            ],
            y_start=320,
            color=BLACK,
        )
        take_note = make_body("This is the simple idea behind modern chat AI.", y=580, color=ORANGE)

        scene.add(
            SketchAnimation(start_time=takeaway_start + 0.5, duration=1.5), drawable=take_title
        )
        for i, bullet in enumerate(take_bullets):
            scene.add(
                SketchAnimation(start_time=takeaway_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(
            SketchAnimation(start_time=takeaway_start + 4.0, duration=1.2), drawable=take_note
        )

        take_drawables = [take_title] + take_bullets + [take_note]

        # --- Section 6: Outro ---
        make_eraser(take_drawables, start_time=outro_start - 0.3, duration=1.2)

        outro_title = make_title("Thanks for watching!", y=300, color=BLUE)
        outro_body = make_body(
            "Next video: Pretraining vs Fine-tuning", y=480, color=BLACK
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
