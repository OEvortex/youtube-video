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
from handanim.animations import ReplacementTransform, SketchAnimation
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, LinearPath, Math, Rectangle, Table
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, ORANGE, RED, WHITE, PURPLE, TEAL,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "turboquant"
AUDIO_PATH = OUTPUT_DIR / "turboquant.mp3"
VIDEO_PATH = OUTPUT_DIR / "turboquant.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+0%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome to the ultimate deep dive into TurboQuant. If you have been tracking the AI space, you know models are evolving from 8K context windows to over 100K, and even up to 1 million tokens. "
    "But there is a silent killer lurking inside these Massive Language Models: The Key-Value Cache. "
    
    "<bookmark mark='kv_cache'/> During text generation, a transformer stores the Key and Value representations of every past token. It avoids redundant computation, which is great. "
    "But the KV Cache grows linearly. At a 128-thousand token context, even a modest 8-billion parameter model consumes over 40 gigabytes of VRAM just for the cache! "
    "Your GPU runs out of memory, performance plummets as data swaps to CPU RAM, and inference grinds to a halt. "
    
    "<bookmark mark='standard_quant'/> The obvious solution is Quantization. We want to shrink those 16-bit floating-point numbers down to 3 or 4 bits. "
    "But Large Language Models suffer from an anomaly called Extreme Outliers. A few specific feature dimensions have activations that are hundreds of times larger than the rest. "
    "If we define our quantization buckets to fit these massive spikes, the remaining 99 percent of our data gets squashed into a single bucket. We lose all our information. "
    
    "<bookmark mark='overhead'/> Traditionally, researchers bypass this using Group-wise or Block Quantization. They chop the data into tiny blocks of 32 or 64 elements, and assign a unique 16-bit scaling factor to every single block. "
    "While this saves the outliers, it introduces a massive memory overhead. If you want a 3-bit cache, adding 16 bits of metadata every 32 values ruins your compression ratio! "
    
    "<bookmark mark='turboquant'/> Enter TurboQuant, a breakthrough framework from Google Research presented at ICLR 2026. It completely solves this using a zero-overhead, two-stage mathematical pipeline. "
    
    "<bookmark mark='stage1'/> Stage 1 is called PolarQuant. It relies on a beautiful property of high-dimensional geometry: Random Orthogonal Rotation. "
    "Before we quantize, we multiply the entire Key and Value matrices by a fixed, random orthogonal matrix. "
    "Imagine a massive spike of energy on one axis. When you randomly rotate the coordinate system, that single spike's energy is smeared and distributed uniformly across every single dimension. "
    "By mixing the coordinates, the extreme outliers vanish. The resulting data is isotropic; it forms a perfectly smooth, predictable Gaussian bell curve. "
    
    "<bookmark mark='lloyd_max'/> Because we mathematically know the data is now Gaussian, we don't need any per-block scaling factors! "
    "We can calculate the mathematically optimal quantization buckets globally, using the Lloyd-Max algorithm, entirely offline. "
    "TurboQuant maps this data into polar coordinates—radius and angle—and quantizes the entire cache into just 3 bits per element with zero metadata overhead. "
    
    "<bookmark mark='stage2'/> But wait. Stage 1 is incredibly efficient, but compression always leaves a residual error. "
    "In transformers, Attention is calculated via inner dot products. If we ignore the residual error, our dot products become mathematically biased, and the model's accuracy degrades. "
    
    "<bookmark mark='qjl'/> To fix this, TurboQuant introduces Stage 2: The 1-bit Quantized Johnson-Lindenstrauss transform, or QJL. "
    "Instead of throwing the residual error away, we project it onto a random Gaussian matrix, and then we take only the sign of the result: a simple plus one, or minus one. "
    "This costs exactly 1 extra bit per element. "
    
    "<bookmark mark='math_magic'/> When calculating the Attention score, we compute the dot product of our 3-bit compressed vectors, and we add the dot product of our 1-bit QJL signs. "
    "Through the magic of the Johnson-Lindenstrauss lemma, the sign bits perfectly estimate the angle between the residual errors. "
    "This totally eliminates the mathematical bias! The attention scores match the original 16-bit model perfectly. "
    
    "<bookmark mark='results'/> The results are staggering. TurboQuant achieves lossless KV Cache compression down to 3 or 4 bits. "
    "That is a 4 to 6 times memory reduction, allowing 8 times faster attention throughput, with zero model retraining, and zero fine-tuning required. "
    "It perfectly aces the needle-in-a-haystack retrieval test at massive context lengths. "
    
    "<bookmark mark='outro'/> TurboQuant is an elegant, math-driven triumph that unlocks the next generation of extreme-context AI on standard consumer hardware. Thanks for watching!"
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
        kv_cache_start = tracker.bookmark_time("kv_cache")
        standard_quant_start = tracker.bookmark_time("standard_quant")
        overhead_start = tracker.bookmark_time("overhead")
        turboquant_start = tracker.bookmark_time("turboquant")
        stage1_start = tracker.bookmark_time("stage1")
        lloyd_max_start = tracker.bookmark_time("lloyd_max")
        stage2_start = tracker.bookmark_time("stage2")
        qjl_start = tracker.bookmark_time("qjl")
        math_magic_start = tracker.bookmark_time("math_magic")
        results_start = tracker.bookmark_time("results")
        outro_start = tracker.bookmark_time("outro")

        stroke = StrokeStyle(color=BLACK, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro & KV Cache (0 - ~45s)
        # ---------------------------------------------------------
        intro_title = make_title("TurboQuant: Lossless KV Cache Compression", y=150, color=BLUE)

        llm_box = FlowchartProcess("LLM Processing", top_left=(200, 350), width=350, height=150, font_size=48, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        arr_to_kv = Arrow(start_point=(550, 425), end_point=(700, 425), stroke_style=StrokeStyle(color=BLACK, width=6))
        
        kv_title = make_body("Key-Value (KV) Cache", x=1150, y=300, color=RED, font_size=56)
        kv_boxes =[]
        for i in range(6):
            b = Rectangle(top_left=(750 + i*130, 350), width=110, height=250, stroke_style=stroke, fill_style=FillStyle(color=PASTEL_RED, opacity=0.4), sketch_style=SKETCH)
            t = make_body(f"Tok {i+1}", x=805 + i*130, y=475, color=DARK_GRAY, font_size=36)
            kv_boxes.extend([b, t])
            
        oom_text = make_body("128K Context = 40+ GB VRAM!\nGPU OUT OF MEMORY", x=1150, y=750, color=RED, font_size=72)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=kv_cache_start + 0.5, duration=1.0), drawable=llm_box)
        scene.add(SketchAnimation(start_time=kv_cache_start + 1.5, duration=1.0), drawable=arr_to_kv)
        scene.add(SketchAnimation(start_time=kv_cache_start + 2.5, duration=1.0), drawable=kv_title)
        
        for i in range(0, 12, 2): # Iterate over pairs of box+text
            scene.add(SketchAnimation(start_time=kv_cache_start + 3.5 + (i*0.2), duration=0.8), drawable=kv_boxes[i])
            scene.add(SketchAnimation(start_time=kv_cache_start + 3.5 + (i*0.2), duration=0.5), drawable=kv_boxes[i+1])
            
        scene.add(SketchAnimation(start_time=kv_cache_start + 10.0, duration=1.5), drawable=oom_text)

        intro_drawables =[intro_title, llm_box, arr_to_kv, kv_title, oom_text] + kv_boxes

        # ---------------------------------------------------------
        # SECTION 2: Standard Quantization & Outliers (~45s - ~1m20s)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=standard_quant_start - 1.2)
        
        sq_title = make_title("The Quantization Outlier Problem", y=150, color=RED)
        
        # Axis
        axis_x = Line(start=(300, 600), end=(1600, 600), stroke_style=StrokeStyle(color=BLACK, width=4), sketch_style=SKETCH)
        
        # Normal data
        data_pts = []
        for x in[350, 400, 450, 500, 550, 600, 650]:
            d = Circle(center=(x, 600), radius=15, stroke_style=StrokeStyle(color=BLACK, width=2), fill_style=FillStyle(color=BLUE), sketch_style=SKETCH)
            data_pts.append(d)
        
        norm_lbl = make_body("Normal Activations\n(99% of data)", x=500, y=450, color=BLUE, font_size=48)
        
        # Outlier
        outlier = Circle(center=(1500, 600), radius=30, stroke_style=StrokeStyle(color=BLACK, width=3), fill_style=FillStyle(color=RED), sketch_style=SKETCH)
        out_lbl = make_body("Extreme Outlier\n(100x larger!)", x=1500, y=450, color=RED, font_size=48)
        
        # Quantization Buckets
        bucket_line = Line(start=(300, 700), end=(1600, 700), stroke_style=StrokeStyle(color=GRAY, width=4), sketch_style=SKETCH)
        b_ticks =[Line(start=(x, 680), end=(x, 720), stroke_style=StrokeStyle(color=GRAY, width=4), sketch_style=SKETCH) for x in range(300, 1601, 433)]
        
        squash_lbl = make_body("Result: All normal data squashed into Bucket 1.\nInformation Destroyed!", x=960, y=850, color=ORANGE, font_size=56)

        scene.add(SketchAnimation(start_time=standard_quant_start + 0.5, duration=1.0), drawable=sq_title)
        scene.add(SketchAnimation(start_time=standard_quant_start + 2.0, duration=1.0), drawable=axis_x)
        for i, d in enumerate(data_pts):
            scene.add(SketchAnimation(start_time=standard_quant_start + 3.0 + i*0.1, duration=0.3), drawable=d)
        scene.add(SketchAnimation(start_time=standard_quant_start + 4.0, duration=0.8), drawable=norm_lbl)
        
        scene.add(SketchAnimation(start_time=standard_quant_start + 9.0, duration=0.8), drawable=outlier)
        scene.add(SketchAnimation(start_time=standard_quant_start + 9.5, duration=0.8), drawable=out_lbl)
        
        scene.add(SketchAnimation(start_time=standard_quant_start + 12.0, duration=1.0), drawable=bucket_line)
        for t in b_ticks:
            scene.add(SketchAnimation(start_time=standard_quant_start + 12.5, duration=0.5), drawable=t)
        
        scene.add(SketchAnimation(start_time=standard_quant_start + 15.0, duration=1.5), drawable=squash_lbl)

        sq_drawables =[sq_title, axis_x, norm_lbl, outlier, out_lbl, bucket_line, squash_lbl] + data_pts + b_ticks

        # ---------------------------------------------------------
        # SECTION 3: The Traditional Fix & Overhead (~1m20s - ~1m45s)
        # ---------------------------------------------------------
        make_eraser(sq_drawables, scene, start_time=overhead_start - 1.2)
        
        ov_title = make_title("Traditional Fix: Block Quantization", y=150, color=ORANGE)
        
        block_math = Math(r"$\text{Block}_i \rightarrow \text{Quantized}(x) \times \text{Scale}_{FP16}$", position=(960, 300), font_size=64, stroke_style=StrokeStyle(color=BLACK, width=2))
        
        overhead_table = Table(
            data=[
                ["Block 1 (32 vals)", "Scale FP16 (16 bits)"],
                ["Block 2 (32 vals)", "Scale FP16 (16 bits)"],
                ["Block 3 (32 vals)", "Scale FP16 (16 bits)"]
            ],
            top_left=(560, 450),
            col_widths=[450, 450],
            row_heights=[100, 100, 100],
            font_size=48,
            header_fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=stroke,
            sketch_style=SKETCH
        )
        
        waste_text = make_body("Massive Metadata Overhead!\nRuins compression ratio for 3-bit targets.", x=960, y=850, color=RED, font_size=64)

        scene.add(SketchAnimation(start_time=overhead_start + 0.5, duration=1.0), drawable=ov_title)
        scene.add(SketchAnimation(start_time=overhead_start + 2.0, duration=1.5), drawable=block_math)
        scene.add(SketchAnimation(start_time=overhead_start + 6.0, duration=2.0), drawable=overhead_table)
        scene.add(SketchAnimation(start_time=overhead_start + 12.0, duration=1.5), drawable=waste_text)

        ov_drawables =[ov_title, block_math, overhead_table, waste_text]

        # ---------------------------------------------------------
        # SECTION 4: TurboQuant Stage 1 - Rotation (~1m45s - ~2m40s)
        # ---------------------------------------------------------
        make_eraser(ov_drawables, scene, start_time=turboquant_start - 1.2)
        
        tq1_title = make_title("Stage 1: Random Orthogonal Rotation", y=150, color=PURPLE)
        
        rot_math = Math(r"$X_{rotated} = X \times R_{orthogonal}$", position=(960, 220), font_size=80, stroke_style=StrokeStyle(color=PURPLE, width=3))
        
        # 3 Panels: Before -> Operation -> After
        
        # 1. Before (Spike)
        ax1_x = Line(start=(150, 700), end=(550, 700), stroke_style=stroke)
        ax1_y = Line(start=(150, 700), end=(150, 400), stroke_style=stroke)
        p1 =[(150, 680), (250, 690), (350, 420), (450, 685), (550, 690)] # Massive spike
        spike_path = LinearPath(points=p1, stroke_style=StrokeStyle(color=RED, width=6), sketch_style=SKETCH)
        lbl_spike = make_body("Extreme Spike", x=350, y=820, color=RED, font_size=40)
        
        # 2. Matrix Multiplication Arrow
        arr_mul = Arrow(start_point=(650, 550), end_point=(850, 550), stroke_style=StrokeStyle(color=BLACK, width=6))
        # Separate the label into two lines, and add a strikethrough line over 'R Matrix'
        lbl_mul_top = make_body("Multiply by", x=750, y=500, color=BLACK, font_size=40)
        lbl_mul_bottom = make_body("R Matrix", x=750, y=540, color=BLACK, font_size=40)
        # Draw a strikethrough line over 'R Matrix'
        strikethrough = Line(start=(670, 540), end=(830, 540), stroke_style=StrokeStyle(color=BLACK, width=5))

        # 3. After (Gaussian)
        ax2_x = Line(start=(1350, 700), end=(1750, 700), stroke_style=stroke)
        ax2_y = Line(start=(1350, 700), end=(1350, 400), stroke_style=stroke)
        
        # Generate bell curve points
        bell_pts =[]
        for x in range(1350, 1751, 10):
            norm_x = (x - 1550) / 70
            y = 700 - 200 * math.exp(-0.5 * norm_x**2)
            bell_pts.append((x, y))
        bell_curve = Curve(points=bell_pts, stroke_style=StrokeStyle(color=GREEN, width=6), sketch_style=SKETCH)
        lbl_gauss = make_body("Smooth Gaussian\nDistribution", x=1550, y=820, color=GREEN, font_size=40)
        
        iso_text = make_body("Energy is smeared uniformly across all dimensions.\nOutliers vanish. Data becomes isotropic.", x=960, y=970, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=turboquant_start + 0.5, duration=1.0), drawable=tq1_title)
        scene.add(SketchAnimation(start_time=stage1_start + 1.0, duration=1.5), drawable=rot_math)
        
        scene.add(SketchAnimation(start_time=stage1_start + 4.0, duration=1.0), drawable=ax1_x)
        scene.add(SketchAnimation(start_time=stage1_start + 4.0, duration=1.0), drawable=ax1_y)
        scene.add(SketchAnimation(start_time=stage1_start + 5.0, duration=1.5), drawable=spike_path)
        scene.add(SketchAnimation(start_time=stage1_start + 6.5, duration=0.8), drawable=lbl_spike)
        
        scene.add(SketchAnimation(start_time=stage1_start + 9.0, duration=1.0), drawable=arr_mul)
        scene.add(SketchAnimation(start_time=stage1_start + 9.5, duration=0.8), drawable=lbl_mul_top)
        scene.add(SketchAnimation(start_time=stage1_start + 9.7, duration=0.8), drawable=lbl_mul_bottom)
        scene.add(SketchAnimation(start_time=stage1_start + 9.7, duration=0.8), drawable=strikethrough)
        
        scene.add(SketchAnimation(start_time=stage1_start + 14.0, duration=1.0), drawable=ax2_x)
        scene.add(SketchAnimation(start_time=stage1_start + 14.0, duration=1.0), drawable=ax2_y)
        scene.add(SketchAnimation(start_time=stage1_start + 15.0, duration=2.0), drawable=bell_curve)
        scene.add(SketchAnimation(start_time=stage1_start + 17.0, duration=1.0), drawable=lbl_gauss)

        # Erase previous elements before Lloyd-Max overlay and explanation
        tq1_drawables_pre_lloyd = [tq1_title, rot_math, ax1_x, ax1_y, spike_path, lbl_spike, arr_mul, lbl_mul_top, lbl_mul_bottom, strikethrough, ax2_x, ax2_y, bell_curve, lbl_gauss]
        make_eraser(tq1_drawables_pre_lloyd, scene, start_time=lloyd_max_start - 1.2)

        # LLOYD MAX OVERLAY and explanation
        lm_box = FlowchartProcess("Global Lloyd-Max Quantizer\n(Zero Per-Block Overhead)", top_left=(660, 400), width=600, height=180, font_size=56, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.9), stroke_style=StrokeStyle(color=GREEN, width=4))
        scene.add(SketchAnimation(start_time=lloyd_max_start + 0.5, duration=1.5), drawable=lm_box)
        scene.add(SketchAnimation(start_time=lloyd_max_start + 2.5, duration=2.0), drawable=iso_text)

        tq1_drawables = tq1_drawables_pre_lloyd + [lm_box, iso_text]

        # ---------------------------------------------------------
        # SECTION 5: Stage 2 - QJL Residual Correction (~2m40s - ~3m40s)
        # ---------------------------------------------------------
        make_eraser(tq1_drawables, scene, start_time=stage2_start - 1.2)
        
        tq2_title = make_title("Stage 2: Quantized Johnson-Lindenstrauss (QJL)", y=150, color=TEAL)
        
        err_math = Math(r"$\text{Residual Error } (E) = \text{Original} - \text{Quantized}$", position=(960, 250), font_size=64, stroke_style=StrokeStyle(color=BLACK, width=2))
        
        bias_warn = make_body("Ignoring this error causes Biased Attention!", x=960, y=350, color=RED, font_size=48)
        
        # QJL Process Flow
        err_box = FlowchartProcess("Error Matrix E", top_left=(250, 450), width=350, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=stroke)
        arr_qjl = Arrow(start_point=(600, 510), end_point=(750, 510), stroke_style=stroke)
        
        qjl_proj = FlowchartProcess("Project onto\nRandom Gaussian Matrix", top_left=(750, 420), width=450, height=180, font_size=42, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        arr_sign = Arrow(start_point=(1200, 510), end_point=(1350, 510), stroke_style=stroke)
        
        sign_box = FlowchartProcess("Take Sign()\n(+1 or -1)", top_left=(1350, 450), width=300, height=120, font_size=48, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4), stroke_style=stroke)
        
        bit_cost = make_body("Cost: Exactly 1 extra bit per element.", x=1500, y=620, color=GREEN, font_size=40)

        attn_math = Math(r"$\text{Attention} \approx (\hat{Q} \cdot \hat{K}^T) + c(S_Q \cdot S_K^T)$", position=(960, 750), font_size=80, stroke_style=StrokeStyle(color=BLUE, width=3))
        unbiased_txt = make_body("Perfectly Unbiased Mathematical Estimate!", x=960, y=900, color=GREEN, font_size=64)

        scene.add(SketchAnimation(start_time=stage2_start + 0.5, duration=1.0), drawable=tq2_title)
        scene.add(SketchAnimation(start_time=stage2_start + 3.0, duration=1.5), drawable=err_math)
        scene.add(SketchAnimation(start_time=stage2_start + 7.0, duration=1.0), drawable=bias_warn)
        
        scene.add(SketchAnimation(start_time=qjl_start + 1.0, duration=1.0), drawable=err_box)
        scene.add(SketchAnimation(start_time=qjl_start + 3.0, duration=0.8), drawable=arr_qjl)
        scene.add(SketchAnimation(start_time=qjl_start + 4.0, duration=1.5), drawable=qjl_proj)
        scene.add(SketchAnimation(start_time=qjl_start + 7.0, duration=0.8), drawable=arr_sign)
        scene.add(SketchAnimation(start_time=qjl_start + 8.0, duration=1.5), drawable=sign_box)
        scene.add(SketchAnimation(start_time=qjl_start + 10.0, duration=1.0), drawable=bit_cost)
        
        scene.add(SketchAnimation(start_time=math_magic_start + 1.0, duration=2.5), drawable=attn_math)
        scene.add(SketchAnimation(start_time=math_magic_start + 12.0, duration=1.5), drawable=unbiased_txt)

        tq2_drawables =[tq2_title, err_math, bias_warn, err_box, arr_qjl, qjl_proj, arr_sign, sign_box, bit_cost, attn_math, unbiased_txt]

        # ---------------------------------------------------------
        # SECTION 6: Results & Outro (~3m40s - End)
        # ---------------------------------------------------------
        make_eraser(tq2_drawables, scene, start_time=results_start - 1.2)
        
        res_title = make_title("TurboQuant Redefines LLM Efficiency", y=150, color=BLACK)

        res_table = Table(
            data=[
                ["Metric", "Standard FP16", "TurboQuant"],
                ["KV Cache Memory", "40+ GB", "6.6 GB (6x Smaller)"],["Attention Speed", "Baseline", "8x Faster Throughput"],["Accuracy Loss", "None", "Lossless / Negligible"],
                ["Calibration Data", "None needed", "Zero Retraining"]
            ],
            top_left=(310, 300),
            col_widths=[400, 400, 500],
            row_heights=[100, 100, 100, 100, 100],
            font_size=48,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=stroke,
            sketch_style=SKETCH
        )

        outro_text = make_body("Unlocking million-token contexts on consumer hardware.", y=950, color=BLUE, font_size=64)

        scene.add(SketchAnimation(start_time=results_start + 0.5, duration=1.0), drawable=res_title)
        scene.add(SketchAnimation(start_time=results_start + 3.0, duration=3.0), drawable=res_table)
        scene.add(SketchAnimation(start_time=outro_start + 1.0, duration=2.0), drawable=outro_text)

        return tracker.end_time + 2.0


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH, regenerate=True))
    final_duration = build_scene()
    print("Rendering ultimate TurboQuant masterclass animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")


if __name__ == "__main__":
    main()