import os
import asyncio
import edge_tts
from handanim.core import Scene, FillStyle, StrokeStyle, SketchStyle, DrawableGroup
from handanim.primitives.eraser import Eraser
from handanim.core.scene import tts_speech
from handanim.animations import SketchAnimation, FadeInAnimation, FadeOutAnimation
from handanim.primitives import (
    Text, Rectangle, Circle, Line, Arrow, Polygon
)

# ─────────────────────────────────────────────
# CANVAS & LAYOUT CONSTANTS  (1920 × 1080)
# ─────────────────────────────────────────────
W, H = 1920, 1080
SAFE_L, SAFE_R = 60, 1860        # horizontal safe zone
SAFE_T, SAFE_B = 60, 970         # vertical safe zone

# Two-column panel geometry
LP_X, LP_W = 60, 840             # left panel  : x=60..900
RP_X, RP_W = 1020, 840          # right panel : x=1020..1860
LP_CX = LP_X + LP_W // 2        # 480
RP_CX = RP_X + RP_W // 2        # 1440
CX = W // 2                     # 960  (full-width centre)

PANEL_TOP = 150                  # panels start below heading
PANEL_H   = 790                  # panels end at y=940 (< SAFE_B)

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
BLACK      = (0.05, 0.05, 0.05)
WHITE      = (0.98, 0.98, 0.98)
GRAY       = (0.55, 0.55, 0.55)
DARK_GRAY  = (0.22, 0.22, 0.22)
LIGHT_GRAY = (0.82, 0.82, 0.82)

BLUE       = (0.10, 0.35, 0.85)
DARK_BLUE  = (0.05, 0.20, 0.60)
SKY_BLUE   = (0.40, 0.70, 1.00)
CYAN       = (0.00, 0.75, 0.90)

GREEN      = (0.10, 0.72, 0.40)
DARK_GREEN = (0.05, 0.50, 0.25)

RED        = (0.88, 0.15, 0.20)
CORAL      = (1.00, 0.45, 0.40)

ORANGE     = (0.95, 0.55, 0.10)
AMBER      = (1.00, 0.75, 0.20)

PURPLE     = (0.55, 0.20, 0.80)
VIOLET     = (0.70, 0.45, 1.00)

PINK       = (0.92, 0.30, 0.65)
TEAL       = (0.10, 0.65, 0.65)
INDIGO     = (0.30, 0.25, 0.78)

PASTEL_BLUE   = (0.80, 0.88, 1.00)
PASTEL_GREEN  = (0.78, 0.96, 0.85)
PASTEL_RED    = (1.00, 0.82, 0.82)
PASTEL_ORANGE = (1.00, 0.91, 0.76)
PASTEL_PURPLE = (0.91, 0.82, 1.00)
PASTEL_CYAN   = (0.80, 0.96, 1.00)
PASTEL_MINT   = (0.85, 1.00, 0.90)
PASTEL_AMBER  = (1.00, 0.97, 0.82)

# Use better font and primary color
FONT  = "fredericka_the_great"
COLOR_PRIMARY = BLUE
FPS   = 24
VOICE = "en-US-JennyNeural"
RATE  = "+4%"

# ─────────────────────────────────────────────
# TTS PROVIDER
# ─────────────────────────────────────────────
class EdgeTTSProvider:
    @tts_speech
    def synthesize(self, speech: str, output_path: str, **kwargs) -> str:
        communicate = edge_tts.Communicate(speech, **kwargs)
        asyncio.run(communicate.save(output_path))
        return output_path


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def heading(text, color=BLUE, size=52):
    """Full-width scene heading at y=78."""
    return Text(text=text, position=(CX, 78), font_size=size,
                stroke_style=StrokeStyle(color=color, width=3), font_name=FONT)

def label(text, x, y, color=DARK_GRAY, size=30, width=2):
    return Text(text=text, position=(x, y), font_size=size,
                stroke_style=StrokeStyle(color=color, width=width), font_name=FONT)

def panel(x, y, w, h, stroke_col, fill_col, roughness=2):
    return Rectangle(
        top_left=(x, y), width=w, height=h,
        stroke_style=StrokeStyle(color=stroke_col, width=2),
        fill_style=FillStyle(color=fill_col, opacity=0.15),
        sketch_style=SketchStyle(roughness=roughness),
    )

def solid_rect(x, y, w, h, stroke_col, fill_col, opacity=0.55, roughness=1):
    return Rectangle(
        top_left=(x, y), width=w, height=h,
        stroke_style=StrokeStyle(color=stroke_col, width=2),
        fill_style=FillStyle(color=fill_col, opacity=opacity),
        sketch_style=SketchStyle(roughness=roughness),
    )

def arrow_down(x, y1, y2, color=ORANGE, width=3):
    return Arrow(
        start_point=(x, y1), end_point=(x, y2),
        arrow_head_type="->", arrow_head_size=22, arrow_head_angle=38,
        stroke_style=StrokeStyle(color=color, width=width),
    )

def arrow_right(x1, x2, y, color=ORANGE, width=3):
    return Arrow(
        start_point=(x1, y), end_point=(x2, y),
        arrow_head_type="->", arrow_head_size=22, arrow_head_angle=38,
        stroke_style=StrokeStyle(color=color, width=width),
    )

def sketch(scene, drawable, t, dur=1.0):
    scene.add(SketchAnimation(start_time=scene.timeline_cursor + t, duration=dur),
              drawable=drawable)

def erase(scene, objects_to_erase, at, duration=1.5):
    """Use eraser tool to clean up the canvas similar to LLM course style."""
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=scene.timeline_cursor + at, duration=duration), 
              drawable=eraser)

def fadeout(scene, elements, at):
    scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + at, duration=1.5),
              drawable=DrawableGroup(elements=elements))


# ══════════════════════════════════════════════
# SCENE 1  ─  CINEMATIC TITLE  (~60 s)
# ══════════════════════════════════════════════
def scene_title(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Imagine reading seven complete novels — in a single prompt — while an AI "
            "reasons through every line without slowing down. That is not a future dream. "
            "That is DeepSeek-V4, released few days back on HuggingFace for the world. "
            "With one-point-six trillion parameters, a native one-million-token context "
            "window, and inference costs only twenty-seven percent of its predecessor, "
            "DeepSeek-V4 is the most efficient large-scale open model ever trained. "
            "In the next fifteen minutes, we will go deep on every architectural innovation "
            "that makes this possible: Compressed Sparse Attention, Heavily Compressed "
            "Attention, Manifold-Constrained Hyper-Connections, the Muon optimizer, "
            "and the On-Policy Distillation post-training pipeline. "
            "Get ready — this one is a masterclass in AI engineering."
        ),
        voice=VOICE, rate=RATE,
    ):
        # Drop-shadow title
        shadow = Text("DeepSeek-V4", position=(CX+4, 344),
                      font_size=148, font_name=FONT,
                      stroke_style=StrokeStyle(color=LIGHT_GRAY, width=7))
        title  = Text("DeepSeek-V4", position=(CX, 340),
                      font_size=148, font_name=FONT,
                      stroke_style=StrokeStyle(color=COLOR_PRIMARY, width=5))
        sub    = label("Towards Highly Efficient Million-Token Context Intelligence",
                       CX, 510, DARK_GRAY, 42, 2)
        tag    = label("1.6T Parameters  ·  1M Token Context  ·  Open Source",
                       CX, 600, ORANGE, 34, 2)
        stats1 = label("27% inference FLOPs  vs  DeepSeek-V3.2", CX, 690, GREEN, 32, 2)
        stats2 = label("10% KV Cache size  vs  DeepSeek-V3.2",   CX, 750, GREEN, 32, 2)
        credit = label("A Complete Technical Deep Dive", CX, 860, GRAY, 28, 1)

        all_els = [shadow, title, sub, tag, stats1, stats2, credit]

        sketch(scene, shadow, 0.0, 3.0)
        sketch(scene, title,  0.3, 3.0)
        sketch(scene, sub,    2.8, 2.0)
        sketch(scene, tag,    4.2, 1.8)
        sketch(scene, stats1, 5.5, 1.5)
        sketch(scene, stats2, 6.4, 1.5)
        sketch(scene, credit, 7.5, 1.5)

        erase(scene, all_els, 52)


