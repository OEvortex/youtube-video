import asyncio
import math
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
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, Math, Rectangle, Table
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, ORANGE, RED, WHITE, PURPLE, TEAL,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "moss_tts"
AUDIO_PATH = OUTPUT_DIR / "moss_tts_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "moss_tts_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+2%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome to a deep dive into the architecture of MOSS-TTS-Nano. "
    "At just 100 million parameters, it is an ultra-lightweight, CPU-friendly speech generation model that achieves state-of-the-art zero-shot voice cloning. "
    
    "<bookmark mark='high_level'/> The core of MOSS-TTS-Nano is an Autoregressive Decoder-only Transformer based on GPT-2. "
    "Unlike complex diffusion models, MOSS treats audio generation as a sequence-to-sequence language modeling task. "
    "It takes text tokens and reference audio tokens as a prompt, and predicts the continuation step-by-step. "
    
    "<bookmark mark='rvq'/> But how does a language model speak? It uses Residual Vector Quantization, or RVQ. "
    "Raw audio waveforms are incredibly dense. The tokenizer compresses this waveform into discrete codes across multiple hierarchical levels, or codebooks. "
    "The first level captures coarse semantic meaning, while subsequent levels capture fine acoustic details and prosody. "
    
    "<bookmark mark='delay_pattern'/> To predict these efficiently, MOSS-TTS-Nano uses a clever 'Delay Pattern'. "
    "Its prediction head doesn't just output one token. It has N plus 1 heads. Head zero predicts the semantic text alignment. "
    "The remaining heads predict the RVQ audio levels, but they are delayed! Level 1 is predicted one timestep after the semantic token, Level 2 after Level 1, and so on. "
    "This staggered approach allows fine acoustic details to be conditioned on stable semantic structures. "
    
    "<bookmark mark='transformer'/> Under the hood, the GPT-2 Backbone is highly optimized. "
    "It utilizes RMS-Norm for stable and fast convergence, and FlashAttention-2 or Scaled Dot-Product Attention for massive speedups. "
    "Crucially, it abandons standard absolute positions in favor of Rotary Positional Embeddings, or RoPE. "
    "RoPE injects relative positional information directly into the attention queries and keys, drastically improving the model's ability to maintain prosodic rhythm in long-form speech. "
    
    "<bookmark mark='cloning'/> Because of this unified architecture, zero-shot voice cloning is native. "
    "You feed the model a 3-second reference audio. The self-attention mechanism acts as a Cross-Attention bridge, prefixing the prompt tokens to the generation sequence. "
    "The newly generated tokens instantly inherit the speaker's timbre and identity without any fine-tuning. "
    
    "<bookmark mark='outro'/> MOSS-TTS-Nano proves that intelligent architecture—combining RVQ, RoPE, and autoregressive modeling—can deliver giant performance in a nano-sized package. Thanks for watching!"
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
        font_size=88,
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
        high_level_start = tracker.bookmark_time("high_level")
        rvq_start = tracker.bookmark_time("rvq")
        delay_pattern_start = tracker.bookmark_time("delay_pattern")
        transformer_start = tracker.bookmark_time("transformer")
        cloning_start = tracker.bookmark_time("cloning")
        outro_start = tracker.bookmark_time("outro")

        stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro (0 - ~15s)
        # ---------------------------------------------------------
        intro_title = make_title("MOSS-TTS-Nano Architecture", y=350, color=BLUE)
        intro_sub = make_body("Ultra-Lightweight 100M Parameter TTS", y=500, color=ORANGE, font_size=64)
        cpu_label = FlowchartProcess("CPU Real-Time Generation", top_left=(660, 650), width=600, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=stroke)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        scene.add(SketchAnimation(start_time=intro_start + 5.0, duration=1.5), drawable=cpu_label)

        intro_drawables =[intro_title, intro_sub, cpu_label]

        # ---------------------------------------------------------
        # SECTION 2: High Level Pipeline (~15s - ~30s)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=high_level_start - 1.2)
        
        hl_title = make_title("High-Level Pipeline (Seq-to-Seq)", y=150, color=GREEN)
        
        prompt_box = FlowchartProcess("Text Prompt\n+\nRef Audio Tokens", top_left=(150, 420), width=400, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        arr1 = Arrow(start_point=(550, 520), end_point=(700, 520), stroke_style=StrokeStyle(color=BLACK, width=6))
        
        gpt_box = FlowchartProcess("GPT-2 Autoregressive\nDecoder Backbone\n(Predicts Next Token)", top_left=(700, 370), width=500, height=300, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=stroke)
        arr2 = Arrow(start_point=(1200, 520), end_point=(1350, 520), stroke_style=StrokeStyle(color=BLACK, width=6))
        
        audio_box = FlowchartProcess("Generated Audio\nSequence", top_left=(1350, 420), width=400, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=stroke)

        scene.add(SketchAnimation(start_time=high_level_start + 0.5, duration=1.0), drawable=hl_title)
        scene.add(SketchAnimation(start_time=high_level_start + 2.0, duration=1.5), drawable=prompt_box)
        scene.add(SketchAnimation(start_time=high_level_start + 4.0, duration=0.8), drawable=arr1)
        scene.add(SketchAnimation(start_time=high_level_start + 5.0, duration=1.5), drawable=gpt_box)
        scene.add(SketchAnimation(start_time=high_level_start + 8.0, duration=0.8), drawable=arr2)
        scene.add(SketchAnimation(start_time=high_level_start + 9.0, duration=1.5), drawable=audio_box)

        hl_drawables =[hl_title, prompt_box, arr1, gpt_box, arr2, audio_box]

        # ---------------------------------------------------------
        # SECTION 3: RVQ (~30s - ~50s)
        # ---------------------------------------------------------
        make_eraser(hl_drawables, scene, start_time=rvq_start - 1.2)
        
        rvq_title = make_title("Residual Vector Quantization (RVQ)", y=150, color=PURPLE)
        
        # Waveform
        wave_pts =[]
        for x in range(200, 601, 10):
            val = (x - 400) / 30
            y = 500 - 150 * math.sin(val) * math.exp(-0.01 * (x-400)**2)
            wave_pts.append((x, y))
        waveform = Curve(points=wave_pts, stroke_style=StrokeStyle(color=BLUE, width=6), sketch_style=SKETCH)
        wave_lbl = make_body("Dense Raw Audio", x=400, y=700, color=BLUE, font_size=48)
        
        arr_rvq = Arrow(start_point=(650, 500), end_point=(850, 500), stroke_style=StrokeStyle(color=BLACK, width=6))
        
        # RVQ Stack (Codebooks)
        rvq_boxes =[]
        for i in range(4): # Show 4 levels for simplicity
            b = Rectangle(top_left=(900, 300 + i*110), width=600, height=90, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3 + i*0.1), sketch_style=SKETCH)
            if i == 0:
                lbl = "Level 1: Coarse Semantic Meaning"
            elif i == 3:
                lbl = "Level 4: Fine Acoustic Details"
            else:
                lbl = f"Level {i+1}: Prosody & Timbre"
            t = make_body(lbl, x=1200, y=345 + i*110, color=BLACK, font_size=36)
            rvq_boxes.extend([b, t])

        scene.add(SketchAnimation(start_time=rvq_start + 0.5, duration=1.0), drawable=rvq_title)
        scene.add(SketchAnimation(start_time=rvq_start + 2.0, duration=1.5), drawable=waveform)
        scene.add(SketchAnimation(start_time=rvq_start + 3.0, duration=0.8), drawable=wave_lbl)
        scene.add(SketchAnimation(start_time=rvq_start + 4.5, duration=1.0), drawable=arr_rvq)
        
        for i in range(4):
            scene.add(SketchAnimation(start_time=rvq_start + 6.0 + i*1.0, duration=0.8), drawable=rvq_boxes[i*2])
            scene.add(SketchAnimation(start_time=rvq_start + 6.0 + i*1.0, duration=0.5), drawable=rvq_boxes[i*2 + 1])

        rvq_drawables =[rvq_title, waveform, wave_lbl, arr_rvq] + rvq_boxes

        # ---------------------------------------------------------
        # SECTION 4: Delay Pattern (~50s - ~1m15s)
        # ---------------------------------------------------------
        make_eraser(rvq_drawables, scene, start_time=delay_pattern_start - 1.2)
        
        dp_title = make_title("The RVQ Delay Pattern", y=150, color=ORANGE)
        
        heads_txt = make_body("Multi-Head Output: (N_vq + 1) Heads", x=960, y=250, color=BLUE, font_size=64)
        
        # Grid representing Timesteps vs Levels
        dp_grid = []
        # Headers
        t_headers =[make_body(f"Time {t}", x=650 + t*250, y=350, font_size=40, color=DARK_GRAY) for t in range(4)]
        l_headers =[make_body("Semantic (H0)", x=350, y=450, font_size=40, color=RED),
                    make_body("Audio L1 (H1)", x=350, y=550, font_size=40, color=GREEN),
                    make_body("Audio L2 (H2)", x=350, y=650, font_size=40, color=GREEN),
                    make_body("Audio L3 (H3)", x=350, y=750, font_size=40, color=GREEN)]
        
        dp_grid.extend(t_headers + l_headers)
        
        # Matrix cells (Staggered)
        for level in range(4):
            for t in range(4):
                if t >= level: # Staggered condition
                    rect = Rectangle(top_left=(550 + t*250, 400 + level*100), width=200, height=80, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.6), sketch_style=SKETCH)
                    txt = make_body(f"Token {t-level}", x=650 + t*250, y=440 + level*100, font_size=36, color=BLACK)
                    
                    # Animate based on timestep
                    scene.add(SketchAnimation(start_time=delay_pattern_start + 6.0 + t*1.5 + level*0.2, duration=0.5), drawable=rect)
                    scene.add(SketchAnimation(start_time=delay_pattern_start + 6.0 + t*1.5 + level*0.2, duration=0.3), drawable=txt)
                    dp_grid.extend([rect, txt])
                    
        cond_lbl = make_body("Fine acoustic tokens are conditioned on stable semantic structures.", x=960, y=900, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=delay_pattern_start + 0.5, duration=1.0), drawable=dp_title)
        scene.add(SketchAnimation(start_time=delay_pattern_start + 2.0, duration=1.5), drawable=heads_txt)
        
        for h in t_headers + l_headers:
            scene.add(SketchAnimation(start_time=delay_pattern_start + 4.0, duration=0.5), drawable=h)
            
        scene.add(SketchAnimation(start_time=delay_pattern_start + 14.0, duration=2.0), drawable=cond_lbl)

        dp_drawables =[dp_title, heads_txt, cond_lbl] + dp_grid

        # ---------------------------------------------------------
        # SECTION 5: GPT-2 Transformer Core (~1m15s - ~1m45s)
        # ---------------------------------------------------------
        make_eraser(dp_drawables, scene, start_time=transformer_start - 1.2)
        
        tc_title = make_title("Optimized GPT-2 Backbone", y=150, color=TEAL)
        
        # Transformer Block Diagram
        block_bg = Rectangle(top_left=(250, 300), width=450, height=600, stroke_style=StrokeStyle(color=BLACK, width=5), fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.1), sketch_style=SKETCH)
        
        rms1 = FlowchartProcess("RMS-Norm", top_left=(300, 350), width=350, height=100, font_size=40, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=stroke)
        attn = FlowchartProcess("Self-Attention\n(FlashAttention-2)", top_left=(300, 500), width=350, height=120, font_size=36, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3), stroke_style=stroke)
        rms2 = FlowchartProcess("RMS-Norm", top_left=(300, 670), width=350, height=100, font_size=40, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=stroke)
        mlp = FlowchartProcess("MLP", top_left=(300, 820), width=350, height=100, font_size=40, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=stroke)

        # Math Highlights
        rms_math = Math(r"$\text{RMS}(x) = \sqrt{\frac{1}{n}\sum x_i^2}$", position=(1300, 400), font_size=64, stroke_style=StrokeStyle(color=RED, width=2))
        
        rope_box = FlowchartProcess("Rotary Positional Embeddings (RoPE)", top_left=(850, 550), width=900, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), stroke_style=stroke)
        rope_math = Math(r"$q_m = (q \cdot \cos) + (\text{rotate}(q) \cdot \sin)$", position=(1300, 750), font_size=64, stroke_style=StrokeStyle(color=PURPLE, width=2))
        
        prosody_lbl = make_body("Injects relative positions to maintain prosodic rhythm!", x=1300, y=900, color=BLACK, font_size=42)

        scene.add(SketchAnimation(start_time=transformer_start + 0.5, duration=1.0), drawable=tc_title)
        
        scene.add(SketchAnimation(start_time=transformer_start + 2.0, duration=1.0), drawable=block_bg)
        scene.add(SketchAnimation(start_time=transformer_start + 2.5, duration=0.8), drawable=rms1)
        scene.add(SketchAnimation(start_time=transformer_start + 3.0, duration=0.8), drawable=attn)
        scene.add(SketchAnimation(start_time=transformer_start + 3.5, duration=0.8), drawable=rms2)
        scene.add(SketchAnimation(start_time=transformer_start + 4.0, duration=0.8), drawable=mlp)
        
        scene.add(SketchAnimation(start_time=transformer_start + 6.0, duration=1.5), drawable=rms_math)
        
        scene.add(SketchAnimation(start_time=transformer_start + 11.0, duration=1.5), drawable=rope_box)
        scene.add(SketchAnimation(start_time=transformer_start + 13.0, duration=2.0), drawable=rope_math)
        scene.add(SketchAnimation(start_time=transformer_start + 18.0, duration=1.5), drawable=prosody_lbl)

        tc_drawables =[tc_title, block_bg, rms1, attn, rms2, mlp, rms_math, rope_box, rope_math, prosody_lbl]

        # ---------------------------------------------------------
        # SECTION 6: Cloning & Outro (~1m45s - End)
        # ---------------------------------------------------------
        make_eraser(tc_drawables, scene, start_time=cloning_start - 1.2)
        
        clone_title = make_title("Native Zero-Shot Voice Cloning", y=150, color=BLACK)
        
        # Flow
        ref_box = FlowchartProcess("3s Reference Audio\n(Timbre Prompt)", top_left=(250, 350), width=450, height=150, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        txt_box = FlowchartProcess("Target Text", top_left=(250, 600), width=450, height=120, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        
        ca_box = FlowchartProcess("Cross-Attention\nBridge", top_left=(850, 450), width=350, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), stroke_style=stroke)
        
        out_audio = FlowchartProcess("Cloned Speech\n(Zero Fine-Tuning)", top_left=(1400, 485), width=400, height=130, font_size=42, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        
        a1 = Arrow(start_point=(700, 425), end_point=(850, 500), stroke_style=StrokeStyle(color=BLACK, width=6))
        a2 = Arrow(start_point=(700, 660), end_point=(850, 600), stroke_style=StrokeStyle(color=BLACK, width=6))
        a3 = Arrow(start_point=(1200, 550), end_point=(1400, 550), stroke_style=StrokeStyle(color=BLACK, width=6))

        scene.add(SketchAnimation(start_time=cloning_start + 0.5, duration=1.0), drawable=clone_title)
        
        scene.add(SketchAnimation(start_time=cloning_start + 2.0, duration=1.0), drawable=ref_box)
        scene.add(SketchAnimation(start_time=cloning_start + 2.5, duration=1.0), drawable=txt_box)
        scene.add(SketchAnimation(start_time=cloning_start + 3.0, duration=0.8), drawable=a1)
        scene.add(SketchAnimation(start_time=cloning_start + 3.0, duration=0.8), drawable=a2)
        
        scene.add(SketchAnimation(start_time=cloning_start + 4.5, duration=1.5), drawable=ca_box)
        
        scene.add(SketchAnimation(start_time=cloning_start + 9.0, duration=0.8), drawable=a3)
        scene.add(SketchAnimation(start_time=cloning_start + 9.5, duration=1.5), drawable=out_audio)

        # Outro Table
        sum_table = Table(
            data=[["Architecture", "GPT-2 Autoregressive Transformer"],
                ["Audio Tokenization", "Residual Vector Quantization (RVQ)"],
                ["Positioning", "RoPE (Rotary Positional Embeddings)"],["Parameter Count", "100 Million (CPU Efficient)"]
            ],
            top_left=(360, 200),
            col_widths=[500, 700],
            row_heights=[90, 90, 90, 90],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=stroke,
            sketch_style=SKETCH
        )

        outro_text = make_body("Giant performance in a nano-sized package.", y=850, color=BLUE, font_size=72)

        # Erase cloning, show summary
        clone_drawables =[clone_title, ref_box, txt_box, ca_box, out_audio, a1, a2, a3]
        make_eraser(clone_drawables, scene, start_time=outro_start - 1.2)
        
        out_title = make_title("MOSS-TTS-Nano Summary", y=100, color=BLACK)
        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.0), drawable=out_title)
        scene.add(SketchAnimation(start_time=outro_start + 1.5, duration=2.5), drawable=sum_table)
        scene.add(SketchAnimation(start_time=tracker.end_time - 3.0, duration=1.5), drawable=outro_text)

        return tracker.end_time + 1.5


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering MOSS-TTS-Nano whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")
    print(f"Video saved to: {VIDEO_PATH}")


if __name__ == "__main__":
    main()