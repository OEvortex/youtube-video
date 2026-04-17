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
from handanim.animations import SketchAnimation, ReplacementTransform
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, LinearPath, Math, Rectangle, Table
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, ORANGE, RED, WHITE, PURPLE, TEAL,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "mtp_qwen_deep_dive"
AUDIO_PATH = OUTPUT_DIR / "mtp_deep_dive_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "mtp_deep_dive_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+2%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome to a deep dive into Multi-Token Prediction, or MTP. "
    "If you want to understand how modern giants like DeepSeek-V3 and the newly released Qwen 3.5 achieve blazing fast inference, you are in the right place. "
    
    "<bookmark mark='ntp'/> Let's start with the traditional method: Next-Token Prediction. "
    "Standard Large Language Models generate text sequentially. They predict exactly one word, append it to the context, and run the entire massive model all over again. "
    "This auto-regressive bottleneck is incredibly slow and forces the model to act short-sighted, predicting immediate words rather than planning complete thoughts. "
    
    "<bookmark mark='mtp'/> Multi-Token Prediction shatters this bottleneck. "
    "Instead of predicting just one token, the model is trained to predict multiple future tokens simultaneously. "
    "For example, from 'The cat', it might predict 'sat', 'on', 'the', and 'mat' all in one step. "
    "This forces the AI to plan its logic ahead of time, greatly improving complex reasoning. "
    
    "<bookmark mark='gloeckle'/> How do we build this? The first major architecture came from Meta's Gloeckle. "
    "Their approach uses Independent Parallel Heads. The main model processes the context, and then multiple separate output heads branch off. "
    "Head 1 predicts token T plus 1. Head 2 predicts T plus 2. "
    "While this yielded huge speedups on coding tasks, it ignores the causal chain. Head 3 doesn't actually know what Head 2 is predicting! "
    
    "<bookmark mark='deepseek'/> DeepSeek-V3 solved this with Sequential MTP Modules. "
    "Instead of independent branches, DeepSeek chains the modules together. "
    "Module 2 takes the hidden state from Module 1, combining it with the newly predicted token embedding. "
    "This preserves causal dependency, allowing profound reasoning across general domains. "
    
    "<bookmark mark='qwen35'/> Recently, Alibaba took this even further with Qwen 3.5. "
    "Qwen 3.5 integrates MTP directly into a hybrid architecture. It combines Gated Delta Networks, which use linear attention, with a Sparse Mixture of Experts. "
    "By fusing linear attention with MTP training, Qwen 3.5 serves as a native drafting engine, achieving up to 19 times faster decoding throughput compared to previous generations! "
    
    "<bookmark mark='speculative'/> So how does MTP accelerate inference? The secret is Self-Speculative Decoding. "
    "During inference, these lightweight MTP modules instantly draft the next 3 or 4 tokens. "
    "The massive main model then verifies all these drafted tokens in a single parallel forward pass. "
    "If correct, we skip multiple computation steps. If wrong, we simply discard the errors and continue. No external draft model is required! "
    
    "<bookmark mark='summary'/> Let's summarize. Next-Token Prediction is sequential and slow. "
    "Meta's Gloeckle forces future planning via parallel heads. "
    "DeepSeek's Sequential MTP maintains the causal chain. "
    "And Qwen 3.5 fuses MTP with hybrid linear attention for extreme throughput. "
    
    "<bookmark mark='outro'/> Multi-Token Prediction is fundamentally changing AI efficiency. Thanks for watching!"
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