# ══════════════════════════════════════════════
# SCENE 2  ─  THE CONTEXT BOTTLENECK  (~90 s)
# ══════════════════════════════════════════════
def scene_context_problem(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "To understand why DeepSeek-V4 matters, we must first understand the "
            "fundamental bottleneck that has crippled long-context AI for years. "
            "Traditional Transformer attention is quadratic in complexity. If you "
            "double the number of tokens, the computation quadruples. At one million "
            "tokens, this becomes completely unworkable. A standard model would need "
            "one quintillion floating-point operations just for attention. "
            "But that is only half the problem. Every token you process also requires "
            "a Key-Value cache entry. In a standard model at one million tokens, "
            "this cache alone would require hundreds of gigabytes of GPU memory "
            "— more than most data centers can allocate to a single request. "
            "DeepSeek-V4 attacks BOTH problems simultaneously. Through Compressed "
            "Sparse Attention and Heavily Compressed Attention, it reduces inference "
            "computation to approximately linear growth and shrinks the KV cache to "
            "just two percent of a standard BF16 GQA baseline at one million tokens. "
            "This is not an incremental improvement. This is a structural breakthrough "
            "that makes one-million-token contexts economically viable for the first time. "
            "Let us see exactly how they did it — starting with what DeepSeek-V4 "
            "inherits from its predecessors."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("The Long-Context Bottleneck", BLUE)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left panel: Quadratic problem ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, RED, PASTEL_RED)
        sketch(scene, lp, 1.5, 1.2)

        lh = label("Standard Attention", LP_CX, 210, RED, 36, 2)
        sketch(scene, lh, 2.2, 1.0)
        lsub = label("O(N²) complexity", LP_CX, 265, DARK_GRAY, 28, 1)
        sketch(scene, lsub, 2.8, 0.8)

        # draw a grid of "active attention" cells – all red (expensive)
        cells_l = []
        for row in range(6):
            for col in range(7):
                cx_ = LP_X + 60 + col * 106
                cy_ = 310 + row * 96
                c = solid_rect(cx_-44, cy_-38, 88, 76, RED, PASTEL_RED, 0.55)
                cells_l.append(c)

        t = 3.4
        for c in cells_l:
            sketch(scene, c, t, 0.25)
            t += 0.06

        cost_l = label("2x tokens → 4x compute", LP_CX, 900, RED, 30, 2)
        sketch(scene, cost_l, t, 0.9)
        t += 0.8

        # ── Right panel: V4 solution ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, GREEN, PASTEL_GREEN)
        sketch(scene, rp, t, 1.2)
        t += 0.5

        rh = label("DeepSeek-V4 Hybrid Attention", RP_CX, 210, GREEN, 34, 2)
        sketch(scene, rh, t, 1.0)
        t += 0.6

        rsub = label("Near-linear via compression", RP_CX, 265, DARK_GRAY, 28, 1)
        sketch(scene, rsub, t, 0.8)
        t += 0.6

        # sparse grid – only ~15% cells active
        active = {0, 1, 7, 14, 21, 28, 35, 36}
        cells_r = []
        for row in range(6):
            for col in range(7):
                idx = row * 7 + col
                cx_ = RP_X + 60 + col * 106
                cy_ = 310 + row * 96
                if idx in active:
                    c = solid_rect(cx_-44, cy_-38, 88, 76, GREEN, PASTEL_GREEN, 0.75)
                else:
                    c = solid_rect(cx_-44, cy_-38, 88, 76, LIGHT_GRAY, LIGHT_GRAY, 0.20)
                cells_r.append(c)

        for c in cells_r:
            sketch(scene, c, t, 0.25)
            t += 0.05

        kv_stat  = label("KV Cache: 2% of BF16 GQA baseline", RP_CX, 890, GREEN, 28, 2)
        flop_stat = label("at 1M-token context window",        RP_CX, 935, GREEN, 26, 1)
        sketch(scene, kv_stat,  t, 0.9)
        sketch(scene, flop_stat, t+0.4, 0.8)

        all_els = ([hd, lp, lh, lsub, cost_l, rp, rh, rsub, kv_stat, flop_stat]
                   + cells_l + cells_r)
        erase(scene, all_els, 82)


# ══════════════════════════════════════════════
# SCENE 3  ─  ARCHITECTURE OVERVIEW  (~85 s)
# ══════════════════════════════════════════════
def scene_architecture_overview(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "DeepSeek-V4 comes in two flavors. DeepSeek-V4-Pro has one-point-six "
            "trillion total parameters with forty-nine billion activated per token, "
            "sixty-one Transformer layers, and a hidden dimension of seven-thousand "
            "one-hundred and sixty-eight. DeepSeek-V4-Flash is the efficient variant "
            "with two-hundred and eighty-four billion total parameters, thirteen billion "
            "activated, forty-three layers, and a hidden dimension of four-thousand "
            "and ninety-six. Both models were pre-trained on over thirty-two trillion "
            "tokens and both natively support one-million-token contexts. "
            "The architecture introduces three major innovations over DeepSeek-V3. "
            "First: Manifold-Constrained Hyper-Connections, or mHC, which replace "
            "standard residual connections to enable stable deep network training. "
            "Second: Hybrid Attention, combining Compressed Sparse Attention and "
            "Heavily Compressed Attention in an interleaved pattern across layers "
            "to achieve dramatic gains in long-context efficiency. "
            "Third: The Muon optimizer, replacing AdamW for most modules, which uses "
            "orthogonalized gradient updates for faster convergence and better stability. "
            "On top of this, the MoE Feed-Forward architecture from DeepSeek-V3 is "
            "retained with a few targeted refinements. Let us go through each innovation "
            "in depth, starting with the foundational Hyper-Connections."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Architecture Overview", INDIGO)
        sketch(scene, hd, 0.0, 2.0)

        # ── Pro Model Card ──
        pro_box = panel(LP_X, PANEL_TOP, LP_W, 400, BLUE, PASTEL_BLUE)
        sketch(scene, pro_box, 1.5, 1.2)
        sketch(scene, label("DeepSeek-V4-Pro", LP_CX, 195, BLUE, 38, 2), 2.2, 1.0)

        pro_rows = [
            ("Total Parameters",    "1.6 Trillion"),
            ("Activated / Token",   "49 Billion"),
            ("Transformer Layers",  "61"),
            ("Hidden Dimension",    "7,168"),
            ("Pre-training Tokens", "33 Trillion"),
        ]
        t = 3.0
        for k, v in pro_rows:
            sketch(scene, label(f"• {k}:", LP_CX-80, 260+pro_rows.index((k,v))*70, DARK_GRAY, 26, 1), t, 0.5)
            sketch(scene, label(v, LP_CX+180, 260+pro_rows.index((k,v))*70, BLUE, 28, 2), t+0.2, 0.5)
            t += 0.4

        # ── Flash Model Card ──
        fl_box = panel(LP_X, PANEL_TOP+430, LP_W, 370, TEAL, PASTEL_CYAN)
        sketch(scene, fl_box, t, 1.2)
        t += 0.5
        sketch(scene, label("DeepSeek-V4-Flash", LP_CX, PANEL_TOP+485, TEAL, 36, 2), t, 1.0)
        t += 0.5

        flash_rows = [
            ("Total Parameters",    "284 Billion"),
            ("Activated / Token",   "13 Billion"),
            ("Transformer Layers",  "43"),
            ("Hidden Dimension",    "4,096"),
        ]
        for k, v in flash_rows:
            sketch(scene, label(f"• {k}:", LP_CX-80, 640+flash_rows.index((k,v))*62, DARK_GRAY, 26, 1), t, 0.5)
            sketch(scene, label(v, LP_CX+180, 640+flash_rows.index((k,v))*62, TEAL, 28, 2), t+0.2, 0.5)
            t += 0.38

        # ── Right panel: 3 innovations ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, PURPLE, PASTEL_PURPLE)
        sketch(scene, rp, t, 1.2)
        t += 0.5

        sketch(scene, label("Three Key Innovations", RP_CX, 200, PURPLE, 36, 2), t, 1.0)
        t += 0.7

        innovations = [
            (PURPLE, "1.  mHC",              "Manifold-Constrained Hyper-Connections"),
            (PURPLE, "    Replaces residuals",  "→ Stable deep-layer signal propagation"),
            (BLUE,   "2.  Hybrid Attention",  "CSA + HCA  interleaved across layers"),
            (BLUE,   "    27% FLOPs of V3.2", "→ Near-linear long-context compute"),
            (AMBER,  "3.  Muon Optimizer",    "Orthogonalized gradient updates"),
            (AMBER,  "    Faster convergence","→ Replaces AdamW for most modules"),
        ]
        row_y = 290
        for col, title, desc in innovations:
            sketch(scene, label(title, RP_CX, row_y, col, 28, 2), t, 0.6)
            t += 0.3
            sketch(scene, label(desc, RP_CX, row_y+42, DARK_GRAY, 24, 1), t, 0.5)
            t += 0.5
            row_y += 104

        all_els = [hd, pro_box, fl_box, rp]
        erase(scene, all_els, 78)


# ══════════════════════════════════════════════
# SCENE 4  ─  mHC  (~110 s)
# ══════════════════════════════════════════════
def scene_mhc(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "The first major innovation is Manifold-Constrained Hyper-Connections, mHC. "
            "To understand this, start with standard residual connections. In a classic "
            "Transformer, each layer adds its output directly to the residual stream. "
            "Hyper-Connections, or HC, generalize this by expanding the residual stream "
            "width by a factor — in V4, this factor is four — creating multiple parallel "
            "channels of information flow. This is described by the equation: "
            "X at layer l plus one equals B-sub-l times X at layer l, "
            "plus C-sub-l times F-sub-l applied to A-sub-l times X at layer l. "
            "Here A, B, and C are learned linear mappings. The problem is that in "
            "very deep networks, the B matrix — the residual mapping — can expand "
            "signal magnitudes exponentially. This causes catastrophic numerical "
            "instability during training. "
            "mHC fixes this with one elegant constraint: it forces B to remain "
            "within the Birkhoff polytope — the set of doubly stochastic matrices. "
            "A doubly stochastic matrix has all rows AND all columns summing to one. "
            "This mathematically guarantees the spectral norm stays at or below one, "
            "making the transformation non-expansive. Signals cannot blow up. "
            "The Sinkhorn-Knopp algorithm projects the raw parameter matrix onto "
            "this manifold using twenty iterative normalizations, which is both "
            "computationally cheap and provably convergent. "
            "The result is that mHC adds only six-point-seven percent wall-time overhead "
            "to the training pipeline while unlocking stable training across all "
            "sixty-one layers of DeepSeek-V4-Pro."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Manifold-Constrained Hyper-Connections (mHC)", PURPLE)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left: Standard HC vs mHC concept ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, GRAY, LIGHT_GRAY)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("Standard HC  →  Unstable", LP_CX, 205, RED, 34, 2), 2.2, 1.0)

        chaotic = []
        for i in range(6):
            y = 280 + i * 100
            x1 = LP_X + 80 + (i % 3) * 200
            x2 = LP_X + 80 + ((i+2) % 3) * 200
            w = abs(x2 - x1) + 80
            xmin = min(x1, x2) - 10
            c = solid_rect(xmin, y-18, w, 36, RED, PASTEL_RED, 0.45, 3)
            chaotic.append(c)

        t = 3.0
        for c in chaotic:
            sketch(scene, c, t, 0.35)
            t += 0.15
        sketch(scene, label("B matrix can amplify signals", LP_CX, 890, RED, 28, 2), t, 0.8)
        t += 0.8

        # ── Right: mHC solution ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, PURPLE, PASTEL_PURPLE)
        sketch(scene, rp, t, 1.2)
        t += 0.5
        sketch(scene, label("mHC  →  Manifold Constrained", RP_CX, 205, PURPLE, 34, 2), t, 1.0)
        t += 0.7

        # Sinkhorn iteration diagram
        sketch(scene, label("Raw B̃ (unconstrained)", RP_CX, 270, DARK_GRAY, 26, 1), t, 0.7)
        t += 0.6
        sketch(scene, arrow_down(RP_CX, 295, 355, ORANGE), t, 0.6)
        sketch(scene, label("exp(B̃) → ensure positivity", RP_CX, 330, ORANGE, 24, 1), t, 0.5)
        t += 0.6

        for i in range(4):
            sketch(scene, arrow_down(RP_CX, 360+i*80, 420+i*80, VIOLET), t, 0.4)
            txt = "Row normalise" if i % 2 == 0 else "Column normalise"
            sketch(scene, label(f"  {txt}  (iter {i+1})", RP_CX, 395+i*80, PURPLE, 24, 1), t, 0.4)
            t += 0.4

        sketch(scene, label("× 20 iterations → B ∈ Birkhoff polytope", RP_CX, 705, PURPLE, 26, 2), t, 0.8)
        t += 0.7

        # Guarantee box
        g_box = solid_rect(RP_X+40, 740, RP_W-80, 100, GREEN, PASTEL_GREEN, 0.25)
        sketch(scene, g_box, t, 0.8)
        t += 0.4
        sketch(scene, label("||B||₂ ≤ 1  →  Non-expansive", RP_CX, 782, GREEN, 30, 2), t, 0.7)
        t += 0.4
        sketch(scene, label("Signal propagation guaranteed stable", RP_CX, 826, GREEN, 26, 1), t, 0.6)
        t += 0.6

        sketch(scene, label("Overhead: only +6.7% wall-time", RP_CX, 906, AMBER, 30, 2), t, 0.8)

        all_els = [hd, lp, rp, g_box] + chaotic
        erase(scene, all_els, 100)


# ══════════════════════════════════════════════
# SCENE 5  ─  CSA  (~110 s)
# ══════════════════════════════════════════════
def scene_csa(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Now for the centrepiece of the architecture: Compressed Sparse Attention, CSA. "
            "CSA has three stages. Stage one: token-level compression. Every group of M "
            "consecutive tokens — in DeepSeek-V4-Pro, M equals four — is compressed into "
            "a single Key-Value entry using learned weights and positional biases. "
            "This compression is overlapping: each compressed entry draws from two windows "
            "of M tokens, one looking forward and one looking backward. This reduces "
            "the sequence length to one-quarter immediately. "
            "Stage two: the Lightning Indexer. Rather than performing full attention over "
            "all compressed blocks, CSA uses a lightweight scoring mechanism to rank "
            "blocks by relevance to the current query. This uses low-rank projected "
            "indexer queries and a ReLU-gated dot-product scoring function. "
            "Stage three: Top-K sparse selection. Only the top K compressed blocks are "
            "retained for core attention. In V4-Pro, K equals one-thousand and twenty-four. "
            "The remaining blocks are discarded, making computation truly sparse. "
            "To preserve local context — since strict causality means queries cannot "
            "see tokens within their own compressed block — a Sliding Window Attention "
            "branch adds the most recent one-hundred and twenty-eight uncompressed tokens. "
            "An attention sink trick with learnable logits prevents attention scores from "
            "summing to one, allowing heads to ignore irrelevant content entirely. "
            "The result in the one-million-token setting: DeepSeek-V4-Pro needs only "
            "twenty-seven percent of inference FLOPs compared to DeepSeek-V3.2. "
            "This is the single biggest compute saving in the entire architecture."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Compressed Sparse Attention (CSA)", BLUE)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left panel: Compression pipeline ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("Stage 1: Token Compression", LP_CX, 200, BLUE, 34, 2), 2.2, 1.0)

        # 8 raw tokens
        tokens = []
        for i in range(8):
            tok = solid_rect(LP_X+50+i*98, 250, 88, 68, SKY_BLUE, PASTEL_CYAN, 0.6)
            tokens.append(tok)
        t = 3.0
        for tok in tokens:
            sketch(scene, tok, t, 0.25)
            t += 0.06

        sketch(scene, label("8 Raw KV Tokens  (m=4, compressed 2:1)", LP_CX, 350, DARK_GRAY, 24, 1), t, 0.6)
        t += 0.5
        sketch(scene, arrow_down(LP_CX, 368, 420, ORANGE), t, 0.5)
        t += 0.4

        # 4 compressed entries
        comp_entries = []
        for i in range(4):
            c = solid_rect(LP_X+100+i*180, 428, 150, 68, GREEN, PASTEL_GREEN, 0.65)
            comp_entries.append(c)
        for c in comp_entries:
            sketch(scene, c, t, 0.3)
            t += 0.1

        sketch(scene, label("4 Compressed Entries", LP_CX, 528, GREEN, 26, 1), t, 0.6)
        t += 0.6

        # Stage 2: Lightning Indexer
        sketch(scene, label("Stage 2: Lightning Indexer", LP_CX, 590, PURPLE, 32, 2), t, 0.8)
        t += 0.7
        sketch(scene, label("Low-rank indexer queries score each block", LP_CX, 640, DARK_GRAY, 24, 1), t, 0.6)
        t += 0.5
        sketch(scene, label("ReLU gated dot-product scoring", LP_CX, 680, DARK_GRAY, 24, 1), t, 0.6)
        t += 0.6

        # Stage 3: Top-K
        sketch(scene, label("Stage 3: Top-K Sparse Selection", LP_CX, 740, ORANGE, 32, 2), t, 0.8)
        t += 0.7
        sketch(scene, label("Pro: K=1024   Flash: K=512", LP_CX, 790, ORANGE, 28, 2), t, 0.7)
        t += 0.6

        # SWA
        sketch(scene, label("+ Sliding Window  (n_win = 128 tokens)", LP_CX, 854, TEAL, 28, 2), t, 0.7)
        t += 0.5
        sketch(scene, label("+ Attention Sink  (learnable logits)", LP_CX, 900, TEAL, 26, 1), t, 0.6)
        t += 0.5

        # ── Right panel: Efficiency numbers ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, GREEN, PASTEL_GREEN)
        sketch(scene, rp, t, 1.2)
        t += 0.5

        sketch(scene, label("Efficiency at 1M Tokens", RP_CX, 200, GREEN, 36, 2), t, 1.0)
        t += 0.8

        metrics = [
            (GREEN,  "Inference FLOPs",   "27% of DeepSeek-V3.2"),
            (GREEN,  "KV Cache Size",     "10% of DeepSeek-V3.2"),
            (BLUE,   "KV vs GQA BF16",    "~2% at 1M-token context"),
            (AMBER,  "CSA Compression",   "m = 4  (sequence ÷ 4)"),
            (AMBER,  "Top-K (Pro)",       "K = 1,024 sparse blocks"),
            (AMBER,  "Top-K (Flash)",     "K = 512 sparse blocks"),
            (PURPLE, "SWA Window",        "128 uncompressed tokens"),
            (TEAL,   "Indexer Precision", "FP4 for QK path"),
        ]
        row_y = 295
        for col, key, val in metrics:
            box = solid_rect(RP_X+40, row_y-30, RP_W-80, 64, col, PASTEL_BLUE, 0.10)
            sketch(scene, box, t, 0.5)
            t += 0.2
            sketch(scene, label(key, RP_CX-120, row_y, DARK_GRAY, 26, 1), t, 0.4)
            sketch(scene, label(val, RP_CX+160, row_y, col, 28, 2), t+0.1, 0.4)
            t += 0.42
            row_y += 72

        all_els = ([hd, lp, rp] + tokens + comp_entries)
        erase(scene, all_els, 100)


# ══════════════════════════════════════════════
# SCENE 6  ─  HCA  (~90 s)
# ══════════════════════════════════════════════
def scene_hca(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Interleaved with CSA across the Transformer layers is Heavily Compressed "
            "Attention, HCA. If CSA is a good summary of a chapter, HCA is a one-sentence "
            "summary of an entire book. HCA applies a compression rate M-prime of one "
            "hundred and twenty-eight — thirty-two times more aggressive than CSA's "
            "compression rate of four. Every one-hundred and twenty-eight consecutive "
            "tokens are collapsed into a single Key-Value entry. "
            "Because the compression is so aggressive, HCA does NOT use sparse attention. "
            "Instead, it performs full dense attention over the compressed blocks. "
            "With one-million tokens compressed to under eight thousand entries, "
            "even dense attention is computationally manageable. "
            "The compression mechanism is simpler than CSA: no overlapping windows, "
            "just a straight weighted average using learned positional biases. "
            "Like CSA, HCA also appends a Sliding Window Attention branch for "
            "the most recent one-hundred and twenty-eight uncompressed tokens, "
            "ensuring sharp local awareness. "
            "The interleaved design — alternating CSA and HCA layers — gives the model "
            "two complementary views of the context. CSA provides medium-range selective "
            "attention via sparse top-K selection, while HCA provides broad global "
            "coverage via ultra-compressed dense attention. Together, they cover "
            "the full spectrum from local to global, enabling the model to handle "
            "truly long documents without losing either fine-grained detail or "
            "big-picture understanding."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Heavily Compressed Attention (HCA)", INDIGO)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left: HCA compression diagram ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, INDIGO, PASTEL_PURPLE)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("HCA: Ultra-Heavy Compression", LP_CX, 200, INDIGO, 34, 2), 2.2, 1.0)

        # 12 small token boxes → 1 big compressed entry
        tok_boxes = []
        for row in range(2):
            for col in range(6):
                bx = LP_X + 60 + col * 126
                by = 260 + row * 80
                b = solid_rect(bx, by, 110, 68, VIOLET, PASTEL_PURPLE, 0.40)
                tok_boxes.append(b)

        t = 3.0
        for b in tok_boxes:
            sketch(scene, b, t, 0.18)
            t += 0.05

        sketch(scene, label("128 Raw Tokens (m' = 128)", LP_CX, 435, DARK_GRAY, 24, 1), t, 0.6)
        t += 0.5
        sketch(scene, arrow_down(LP_CX, 452, 510, ORANGE, 3), t, 0.5)
        t += 0.4

        one_entry = solid_rect(LP_CX-160, 518, 320, 80, GREEN, PASTEL_GREEN, 0.65)
        sketch(scene, one_entry, t, 0.8)
        t += 0.5
        sketch(scene, label("1 Compressed KV Entry", LP_CX, 558, GREEN, 28, 2), t, 0.6)
        t += 0.6

        # Dense attention over all compressed blocks
        sketch(scene, label("Dense Attention over all blocks", LP_CX, 640, INDIGO, 30, 2), t, 0.8)
        t += 0.7
        sketch(scene, label("(no Top-K selection needed)", LP_CX, 682, DARK_GRAY, 24, 1), t, 0.6)
        t += 0.6

        # SWA again
        swa = solid_rect(LP_X+40, 730, LP_W-80, 80, TEAL, PASTEL_CYAN, 0.20)
        sketch(scene, swa, t, 0.7)
        t += 0.4
        sketch(scene, label("+ SWA: 128 uncompressed recent tokens", LP_CX, 770, TEAL, 26, 2), t, 0.7)
        t += 0.7

        # ── Right: CSA vs HCA comparison ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, BLUE, PASTEL_BLUE)
        sketch(scene, rp, t, 1.2)
        t += 0.5

        sketch(scene, label("CSA  vs  HCA  —  Side by Side", RP_CX, 200, DARK_BLUE, 34, 2), t, 1.0)
        t += 0.8

        rows_csa_hca = [
            ("Compression Rate",   "m = 4",        "m' = 128"),
            ("Attention Type",     "Sparse Top-K", "Dense Full"),
            ("Top-K (Pro/Flash)",  "1024 / 512",   "N/A (dense)"),
            ("Overlapping Windows","Yes (2×m)",     "No"),
            ("SWA Branch",        "128 tokens",    "128 tokens"),
            ("Focus",             "Medium range",  "Global range"),
            ("Layers in Pro",     "Alternating",   "Alternating"),
        ]
        sketch(scene, label("Attribute", RP_CX-220, 284, DARK_GRAY, 24, 1), t, 0.5)
        sketch(scene, label("CSA",       RP_CX+30,  284, BLUE, 26, 2), t, 0.5)
        sketch(scene, label("HCA",       RP_CX+230, 284, INDIGO, 26, 2), t, 0.5)
        t += 0.5

        row_y = 328
        for attr, cval, hval in rows_csa_hca:
            sketch(scene, label(attr, RP_CX-220, row_y, DARK_GRAY, 22, 1), t, 0.4)
            sketch(scene, label(cval, RP_CX+30, row_y, BLUE, 24, 2), t+0.1, 0.4)
            sketch(scene, label(hval, RP_CX+230, row_y, INDIGO, 24, 2), t+0.1, 0.4)
            t += 0.38
            row_y += 68

        insight = solid_rect(RP_X+40, 830, RP_W-80, 90, AMBER, PASTEL_AMBER, 0.20)
        sketch(scene, insight, t, 0.8)
        t += 0.3
        sketch(scene, label("Together: local + medium + global coverage", RP_CX, 870, AMBER, 26, 2), t, 0.7)
        t += 0.3
        sketch(scene, label("Native 1M-token support unlocked", RP_CX, 912, AMBER, 24, 1), t, 0.6)

        all_els = [hd, lp, rp, one_entry, swa, insight] + tok_boxes
        erase(scene, all_els, 82)


# ══════════════════════════════════════════════
# SCENE 7  ─  MUON OPTIMIZER  (~110 s)
# ══════════════════════════════════════════════
def scene_muon(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Training a model with one-point-six trillion parameters requires more "
            "than architectural tricks — it demands a better optimizer. DeepSeek-V4 "
            "introduces the Muon optimizer for all modules except embeddings, "
            "prediction heads, and normalization layers, which retain AdamW. "
            "The core insight behind Muon is orthogonalization. Every standard gradient "
            "update has a direction and a magnitude. AdamW adapts the magnitude per "
            "parameter but leaves gradients pointing in correlated directions, which "
            "wastes budget on redundant movement. "
            "Muon instead orthogonalizes the update matrix using Newton-Schulz iterations. "
            "Given a gradient matrix G, it computes an orthogonal approximation U V-transpose "
            "using ten iterations in two stages. The first eight iterations use coefficients "
            "three-point-four-four, negative four-point-seven-eight, and two-point-zero-three "
            "to drive rapid convergence. The final two iterations switch to coefficients "
            "two, negative one-point-five, and zero-point-five to lock singular values "
            "precisely at one. "
            "This is combined with the Nesterov momentum trick: instead of using the "
            "current momentum buffer, it uses the lookahead momentum, which empirically "
            "accelerates convergence. The update is then rescaled so its root-mean-square "
            "is zero-point-one-eight, allowing direct reuse of AdamW learning-rate schedules. "
            "An important note: because the attention queries and KV entries already have "
            "RMSNorm applied — a design choice in the CSA and HCA architecture — "
            "attention logits cannot explode. This means V4 does NOT need the "
            "QK-Clip technique other Muon implementations use. "
            "Weight decay of zero-point-one and momentum of zero-point-nine-five "
            "are applied. The result is faster loss convergence and superior final "
            "model quality compared to AdamW training."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("The Muon Optimizer", AMBER)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left: AdamW (standard) ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, GRAY, LIGHT_GRAY)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("AdamW  (Standard)", LP_CX, 200, GRAY, 36, 2), 2.2, 1.0)

        # Random walk visualisation
        adamw_pts = [
            (LP_X+100, 290), (LP_X+280, 420), (LP_X+160, 570),
            (LP_X+440, 490), (LP_X+550, 680), (LP_X+380, 790),
            (LP_X+680, 700), (LP_X+760, 860),
        ]
        t = 3.0
        for i in range(len(adamw_pts)-1):
            ax = Arrow(start_point=adamw_pts[i], end_point=adamw_pts[i+1],
                       arrow_head_type="->", arrow_head_size=18, arrow_head_angle=35,
                       stroke_style=StrokeStyle(color=RED, width=2))
            sketch(scene, ax, t, 0.5)
            t += 0.22
        sketch(scene, label("Correlated updates → slow convergence", LP_CX, 920, RED, 26, 2), t, 0.8)
        t += 0.9

        # ── Right: Muon ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, AMBER, PASTEL_AMBER)
        sketch(scene, rp, t, 1.2)
        t += 0.5
        sketch(scene, label("Muon  (Orthogonal Updates)", RP_CX, 200, AMBER, 34, 2), t, 1.0)
        t += 0.7

        # Orthogonal staircase
        muon_pts = [
            (RP_X+60,  290), (RP_X+230, 290),
            (RP_X+230, 450), (RP_X+400, 450),
            (RP_X+400, 610), (RP_X+560, 610),
            (RP_X+560, 770), (RP_X+730, 770),
        ]
        for i in range(len(muon_pts)-1):
            ax = Arrow(start_point=muon_pts[i], end_point=muon_pts[i+1],
                       arrow_head_type="->", arrow_head_size=18, arrow_head_angle=35,
                       stroke_style=StrokeStyle(color=GREEN, width=2))
            sketch(scene, ax, t, 0.5)
            t += 0.22
        sketch(scene, label("Orthogonal steps = zero redundancy", RP_CX, 850, GREEN, 28, 2), t, 0.8)
        t += 0.8

        # Newton-Schulz detail
        ns_box = solid_rect(RP_X+40, 888, RP_W-80, 52, AMBER, PASTEL_AMBER, 0.25)
        sketch(scene, ns_box, t, 0.6)
        t += 0.3
        sketch(scene, label("Newton-Schulz: 8+2 iters  |  momentum=0.95  |  wd=0.1", RP_CX, 914, DARK_GRAY, 22, 1), t, 0.7)

        all_els = [hd, lp, rp, ns_box]
        erase(scene, all_els, 100)


# ══════════════════════════════════════════════
# SCENE 8  ─  TRAINING STABILITY  (~90 s)
# ══════════════════════════════════════════════
def scene_stability(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Even with mHC and Muon, training a trillion-parameter Mixture-of-Experts "
            "model occasionally hits catastrophic loss spikes — sudden jumps where the "
            "loss value explodes, requiring rollbacks that waste GPU hours. "
            "The DeepSeek team isolated the root cause: routing outliers. The MoE routing "
            "network and the backbone network update simultaneously, creating a vicious "
            "feedback loop. An outlier in one step amplifies the next, until the loss spikes. "
            "Two practical fixes were discovered. "
            "Fix one: Anticipatory Routing. At training step T, the backbone computes "
            "features using current parameters theta-T. But the routing indices — "
            "which expert each token goes to — are computed using the historical "
            "parameters theta at T-minus-delta. This decoupling breaks the feedback loop. "
            "In practice, this is implemented by fetching data one step early and "
            "caching the routing indices. An automatic detector triggers anticipatory "
            "routing when a loss spike begins and reverts to standard training after "
            "a stabilization period. The additional overhead is approximately twenty percent. "
            "Fix two: SwiGLU Clamping. The Feed-Forward networks use SwiGLU activation, "
            "which has two components: a linear component and a gate component. "
            "The team discovered that hard-clamping the linear component to the range "
            "negative ten to positive ten, and capping the gate component's upper bound "
            "at ten, directly eliminates the activation outliers that seed loss spikes. "
            "This costs essentially zero compute overhead. "
            "Together, these two techniques produced fully stable training runs "
            "across both DeepSeek-V4-Pro and DeepSeek-V4-Flash, with no loss spikes "
            "in the final training runs."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Mitigating Training Instability", CORAL)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left: Anticipatory Routing ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("Fix 1: Anticipatory Routing", LP_CX, 200, BLUE, 34, 2), 2.2, 1.0)

        t = 3.0
        steps = [
            (RED,  "Problem: Synchronous router + backbone"),
            (RED,  "update creates feedback amplification"),
            (DARK_GRAY, ""),
            (BLUE, "Solution: At step T →"),
            (BLUE, "  Backbone uses θ_T  (current)"),
            (BLUE, "  Router uses θ_{T-Δt}  (historical)"),
            (DARK_GRAY, ""),
            (GREEN, "Result: Feedback loop broken"),
            (GREEN, "Overhead: ~20% additional wall-time"),
            (DARK_GRAY, ""),
            (AMBER, "Auto-detector triggers when spike begins"),
            (AMBER, "Reverts after stabilization period"),
        ]
        row_y = 275
        for col, txt in steps:
            if txt:
                sketch(scene, label(txt, LP_CX, row_y, col, 26, 1 if col==DARK_GRAY else 2), t, 0.5)
                t += 0.4
            row_y += 60

        # ── Right: SwiGLU Clamping ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, CORAL, PASTEL_RED)
        sketch(scene, rp, t, 1.2)
        t += 0.5
        sketch(scene, label("Fix 2: SwiGLU Clamping", RP_CX, 200, CORAL, 34, 2), t, 1.0)
        t += 0.7

        swiglu_rows = [
            (RED,   "Problem: Outlier activations in FFN"),
            (RED,   "amplify through MoE layers"),
            (DARK_GRAY, ""),
            (CORAL, "SwiGLU: output = σ(W₁x) ⊙ (W₂x)"),
            (DARK_GRAY, ""),
            (GREEN, "Linear component: clamp to [-10, 10]"),
            (GREEN, "Gate component: cap upper bound at 10"),
            (DARK_GRAY, ""),
            (GREEN, "Zero additional compute overhead"),
            (DARK_GRAY, ""),
            (BLUE,  "Combined with Anticipatory Routing:"),
            (BLUE,  "No loss spikes in final training runs"),
        ]
        row_y = 275
        for col, txt in swiglu_rows:
            if txt:
                sketch(scene, label(txt, RP_CX, row_y, col, 26, 1 if col==DARK_GRAY else 2), t, 0.5)
                t += 0.38
            row_y += 60

        all_els = [hd, lp, rp]
        erase(scene, all_els, 82)


# ══════════════════════════════════════════════
# SCENE 9  ─  POST-TRAINING / OPD  (~90 s)
# ══════════════════════════════════════════════
def scene_post_training(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "After pre-training, DeepSeek-V4 undergoes a two-stage post-training pipeline "
            "that replaces the traditional mixed Reinforcement Learning approach entirely. "
            "Stage one: Specialist Training. For each target domain — mathematics, "
            "coding, agent tasks, and instruction following — a separate expert model "
            "is trained from the foundation. Each expert first undergoes Supervised "
            "Fine-Tuning on high-quality domain data, then Reinforcement Learning using "
            "Group Relative Policy Optimization, GRPO. Domain-specific reward models "
            "guide the RL phase. A Generative Reward Model eliminates the need for "
            "human annotation on hard-to-verify tasks, by using the model itself "
            "as both actor and judge. "
            "Stage two: On-Policy Distillation, OPD. Rather than merging expert "
            "weights — which typically degrades performance — OPD trains a single "
            "unified model as a student that learns from over ten expert teacher models. "
            "The student generates its own training trajectories on-policy, "
            "and the loss is the reverse KL divergence between the student distribution "
            "and each weighted teacher distribution. "
            "Crucially, V4 uses full-vocabulary logit distillation rather than "
            "token-level KL approximation. This is more expensive but produces "
            "dramatically more stable gradients and more faithful knowledge transfer. "
            "The FP4 quantization-aware training of MoE expert weights — using "
            "the MXFP4 format — halves memory consumption and will offer one-third "
            "additional speedup on future hardware supporting FP4 natively. "
            "Three reasoning effort modes emerge: Non-Think for fast responses, "
            "Think-High for complex problems, and Think-Max for frontier reasoning."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Post-Training: OPD Pipeline", PINK)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left: Specialist Training ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("Stage 1: Specialist Training", LP_CX, 200, BLUE, 34, 2), 2.2, 1.0)

        domains = [
            (BLUE,   "Mathematics Expert"),
            (GREEN,  "Coding Expert"),
            (ORANGE, "Agent Expert"),
            (PURPLE, "Instruction Expert"),
        ]
        t = 3.0
        for i, (col, dom) in enumerate(domains):
            box = solid_rect(LP_X+60, 280+i*138, LP_W-120, 118, col, PASTEL_BLUE, 0.15)
            sketch(scene, box, t, 0.6)
            t += 0.3
            sketch(scene, label(dom, LP_CX, 320+i*138, col, 28, 2), t, 0.5)
            t += 0.2
            sketch(scene, label("SFT  →  GRPO RL  →  GRM Reward", LP_CX, 360+i*138, DARK_GRAY, 22, 1), t, 0.4)
            t += 0.45

        # ── Right: OPD ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, PINK, PASTEL_RED)
        sketch(scene, rp, t, 1.2)
        t += 0.5

        sketch(scene, label("Stage 2: On-Policy Distillation", RP_CX, 200, PINK, 32, 2), t, 1.0)
        t += 0.7

        # Expert circles
        expert_specs = [
            (RP_X+140, 360, BLUE,   "Math"),
            (RP_X+340, 310, GREEN,  "Code"),
            (RP_X+540, 360, ORANGE, "Agent"),
            (RP_X+730, 310, PURPLE, "Inst."),
        ]
        for ex, ey, ec, el in expert_specs:
            circ = Circle(center=(ex, ey), radius=62,
                          stroke_style=StrokeStyle(color=ec, width=2),
                          fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
                          sketch_style=SketchStyle(roughness=2))
            sketch(scene, circ, t, 0.6)
            t += 0.2
            sketch(scene, label(el, ex, ey, ec, 26, 2), t, 0.4)
            t += 0.3

        # Arrows pointing down to student
        for ex, ey, ec, _ in expert_specs:
            ax = Arrow(start_point=(ex, ey+62), end_point=(RP_CX, 572),
                       arrow_head_type="->", arrow_head_size=16, arrow_head_angle=35,
                       stroke_style=StrokeStyle(color=ORANGE, width=2))
            sketch(scene, ax, t, 0.5)
            t += 0.2

        # Student
        stu = solid_rect(RP_X+220, 576, RP_W-440, 100, PINK, PASTEL_RED, 0.45)
        sketch(scene, stu, t, 0.8)
        t += 0.4
        sketch(scene, label("Unified Student  (DeepSeek-V4)", RP_CX, 614, PINK, 28, 2), t, 0.7)
        t += 0.5
        sketch(scene, label("min Σ wᵢ · D_KL(πθ ∥ πEᵢ)", RP_CX, 656, DARK_GRAY, 24, 1), t, 0.6)
        t += 0.6

        # Full vocab KL
        kl_box = solid_rect(RP_X+40, 700, RP_W-80, 80, GREEN, PASTEL_GREEN, 0.20)
        sketch(scene, kl_box, t, 0.6)
        t += 0.3
        sketch(scene, label("Full-vocabulary logit distillation", RP_CX, 732, GREEN, 26, 2), t, 0.6)
        t += 0.3
        sketch(scene, label("(not token-level KL — more stable grads)", RP_CX, 770, DARK_GRAY, 22, 1), t, 0.5)
        t += 0.5

        # 3 modes
        sketch(scene, label("3 Modes:  Non-Think · Think-High · Think-Max", RP_CX, 852, AMBER, 26, 2), t, 0.8)
        t += 0.4
        sketch(scene, label("FP4 (MXFP4) QAT for MoE experts  →  50% memory", RP_CX, 908, TEAL, 24, 1), t, 0.7)

        all_els = [hd, lp, rp, stu, kl_box]
        erase(scene, all_els, 82)


# ══════════════════════════════════════════════
# SCENE 10  ─  BENCHMARK RESULTS  (~95 s)
# ══════════════════════════════════════════════
def scene_benchmarks(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Let us now look at what all this engineering delivers in practice. "
            "In competitive programming — perhaps the most objective measure of "
            "raw reasoning — DeepSeek-V4-Pro-Max achieves a Codeforces rating of "
            "three-thousand two-hundred and six, placing it twenty-third among all "
            "human competitors on the platform. This is the first time an open model "
            "has matched or exceeded GPT-5.4, which scores three-thousand one-hundred "
            "and sixty-eight. "
            "On LiveCodeBench, V4-Pro-Max scores ninety-three-point-five percent pass-at-one, "
            "again leading all tested models. "
            "For agent tasks — which test a model's ability to use tools, browse the web, "
            "and complete software engineering tasks autonomously — V4-Pro achieves "
            "eighty-point-six percent on SWE-Verified, matching Claude Opus 4.6. "
            "On Terminal Bench 2.0, it scores sixty-seven-point-nine percent, "
            "trailing only GPT-5.4 at seventy-five-point-one. "
            "The long-context results are striking. On the MRCR one-million-token "
            "benchmark, V4-Pro-Max scores eighty-three-point-five percent mean match rate, "
            "beating Gemini 3.1 Pro at seventy-six-point-three and surpassing "
            "Claude Opus 4.6 at ninety-two-point-nine in terms of value-for-cost. "
            "On CorpusQA, V4-Pro scores sixty-two percent, ahead of Gemini 3.1 at "
            "fifty-three-point-eight. "
            "On knowledge tasks, SimpleQA-Verified reveals V4-Pro-Max at fifty-seven-point-nine, "
            "twenty percentage points ahead of the next best open-source model, "
            "though still behind Gemini 3.1 Pro at seventy-five-point-six. "
            "The bottom line: V4-Pro is the strongest open-source model ever released, "
            "competitive with the best closed frontier models, at a fraction of "
            "the inference cost."
        ),
        voice=VOICE, rate=RATE,
    ):
        hd = heading("Benchmark Results  —  V4-Pro-Max vs Frontier Models", GREEN)
        sketch(scene, hd, 0.0, 2.0)

        # ── Left panel: Reasoning & Code ──
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 1.5, 1.2)
        sketch(scene, label("Reasoning & Code", LP_CX, 200, BLUE, 34, 2), 2.2, 1.0)

        benchmarks_l = [
            # (benchmark, V4-Pro-Max, Gemini-3.1-Pro, Claude-4.6, GPT-5.4)
            ("Codeforces (Rating)", "3206", "3052", "—", "3168"),
            ("LiveCodeBench (%)",   "93.5", "91.7", "88.8", "—"),
            ("HMMT 2026 Feb (%)",   "95.2", "94.7", "96.2", "97.7"),
            ("IMOAnswerBench (%)",  "89.8", "81.0", "75.3", "91.4"),
            ("Apex Shortlist (%)",  "90.2", "89.1", "85.9", "78.1"),
            ("HLE (%)",            "37.7", "44.4", "40.0", "39.8"),
        ]

        # Column headers
        t = 3.0
        hdrs = [("Task", LP_CX-200), ("V4", LP_CX+50),
                ("Gem", LP_CX+175), ("Claud", LP_CX+310), ("GPT", LP_CX+440)]
        for hdr_txt, hx in hdrs:
            col = BLUE if hdr_txt == "V4" else DARK_GRAY
            sketch(scene, label(hdr_txt, hx, 262, col, 22, 2 if hdr_txt=="V4" else 1), t, 0.4)
        t += 0.5

        row_y = 302
        for bname, v4, gem, claude, gpt in benchmarks_l:
            # Highlight best in green
            vals = [(v4, LP_CX+50, BLUE), (gem, LP_CX+175, DARK_GRAY),
                    (claude, LP_CX+310, DARK_GRAY), (gpt, LP_CX+440, DARK_GRAY)]
            sketch(scene, label(bname, LP_CX-200, row_y, DARK_GRAY, 21, 1), t, 0.4)
            for vtext, vx, vc in vals:
                c = GREEN if vtext == v4 else vc
                w = 2 if c == GREEN else 1
                sketch(scene, label(vtext, vx, row_y, c, 23, w), t, 0.3)
            t += 0.45
            row_y += 78

        # ── Right panel: Agent & Long-Context ──
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, TEAL, PASTEL_MINT)
        sketch(scene, rp, t, 1.2)
        t += 0.5
        sketch(scene, label("Agent & Long-Context", RP_CX, 200, TEAL, 34, 2), t, 1.0)
        t += 0.7

        benchmarks_r = [
            ("SWE-Verified (%)",       "80.6", "80.6", "80.8", "—"),
            ("Terminal Bench 2.0 (%)", "67.9", "68.5", "65.4", "75.1"),
            ("BrowseComp (%)",         "83.4", "85.9", "83.7", "82.7"),
            ("Toolathlon (%)",         "51.8", "48.8", "47.2", "54.6"),
            ("MRCR 1M-token (%)",      "83.5", "76.3", "92.9", "—"),
            ("CorpusQA 1M (%)",        "62.0", "53.8", "71.7", "—"),
            ("SimpleQA-Verified (%)","57.9", "75.6", "46.2", "45.3"),
        ]

        hdrs_r = [("Task", RP_CX-200), ("V4", RP_CX+50),
                  ("Gem", RP_CX+175), ("Claud", RP_CX+310), ("GPT", RP_CX+440)]
        for hdr_txt, hx in hdrs_r:
            col = TEAL if hdr_txt == "V4" else DARK_GRAY
            sketch(scene, label(hdr_txt, hx, 262, col, 22, 2 if hdr_txt=="V4" else 1), t, 0.4)
        t += 0.5

        row_y = 302
        for bname, v4, gem, claude, gpt in benchmarks_r:
            sketch(scene, label(bname, RP_CX-200, row_y, DARK_GRAY, 21, 1), t, 0.4)
            for vtext, vx, vc in [(v4, RP_CX+50, TEAL), (gem, RP_CX+175, DARK_GRAY),
                                   (claude, RP_CX+310, DARK_GRAY), (gpt, RP_CX+440, DARK_GRAY)]:
                c = GREEN if vtext == v4 else vc
                w = 2 if c == GREEN else 1
                sketch(scene, label(vtext, vx, row_y, c, 23, w), t, 0.3)
            t += 0.42
            row_y += 68

        all_els = [hd, lp, rp]
        erase(scene, all_els, 86)


# ══════════════════════════════════════════════
# SCENE 11  ─  CONCLUSION  (~65 s)
# ══════════════════════════════════════════════
def scene_conclusion(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "DeepSeek-V4 is a landmark. Let us recap what makes it special. "
            "The Manifold-Constrained Hyper-Connections enable stable sixty-one-layer "
            "training by constraining residual mappings to doubly stochastic matrices. "
            "The Hybrid Attention architecture — interleaving Compressed Sparse Attention "
            "with compression rate four and Heavily Compressed Attention with "
            "compression rate one-hundred-twenty-eight — slashes inference FLOPs to "
            "twenty-seven percent of the previous generation. "
            "The KV cache at one-million tokens is just ten percent of DeepSeek-V3.2, "
            "making production deployment genuinely economical. "
            "The Muon optimizer with hybrid Newton-Schulz orthogonalization delivers "
            "faster convergence with no attention logit instability. "
            "Anticipatory Routing and SwiGLU Clamping eliminate loss spikes in "
            "trillion-parameter MoE training. "
            "And On-Policy Distillation consolidates over ten expert models into a "
            "single unified model without weight merging degradation. "
            "The result: an open-source model that ranks twenty-third among human "
            "Codeforces competitors, achieves a perfect formal math proof score, "
            "and processes one million tokens in a single context window. "
            "All model weights are available on HuggingFace. "
            "If you found this breakdown valuable, subscribe for more deep dives "
            "into the models shaping the future of AI."
        ),
        voice=VOICE, rate=RATE,
    ):
        title = Text("A New Era of Long-Context AI", position=(CX, 220),
                     font_size=86, font_name=FONT,
                     stroke_style=StrokeStyle(color=BLUE, width=4))
        sketch(scene, title, 0.0, 3.0)

        results_box = panel(200, 310, 1520, 590, GREEN, PASTEL_GREEN, 2)
        sketch(scene, results_box, 2.5, 2.0)

        kpis = [
            (GREEN, "mHC: Stable 61-layer training via Birkhoff polytope constraint"),
            (BLUE,  "CSA: m=4 compression + Top-K=1024 sparse attention"),
            (BLUE,  "HCA: m'=128 ultra-compression + full dense attention"),
            (AMBER, "27% inference FLOPs  &  10% KV cache vs DeepSeek-V3.2"),
            (PURPLE,"Muon optimizer: Newton-Schulz orthogonalization (8+2 iters)"),
            (CORAL, "Anticipatory Routing + SwiGLU Clamping → zero loss spikes"),
            (PINK,  "OPD: 10+ expert teachers → single unified student model"),
            (GREEN, "Codeforces Rating 3206  ·  Rank #23 among all humans"),
        ]

        t = 4.0
        row_y = 352
        for col, text in kpis:
            sketch(scene, label(text, CX, row_y, col, 28, 2), t, 0.7)
            t += 0.7
            row_y += 68

        cta = label("Weights: huggingface.co/deepseek-ai/deepseek-v4", CX, 928, DARK_GRAY, 28, 1)
        sketch(scene, cta, t, 1.0)


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    print("=" * 68)
    print("  DeepSeek-V4 Technical Deep Dive  |  Target: ~15 minutes")
    print("=" * 68)

    scene = Scene(width=W, height=H, fps=FPS, background_color=WHITE)
    tts   = EdgeTTSProvider()

    builders = [
        ("Title & Hook",               scene_title),
        ("The Context Bottleneck",      scene_context_problem),
        ("Architecture Overview",       scene_architecture_overview),
        ("mHC Innovation",              scene_mhc),
        ("Compressed Sparse Attention", scene_csa),
        ("Heavily Compressed Attention",scene_hca),
        ("Muon Optimizer",              scene_muon),
        ("Training Stability",          scene_stability),
        ("Post-Training & OPD",         scene_post_training),
        ("Benchmark Results",           scene_benchmarks),
        ("Conclusion",                  scene_conclusion),
    ]

    for i, (name, fn) in enumerate(builders, 1):
        print(f"  [{i:02d}/{len(builders)}] Building: {name} ...")
        fn(scene, tts)

    total = scene.get_total_duration()
    print(f"\n  Total Duration : {total:.1f}s  ({total/60:.1f} min)")
    print("  Target         : ~900s  (15 min)")

    out_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "deepseek_v4_15min.mp4")

    print(f"\n  Rendering to: {out_path}")
    scene.render(out_path)
    print("  Done! ✓")


if __name__ == "__main__":
    main()