def make_eraser(objects_to_erase: list, scene: Scene, *, start_time: float, duration: float = 1.2) -> None:
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
        ntp_start = tracker.bookmark_time("ntp")
        mtp_start = tracker.bookmark_time("mtp")
        gloeckle_start = tracker.bookmark_time("gloeckle")
        deepseek_start = tracker.bookmark_time("deepseek")
        qwen35_start = tracker.bookmark_time("qwen35")
        speculative_start = tracker.bookmark_time("speculative")
        summary_start = tracker.bookmark_time("summary")
        outro_start = tracker.bookmark_time("outro")

        stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Multi-Token Prediction (MTP)", y=400, color=BLUE)
        intro_sub = make_body("The Engine Behind DeepSeek-V3 & Qwen 3.5", y=550, color=ORANGE, font_size=64)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)

        intro_drawables =[intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Next-Token Prediction (NTP)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=ntp_start - 1.2)
        
        ntp_title = make_title("The Bottleneck: Next-Token Prediction", y=150, color=RED)
        
        box_ctx = FlowchartProcess("Context:\n'The cat'", top_left=(200, 350), width=300, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        arr1 = Arrow(start_point=(500, 410), end_point=(650, 410), stroke_style=StrokeStyle(color=BLACK, width=4))
        
        box_t1 = FlowchartProcess("sat", top_left=(650, 350), width=150, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.4), stroke_style=stroke)
        arr2 = Arrow(start_point=(800, 410), end_point=(950, 410), stroke_style=StrokeStyle(color=BLACK, width=4))
        
        box_t2 = FlowchartProcess("on", top_left=(950, 350), width=150, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.4), stroke_style=stroke)
        arr3 = Arrow(start_point=(1100, 410), end_point=(1250, 410), stroke_style=StrokeStyle(color=BLACK, width=4))
        
        box_t3 = FlowchartProcess("the", top_left=(1250, 350), width=150, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.4), stroke_style=stroke)
        
        bottleneck_text = make_body("Sequential Bottleneck: Slow & Short-sighted", x=960, y=600, color=RED, font_size=64)
        loop_arrow = Curve(points=[(1325, 470), (1325, 550), (350, 550), (350, 470)], stroke_style=StrokeStyle(color=RED, width=4), sketch_style=SKETCH)
        loop_text = make_body("Re-run entire model", x=800, y=500, color=RED, font_size=40)

        scene.add(SketchAnimation(start_time=ntp_start + 0.5, duration=1.0), drawable=ntp_title)
        scene.add(SketchAnimation(start_time=ntp_start + 2.0, duration=1.0), drawable=box_ctx)
        scene.add(SketchAnimation(start_time=ntp_start + 3.0, duration=0.5), drawable=arr1)
        scene.add(SketchAnimation(start_time=ntp_start + 3.5, duration=0.5), drawable=box_t1)
        
        scene.add(SketchAnimation(start_time=ntp_start + 4.5, duration=0.8), drawable=loop_arrow)
        scene.add(SketchAnimation(start_time=ntp_start + 4.5, duration=0.8), drawable=loop_text)
        
        scene.add(SketchAnimation(start_time=ntp_start + 5.5, duration=0.5), drawable=arr2)
        scene.add(SketchAnimation(start_time=ntp_start + 6.0, duration=0.5), drawable=box_t2)
        scene.add(SketchAnimation(start_time=ntp_start + 6.5, duration=0.5), drawable=arr3)
        scene.add(SketchAnimation(start_time=ntp_start + 7.0, duration=0.5), drawable=box_t3)
        
        scene.add(SketchAnimation(start_time=ntp_start + 9.0, duration=1.5), drawable=bottleneck_text)

        ntp_drawables =[ntp_title, box_ctx, arr1, box_t1, arr2, box_t2, arr3, box_t3, bottleneck_text, loop_arrow, loop_text]

        # ---------------------------------------------------------
        # SECTION 3: Multi-Token Prediction (MTP) Concept
        # ---------------------------------------------------------
        make_eraser(ntp_drawables, scene, start_time=mtp_start - 1.2)
        
        mtp_title = make_title("Multi-Token Prediction (MTP)", y=150, color=GREEN)
        
        box_ctx_m = FlowchartProcess("Context:\n'The cat'", top_left=(200, 450), width=300, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        
        a1 = Arrow(start_point=(500, 525), end_point=(700, 350), stroke_style=StrokeStyle(color=GREEN, width=5))
        a2 = Arrow(start_point=(500, 525), end_point=(700, 470), stroke_style=StrokeStyle(color=GREEN, width=5))
        a3 = Arrow(start_point=(500, 525), end_point=(700, 590), stroke_style=StrokeStyle(color=GREEN, width=5))
        a4 = Arrow(start_point=(500, 525), end_point=(700, 710), stroke_style=StrokeStyle(color=GREEN, width=5))
        
        b1 = FlowchartProcess("sat", top_left=(700, 300), width=200, height=100, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        b2 = FlowchartProcess("on", top_left=(700, 420), width=200, height=100, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        b3 = FlowchartProcess("the", top_left=(700, 540), width=200, height=100, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        b4 = FlowchartProcess("mat", top_left=(700, 660), width=200, height=100, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        
        plan_text = make_body("Forces the AI to Plan Ahead\n(Huge gains in Coding & Logic)", x=1400, y=525, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=mtp_start + 0.5, duration=1.0), drawable=mtp_title)
        scene.add(SketchAnimation(start_time=mtp_start + 2.0, duration=1.0), drawable=box_ctx_m)
        
        scene.add(SketchAnimation(start_time=mtp_start + 4.0, duration=0.5), drawable=a1)
        scene.add(SketchAnimation(start_time=mtp_start + 4.0, duration=0.5), drawable=b1)
        scene.add(SketchAnimation(start_time=mtp_start + 4.5, duration=0.5), drawable=a2)
        scene.add(SketchAnimation(start_time=mtp_start + 4.5, duration=0.5), drawable=b2)
        scene.add(SketchAnimation(start_time=mtp_start + 5.0, duration=0.5), drawable=a3)
        scene.add(SketchAnimation(start_time=mtp_start + 5.0, duration=0.5), drawable=b3)
        scene.add(SketchAnimation(start_time=mtp_start + 5.5, duration=0.5), drawable=a4)
        scene.add(SketchAnimation(start_time=mtp_start + 5.5, duration=0.5), drawable=b4)
        
        scene.add(SketchAnimation(start_time=mtp_start + 8.0, duration=1.5), drawable=plan_text)

        mtp_drawables =[mtp_title, box_ctx_m, a1, b1, a2, b2, a3, b3, a4, b4, plan_text]

        # ---------------------------------------------------------
        # SECTION 4: Gloeckle (Meta)
        # ---------------------------------------------------------
        make_eraser(mtp_drawables, scene, start_time=gloeckle_start - 1.2)
        
        glk_title = make_title("Architecture 1: Gloeckle (Meta)", y=150, color=ORANGE)
        
        trunk = FlowchartProcess("Main Model Trunk\n(Hidden State $h_t$)", top_left=(200, 500), width=450, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=stroke)
        
        arr_h1 = Arrow(start_point=(650, 575), end_point=(900, 350), stroke_style=StrokeStyle(color=BLACK, width=4))
        arr_h2 = Arrow(start_point=(650, 575), end_point=(900, 575), stroke_style=StrokeStyle(color=BLACK, width=4))
        arr_h3 = Arrow(start_point=(650, 575), end_point=(900, 800), stroke_style=StrokeStyle(color=BLACK, width=4))
        
        head1 = FlowchartProcess("Head 1\n($T+1$)", top_left=(900, 300), width=200, height=100, font_size=40, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        head2 = FlowchartProcess("Head 2\n($T+2$)", top_left=(900, 525), width=200, height=100, font_size=40, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        head3 = FlowchartProcess("Head 3\n($T+3$)", top_left=(900, 750), width=200, height=100, font_size=40, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        
        flaw_text = make_body("FLAW: Independent Heads ignore the causal chain.\nHead 3 doesn't know what Head 2 predicted!", x=1450, y=575, color=RED, font_size=48)

        scene.add(SketchAnimation(start_time=gloeckle_start + 0.5, duration=1.0), drawable=glk_title)
        scene.add(SketchAnimation(start_time=gloeckle_start + 2.5, duration=1.5), drawable=trunk)
        
        scene.add(SketchAnimation(start_time=gloeckle_start + 4.5, duration=0.8), drawable=arr_h1)
        scene.add(SketchAnimation(start_time=gloeckle_start + 4.5, duration=0.8), drawable=head1)
        scene.add(SketchAnimation(start_time=gloeckle_start + 5.0, duration=0.8), drawable=arr_h2)
        scene.add(SketchAnimation(start_time=gloeckle_start + 5.0, duration=0.8), drawable=head2)
        scene.add(SketchAnimation(start_time=gloeckle_start + 5.5, duration=0.8), drawable=arr_h3)
        scene.add(SketchAnimation(start_time=gloeckle_start + 5.5, duration=0.8), drawable=head3)
        
        scene.add(SketchAnimation(start_time=gloeckle_start + 9.0, duration=2.0), drawable=flaw_text)

        glk_drawables =[glk_title, trunk, arr_h1, head1, arr_h2, head2, arr_h3, head3, flaw_text]

        # ---------------------------------------------------------
        # SECTION 5: DeepSeek-V3
        # ---------------------------------------------------------
        make_eraser(glk_drawables, scene, start_time=deepseek_start - 1.2)
        
        ds_title = make_title("Architecture 2: DeepSeek-V3", y=150, color=BLUE)
        
        trunk2 = FlowchartProcess("Trunk\n($h_t$)", top_left=(100, 450), width=200, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        
        a_m1 = Arrow(start_point=(300, 525), end_point=(400, 525), stroke_style=stroke)
        m1 = FlowchartProcess("MTP Mod 1\n(Predicts $T+1$)", top_left=(400, 450), width=300, height=150, font_size=40, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.4), stroke_style=stroke)
        
        a_m2 = Arrow(start_point=(700, 525), end_point=(850, 525), stroke_style=stroke)
        m2 = FlowchartProcess("MTP Mod 2\n(Predicts $T+2$)", top_left=(850, 450), width=300, height=150, font_size=40, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.4), stroke_style=stroke)
        
        a_m3 = Arrow(start_point=(1150, 525), end_point=(1300, 525), stroke_style=stroke)
        m3 = FlowchartProcess("MTP Mod 3\n(Predicts $T+3$)", top_left=(1300, 450), width=300, height=150, font_size=40, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.4), stroke_style=stroke)
        
        emb1 = Math(r"$\text{Emb}(x_{T+1})$", position=(550, 350), font_size=48, stroke_style=StrokeStyle(color=ORANGE, width=2))
        arr_emb1 = Arrow(start_point=(550, 380), end_point=(550, 450), stroke_style=StrokeStyle(color=ORANGE, width=3))
        
        emb2 = Math(r"$\text{Emb}(x_{T+2})$", position=(1000, 350), font_size=48, stroke_style=StrokeStyle(color=ORANGE, width=2))
        arr_emb2 = Arrow(start_point=(1000, 380), end_point=(1000, 450), stroke_style=StrokeStyle(color=ORANGE, width=3))

        fix_text = make_body("Sequential Chain Preserved!\nEnables profound general reasoning.", x=960, y=800, color=GREEN, font_size=64)

        scene.add(SketchAnimation(start_time=deepseek_start + 0.5, duration=1.0), drawable=ds_title)
        scene.add(SketchAnimation(start_time=deepseek_start + 2.0, duration=1.0), drawable=trunk2)
        
        scene.add(SketchAnimation(start_time=deepseek_start + 3.5, duration=0.5), drawable=a_m1)
        scene.add(SketchAnimation(start_time=deepseek_start + 4.0, duration=1.0), drawable=m1)
        
        scene.add(SketchAnimation(start_time=deepseek_start + 5.5, duration=0.8), drawable=emb1)
        scene.add(SketchAnimation(start_time=deepseek_start + 5.5, duration=0.5), drawable=arr_emb1)
        
        scene.add(SketchAnimation(start_time=deepseek_start + 6.5, duration=0.5), drawable=a_m2)
        scene.add(SketchAnimation(start_time=deepseek_start + 7.0, duration=1.0), drawable=m2)
        
        scene.add(SketchAnimation(start_time=deepseek_start + 8.5, duration=0.8), drawable=emb2)
        scene.add(SketchAnimation(start_time=deepseek_start + 8.5, duration=0.5), drawable=arr_emb2)
        
        scene.add(SketchAnimation(start_time=deepseek_start + 9.5, duration=0.5), drawable=a_m3)
        scene.add(SketchAnimation(start_time=deepseek_start + 10.0, duration=1.0), drawable=m3)
        
        scene.add(SketchAnimation(start_time=deepseek_start + 12.0, duration=1.5), drawable=fix_text)

        ds_drawables =[ds_title, trunk2, a_m1, m1, a_m2, m2, a_m3, m3, emb1, arr_emb1, emb2, arr_emb2, fix_text]

        # ---------------------------------------------------------
        # SECTION 6: Qwen 3.5
        # ---------------------------------------------------------
        make_eraser(ds_drawables, scene, start_time=qwen35_start - 1.2)
        
        qwen_title = make_title("Architecture 3: Qwen 3.5", y=150, color=PURPLE)
        
        hybrid_box = FlowchartProcess("Hybrid Attention\n(Gated DeltaNet + Softmax)", top_left=(250, 350), width=500, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=stroke)
        moe_box = FlowchartProcess("Sparse MoE\n(Mixture of Experts)", top_left=(250, 550), width=500, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=stroke)
        
        arr_q1 = Arrow(start_point=(750, 425), end_point=(900, 500), stroke_style=stroke)
        arr_q2 = Arrow(start_point=(750, 610), end_point=(900, 500), stroke_style=stroke)
        
        mtp_box = FlowchartProcess("Native MTP Drafting\n(Speculative Engine)", top_left=(900, 400), width=500, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        
        qwen_perf = make_body("Up to 19x Faster Decoding Throughput!", x=960, y=800, color=ORANGE, font_size=64)

        scene.add(SketchAnimation(start_time=qwen35_start + 0.5, duration=1.0), drawable=qwen_title)
        scene.add(SketchAnimation(start_time=qwen35_start + 2.5, duration=1.5), drawable=hybrid_box)
        scene.add(SketchAnimation(start_time=qwen35_start + 4.0, duration=1.5), drawable=moe_box)
        
        scene.add(SketchAnimation(start_time=qwen35_start + 6.0, duration=0.5), drawable=arr_q1)
        scene.add(SketchAnimation(start_time=qwen35_start + 6.0, duration=0.5), drawable=arr_q2)
        scene.add(SketchAnimation(start_time=qwen35_start + 6.5, duration=1.5), drawable=mtp_box)
        
        scene.add(SketchAnimation(start_time=qwen35_start + 9.5, duration=1.5), drawable=qwen_perf)

        qwen_drawables =[qwen_title, hybrid_box, moe_box, arr_q1, arr_q2, mtp_box, qwen_perf]

        # ---------------------------------------------------------
        # SECTION 7: Self-Speculative Decoding
        # ---------------------------------------------------------
        make_eraser(qwen_drawables, scene, start_time=speculative_start - 1.2)
        
        spec_title = make_title("Self-Speculative Decoding", y=150, color=TEAL)
        
        draft_box = FlowchartProcess("MTP Modules\nDraft 3 Tokens instantly", top_left=(300, 350), width=500, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        arr_spec = Arrow(start_point=(800, 425), end_point=(1100, 425), stroke_style=stroke)
        verif_box = FlowchartProcess("Main Model Verifies\nin 1 parallel pass", top_left=(1100, 350), width=500, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=stroke)
        
        toks = make_body("Draft: [ 'sat', 'on', 'the' ]", x=960, y=600, color=DARK_GRAY, font_size=56)
        
        chk1 = make_body("✓", x=830, y=670, color=GREEN, font_size=80)
        chk2 = make_body("✓", x=960, y=670, color=GREEN, font_size=80)
        chk3 = make_body("✓", x=1090, y=670, color=GREEN, font_size=80)
        
        speed_text = make_body("Massive Speedup without needing an external draft model!", x=960, y=850, color=PURPLE, font_size=64)

        scene.add(SketchAnimation(start_time=speculative_start + 0.5, duration=1.0), drawable=spec_title)
        scene.add(SketchAnimation(start_time=speculative_start + 2.5, duration=1.5), drawable=draft_box)
        scene.add(SketchAnimation(start_time=speculative_start + 4.5, duration=0.8), drawable=arr_spec)
        scene.add(SketchAnimation(start_time=speculative_start + 5.0, duration=1.5), drawable=verif_box)
        
        scene.add(SketchAnimation(start_time=speculative_start + 7.0, duration=1.0), drawable=toks)
        
        scene.add(SketchAnimation(start_time=speculative_start + 9.0, duration=0.5), drawable=chk1)
        scene.add(SketchAnimation(start_time=speculative_start + 9.5, duration=0.5), drawable=chk2)
        scene.add(SketchAnimation(start_time=speculative_start + 10.0, duration=0.5), drawable=chk3)
        
        scene.add(SketchAnimation(start_time=speculative_start + 12.0, duration=1.5), drawable=speed_text)

        spec_drawables =[spec_title, draft_box, arr_spec, verif_box, toks, chk1, chk2, chk3, speed_text]

        # ---------------------------------------------------------
        # SECTION 8: Summary & Outro
        # ---------------------------------------------------------
        make_eraser(spec_drawables, scene, start_time=summary_start - 1.2)
        
        sum_title = make_title("Summary", y=150, color=BLACK)

        sum_table = Table(
            data=[
                ["Method", "Architecture", "Primary Benefit"],["NTP", "Sequential Output", "Standard baseline"],
                ["Gloeckle MTP", "Parallel Heads", "3x faster coding, simple"],
                ["DeepSeek MTP", "Sequential Modules", "Deep reasoning, Causality"],["Qwen 3.5 MTP", "Hybrid (DeltaNet + MoE)", "Extreme throughput (up to 19x)"]
            ],
            top_left=(200, 250),
            col_widths=[320, 500, 780],
            row_heights=[90, 90, 90, 90, 90],
            font_size=44,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=stroke,
            sketch_style=SKETCH
        )

        outro_text = make_body("MTP is fundamentally changing AI efficiency.", y=850, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 2.0, duration=3.0), drawable=sum_table)
        scene.add(SketchAnimation(start_time=outro_start + 1.0, duration=2.0), drawable=outro_text)

        return tracker.end_time + 1.5


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering detailed MTP & Qwen 3.5 whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")


if __name__ == "__main__":
    main()