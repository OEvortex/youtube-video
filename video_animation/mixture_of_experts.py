import asyncio
import edge_tts
from handanim.core import Scene, FillStyle, StrokeStyle, SketchStyle
from handanim.core.scene import tts_speech
from handanim.animations import SketchAnimation, FadeOutAnimation
from handanim.primitives import (
    Text,
    Rectangle,
    Circle,
    Arrow,
    RoundedRectangle,
    FlowchartProcess,
    FlowchartDecision,
    FlowchartTerminator,
)


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
# COLOR PALETTE  (clean, YouTube-friendly)
# ─────────────────────────────────────────────
BLACK = (0.05, 0.05, 0.05)
WHITE = (0.98, 0.98, 0.98)
GRAY = (0.55, 0.55, 0.55)
DARK_GRAY = (0.25, 0.25, 0.25)
LIGHT_GRAY = (0.82, 0.82, 0.82)

BLUE = (0.10, 0.35, 0.85)
DARK_BLUE = (0.05, 0.20, 0.60)
SKY_BLUE = (0.40, 0.70, 1.00)
CYAN = (0.00, 0.75, 0.90)

GREEN = (0.10, 0.72, 0.40)
DARK_GREEN = (0.05, 0.50, 0.25)
MINT = (0.60, 0.95, 0.75)

RED = (0.88, 0.15, 0.20)
CORAL = (1.00, 0.45, 0.40)

ORANGE = (0.95, 0.55, 0.10)
AMBER = (1.00, 0.75, 0.20)

PURPLE = (0.55, 0.20, 0.80)
VIOLET = (0.70, 0.45, 1.00)

PINK = (0.92, 0.30, 0.65)
TEAL = (0.10, 0.65, 0.65)
INDIGO = (0.30, 0.25, 0.78)

# Pastel fills
PASTEL_BLUE = (0.80, 0.88, 1.00)
PASTEL_GREEN = (0.78, 0.96, 0.85)
PASTEL_RED = (1.00, 0.82, 0.82)
PASTEL_ORANGE = (1.00, 0.91, 0.76)
PASTEL_PURPLE = (0.91, 0.82, 1.00)
PASTEL_CYAN = (0.80, 0.96, 1.00)
PASTEL_MINT = (0.85, 1.00, 0.90)
PASTEL_AMBER = (1.00, 0.97, 0.82)

FONT_NAME = "cabin_sketch"
FPS = 24


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fade_all(scene, t, dur, *drawables):
    for d in drawables:
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + t, duration=dur), drawable=d)


def sketch_seq(scene, items, start_gap=1.5, step=0.4, draw_dur=0.6):
    """Sequentially sketch a list of drawables. Returns nothing."""
    t = start_gap
    for item in items:
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t, duration=draw_dur), drawable=item
        )
        t += step
    return t


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    output_path = "output/mixture_of_experts_v2.mp4"

    scene = Scene(
        width=1920,
        height=1080,
        fps=FPS,
        background_color=WHITE,
    )

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 1 ─ CINEMATIC TITLE  (~55 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "What if an AI model could have a trillion parameters, yet think as fast as one with only 37 billion? "
            "That's not science fiction — that's Mixture of Experts, the architecture quietly powering almost every "
            "frontier AI model you use today, from DeepSeek to Gemini to GPT-4. "
            "In this video we will go deep — the history, the math, the full architecture, every component, "
            "and how the field has evolved all the way through 2026. Let's go."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        # Big gradient-style title
        title_shadow = Text(
            text="Mixture of Experts",
            position=(964, 404),
            font_size=108,
            stroke_style=StrokeStyle(color=LIGHT_GRAY, width=6),
            font_name=FONT_NAME,
        )
        title = Text(
            text="Mixture of Experts",
            position=(960, 400),
            font_size=108,
            stroke_style=StrokeStyle(color=BLUE, width=5),
            font_name=FONT_NAME,
        )
        subtitle = Text(
            text="The Architecture Behind Every Frontier AI Model",
            position=(960, 530),
            font_size=46,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        tag = Text(
            text="History · Architecture · Math · FFN · Router · 2026 State-of-the-Art",
            position=(960, 630),
            font_size=30,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        credit = Text(
            text="A 15-Minute Deep Dive",
            position=(960, 710),
            font_size=28,
            stroke_style=StrokeStyle(color=GRAY, width=1),
            font_name=FONT_NAME,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 0.0, duration=3.0),
            drawable=title_shadow,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 0.2, duration=3.0), drawable=title
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=2.0), drawable=subtitle
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 4.0, duration=2.0), drawable=tag
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1.5), drawable=credit
        )

        fade_all(scene, 11, 1.5, title_shadow, title, subtitle, tag, credit)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 2 ─ THE "AHA" ANALOGY  (~55 s)
    # "Think of a hospital …"
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Let's start with an analogy. Imagine a hospital. When you walk in with a broken leg, "
            "the hospital doesn't make every doctor examine you. It routes you to the orthopedic surgeon. "
            "The cardiologist, the neurologist, the dermatologist — they stay idle. "
            "That's exactly how Mixture of Experts works inside a neural network. "
            "The model contains many expert sub-networks. For each token the model processes, "
            "a router decides which small set of experts to activate. "
            "The rest stay dormant. You get the knowledge of a massive model, "
            "at the compute cost of a much smaller one."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="The Core Intuition",
            position=(960, 110),
            font_size=68,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # Hospital box
        hosp_box = Rectangle(
            top_left=(80, 180),
            width=860,
            height=820,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.15),
            sketch_style=SketchStyle(roughness=2),
        )
        hosp_label = Text(
            text="Hospital  (= AI Model)",
            position=(510, 230),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1.2), drawable=hosp_box
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 2.2, duration=0.8),
            drawable=hosp_label,
        )

        # Doctors (experts inside hospital)
        doctors = [
            ("Orthopedic", 200, 370, GREEN, PASTEL_GREEN, True),
            ("Cardiologist", 500, 370, GRAY, LIGHT_GRAY, False),
            ("Neurologist", 200, 570, GRAY, LIGHT_GRAY, False),
            ("Dermatologist", 500, 570, GRAY, LIGHT_GRAY, False),
            ("Radiologist", 200, 770, GRAY, LIGHT_GRAY, False),
            ("Oncologist", 500, 770, GRAY, LIGHT_GRAY, False),
        ]
        doc_drawables = []
        for name, cx, cy, sc, fc, active in doctors:
            box = Rectangle(
                top_left=(cx - 130, cy - 55),
                width=260,
                height=110,
                stroke_style=StrokeStyle(color=sc, width=2 if not active else 3),
                fill_style=FillStyle(color=fc, opacity=0.4 if active else 0.2),
                sketch_style=SketchStyle(roughness=2),
            )
            label = Text(
                text=name + (" ✓" if active else ""),
                position=(cx, cy),
                font_size=26,
                stroke_style=StrokeStyle(color=sc, width=2),
                font_name=FONT_NAME,
            )
            doc_drawables.extend([box, label])

        t = 2.8
        for d in doc_drawables:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.5), drawable=d
            )
            t += 0.25

        # Patient arrow
        patient_arrow = Arrow(
            start_point=(80, 980),
            end_point=(200, 900),
            arrow_head_type="->",
            arrow_head_size=30,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=RED, width=3),
        )
        patient_label = Text(
            text="Patient (input token)",
            position=(160, 1010),
            font_size=26,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1),
            drawable=patient_arrow,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 6.0, duration=0.6),
            drawable=patient_label,
        )

        # Router box
        router_box = Rectangle(
            top_left=(80, 880),
            width=300,
            height=80,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.4),
            sketch_style=SketchStyle(roughness=2),
        )
        router_lbl = Text(
            text="Router → Expert 1",
            position=(230, 920),
            font_size=22,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 6.5, duration=1), drawable=router_box
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 7.0, duration=0.6),
            drawable=router_lbl,
        )

        # RIGHT side ─ MoE summary box
        summary_box = Rectangle(
            top_left=(980, 180),
            width=900,
            height=820,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.12),
            sketch_style=SketchStyle(roughness=2),
        )
        summary_lbl = Text(
            text="MoE Key Properties",
            position=(1430, 230),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 7.5, duration=1),
            drawable=summary_box,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 8.0, duration=0.6),
            drawable=summary_lbl,
        )

        props = [
            ("Sparse Activation", "Only top-k experts fire per token", BLUE),
            ("Massive Capacity", "Trillions of params, small compute", GREEN),
            ("Specialization", "Each expert learns unique patterns", ORANGE),
            ("Speed", "Fast as a small model at inference", PURPLE),
            ("Efficiency", "1/10th cost vs. equivalent dense model", TEAL),
        ]
        ty = 330
        t_props = 8.5
        for title_p, desc_p, col in props:
            pt = Text(
                text=f"→ {title_p}",
                position=(1430, ty),
                font_size=32,
                stroke_style=StrokeStyle(color=col, width=2),
                font_name=FONT_NAME,
            )
            pd = Text(
                text=desc_p,
                position=(1430, ty + 45),
                font_size=22,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
                font_name=FONT_NAME,
            )
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t_props, duration=0.7),
                drawable=pt,
            )
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t_props + 0.4, duration=0.6),
                drawable=pd,
            )
            doc_drawables.extend([pt, pd])
            ty += 120
            t_props += 1.0

        all_s2 = [
            heading,
            hosp_box,
            hosp_label,
            patient_arrow,
            patient_label,
            router_box,
            router_lbl,
            summary_box,
            summary_lbl,
        ] + doc_drawables
        fade_all(scene, 12, 1.5, *all_s2)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 4 ─ DENSE vs SPARSE — THE SCALING PROBLEM  (~55 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Before going into the architecture, we must understand why we need MoE in the first place. "
            "A traditional dense model activates every single parameter for every single token. "
            "Want to double model quality? You roughly double the compute cost. "
            "That's O-of-N scaling — brutal. "
            "By 2020, state-of-the-art models needed hundreds of millions of dollars to train. "
            "In PaLM 540B, an enormous dense model, ninety percent of parameters live in feed-forward layers, "
            "and every one of them fires for every token. Wasteful. "
            "MoE breaks this. With sparse activation, you keep all the parameters in memory, "
            "but you only compute on a small subset — typically two to eight experts out of dozens or hundreds. "
            "The result? Train a trillion-parameter model for the compute cost of a 37-billion one. "
            "That's the fundamental promise, and it delivers."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="The Scaling Problem — Dense vs Sparse",
            position=(960, 80),
            font_size=58,
            stroke_style=StrokeStyle(color=RED, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # DENSE side
        dense_border = Rectangle(
            top_left=(60, 150),
            width=860,
            height=860,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.10),
            sketch_style=SketchStyle(roughness=2),
        )
        dense_title = Text(
            text="Dense Model",
            position=(490, 200),
            font_size=42,
            stroke_style=StrokeStyle(color=GRAY, width=3),
            font_name=FONT_NAME,
        )

        # Grid of small cells representing all params — all filled red
        dense_cells = []
        for row in range(6):
            for col in range(8):
                cx = 120 + col * 95
                cy = 280 + row * 110
                cell = Rectangle(
                    top_left=(cx - 36, cy - 36),
                    width=72,
                    height=72,
                    stroke_style=StrokeStyle(color=RED, width=1),
                    fill_style=FillStyle(color=PASTEL_RED, opacity=0.6),
                    sketch_style=SketchStyle(roughness=1),
                )
                dense_cells.append(cell)

        dense_active = Text(
            text="ALL 48 parameters active",
            position=(490, 960),
            font_size=28,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        dense_cost = Text(
            text="Compute ∝ O(N)  — scales badly",
            position=(490, 1010),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )

        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1.2),
            drawable=dense_border,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 2.0, duration=0.8),
            drawable=dense_title,
        )
        t = 2.5
        for cell in dense_cells:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.3), drawable=cell
            )
            t += 0.08
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t + 0.2, duration=0.8),
            drawable=dense_active,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t + 0.5, duration=0.8),
            drawable=dense_cost,
        )

        # SPARSE side
        moe_border = Rectangle(
            top_left=(1000, 150),
            width=880,
            height=860,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.10),
            sketch_style=SketchStyle(roughness=2),
        )
        moe_title = Text(
            text="MoE Sparse Model",
            position=(1440, 200),
            font_size=42,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            font_name=FONT_NAME,
        )

        moe_cells = []
        active_indices = {0, 1, 8, 9}  # top-left 2x2 = "active experts"
        for row in range(6):
            for col in range(8):
                idx = row * 8 + col
                cx = 1060 + col * 95
                cy = 280 + row * 110
                is_active = idx in active_indices
                cell = Rectangle(
                    top_left=(cx - 36, cy - 36),
                    width=72,
                    height=72,
                    stroke_style=StrokeStyle(
                        color=GREEN if is_active else LIGHT_GRAY, width=1 if not is_active else 2
                    ),
                    fill_style=FillStyle(
                        color=PASTEL_GREEN if is_active else LIGHT_GRAY,
                        opacity=0.75 if is_active else 0.2,
                    ),
                    sketch_style=SketchStyle(roughness=1),
                )
                moe_cells.append(cell)

        moe_active = Text(
            text="Only 4 of 48 experts active (top-k=2)",
            position=(1440, 960),
            font_size=28,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        moe_cost = Text(
            text="Compute ∝ O(k/N)  — scales beautifully",
            position=(1440, 1010),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )

        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t + 0.8, duration=1.2),
            drawable=moe_border,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t + 1.3, duration=0.8),
            drawable=moe_title,
        )
        t2 = t + 1.8
        for cell in moe_cells:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t2, duration=0.3), drawable=cell
            )
            t2 += 0.08
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t2 + 0.2, duration=0.8),
            drawable=moe_active,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + t2 + 0.5, duration=0.8),
            drawable=moe_cost,
        )

        all_s4 = (
            [
                heading,
                dense_border,
                dense_title,
                dense_active,
                dense_cost,
                moe_border,
                moe_title,
                moe_active,
                moe_cost,
            ]
            + dense_cells
            + moe_cells
        )
        fade_all(scene, 14, 1.5, *all_s4)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 5 ─ TRANSFORMER BLOCK OVERVIEW  (~60 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Now let's see exactly where MoE fits inside a transformer. "
            "A standard transformer block has two sub-layers. "
            "First: Multi-Head Self-Attention, which lets every token attend to every other token. "
            "Second: a Feed-Forward Network — two linear layers with a non-linearity in between — "
            "applied independently to each token position. "
            "In a dense model this FFN is always the same for every token. "
            "In a MoE transformer, we replace that single FFN with a bank of N expert FFNs, "
            "plus a router that chooses which experts handle each token. "
            "Attention stays dense — it's still computed the same way. "
            "Only the FFN layer becomes sparse. "
            "This is important: the attention mechanism is untouched. "
            "Only the feed-forward layers gain the mixture-of-experts structure."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Where MoE Lives Inside a Transformer",
            position=(960, 75),
            font_size=58,
            stroke_style=StrokeStyle(color=INDIGO, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # ── Dense Transformer (left) ──────────────────────────────────
        def draw_transformer_column(
            x_center, title_text, title_color, ffn_label, ffn_color, ffn_fill, t_start
        ):
            col_title = Text(
                text=title_text,
                position=(x_center, 160),
                font_size=36,
                stroke_style=StrokeStyle(color=title_color, width=2),
                font_name=FONT_NAME,
            )

            # Input
            inp = Rectangle(
                top_left=(x_center - 170, 220),
                width=340,
                height=65,
                stroke_style=StrokeStyle(color=CYAN, width=2),
                fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.4),
                sketch_style=SketchStyle(roughness=2),
            )
            inp_t = Text(
                text="Input Embeddings",
                position=(x_center, 253),
                font_size=22,
                stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
                font_name=FONT_NAME,
            )

            arr_i = Arrow(
                start_point=(x_center, 285),
                end_point=(x_center, 320),
                arrow_head_type="->",
                arrow_head_size=14,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            )

            # Add & Norm
            anorm1 = Rectangle(
                top_left=(x_center - 170, 320),
                width=340,
                height=55,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.3),
                sketch_style=SketchStyle(roughness=1),
            )
            anorm1_t = Text(
                text="Add & LayerNorm",
                position=(x_center, 348),
                font_size=20,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                font_name=FONT_NAME,
            )

            # Attention
            arr_a = Arrow(
                start_point=(x_center, 375),
                end_point=(x_center, 410),
                arrow_head_type="->",
                arrow_head_size=14,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            )
            attn = Rectangle(
                top_left=(x_center - 170, 410),
                width=340,
                height=100,
                stroke_style=StrokeStyle(color=BLUE, width=2),
                fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.45),
                sketch_style=SketchStyle(roughness=2),
            )
            attn_t = Text(
                text="Multi-Head Attention",
                position=(x_center, 445),
                font_size=22,
                stroke_style=StrokeStyle(color=BLUE, width=2),
                font_name=FONT_NAME,
            )
            attn_t2 = Text(
                text="(Dense — unchanged)",
                position=(x_center, 470),
                font_size=17,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                font_name=FONT_NAME,
            )

            # Add & Norm 2
            arr_a2 = Arrow(
                start_point=(x_center, 510),
                end_point=(x_center, 545),
                arrow_head_type="->",
                arrow_head_size=14,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            )
            anorm2 = Rectangle(
                top_left=(x_center - 170, 545),
                width=340,
                height=55,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.3),
                sketch_style=SketchStyle(roughness=1),
            )
            anorm2_t = Text(
                text="Add & LayerNorm",
                position=(x_center, 573),
                font_size=20,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                font_name=FONT_NAME,
            )

            # FFN / MoE Layer
            arr_f = Arrow(
                start_point=(x_center, 600),
                end_point=(x_center, 635),
                arrow_head_type="->",
                arrow_head_size=14,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            )
            ffn = Rectangle(
                top_left=(x_center - 170, 635),
                width=340,
                height=120,
                stroke_style=StrokeStyle(color=ffn_color, width=3),
                fill_style=FillStyle(color=ffn_fill, opacity=0.5),
                sketch_style=SketchStyle(roughness=2),
            )
            ffn_t = Text(
                text=ffn_label,
                position=(x_center, 695),
                font_size=22,
                stroke_style=StrokeStyle(color=ffn_color, width=2),
                font_name=FONT_NAME,
            )

            # Add & Norm 3
            arr_f2 = Arrow(
                start_point=(x_center, 755),
                end_point=(x_center, 790),
                arrow_head_type="->",
                arrow_head_size=14,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            )
            anorm3 = Rectangle(
                top_left=(x_center - 170, 790),
                width=340,
                height=55,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.3),
                sketch_style=SketchStyle(roughness=1),
            )
            anorm3_t = Text(
                text="Add & LayerNorm",
                position=(x_center, 818),
                font_size=20,
                stroke_style=StrokeStyle(color=GRAY, width=1),
                font_name=FONT_NAME,
            )

            # Output
            arr_o = Arrow(
                start_point=(x_center, 845),
                end_point=(x_center, 880),
                arrow_head_type="->",
                arrow_head_size=14,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            )
            out = Rectangle(
                top_left=(x_center - 170, 880),
                width=340,
                height=65,
                stroke_style=StrokeStyle(color=CYAN, width=2),
                fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.4),
                sketch_style=SketchStyle(roughness=2),
            )
            out_t = Text(
                text="Output",
                position=(x_center, 913),
                font_size=22,
                stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
                font_name=FONT_NAME,
            )

            all_d = [
                col_title,
                inp,
                inp_t,
                arr_i,
                anorm1,
                anorm1_t,
                arr_a,
                attn,
                attn_t,
                attn_t2,
                arr_a2,
                anorm2,
                anorm2_t,
                arr_f,
                ffn,
                ffn_t,
                arr_f2,
                anorm3,
                anorm3_t,
                arr_o,
                out,
                out_t,
            ]
            t = t_start
            for d in all_d:
                scene.add(
                    SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.5), drawable=d
                )
                t += 0.25
            return all_d

        dense_col = draw_transformer_column(
            480, "Standard Transformer Block", GRAY, "Single Dense FFN", GRAY, LIGHT_GRAY, 1.5
        )
        moe_col = draw_transformer_column(
            1440,
            "MoE Transformer Block",
            GREEN,
            "MoE Layer (Sparse FFN × N)",
            GREEN,
            PASTEL_GREEN,
            3.5,
        )

        # Big arrow between columns
        vs_arrow = Arrow(
            start_point=(710, 695),
            end_point=(1170, 695),
            arrow_head_type="->",
            arrow_head_size=30,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=ORANGE, width=4),
        )
        vs_text = Text(
            text="Replace dense FFN →",
            position=(940, 660),
            font_size=26,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 7.5, duration=1.2), drawable=vs_arrow
        )
        scene.add(
            SketchAnimation(start_time=scene.timeline_cursor + 8.0, duration=0.8), drawable=vs_text
        )

        all_s5 = [heading, vs_arrow, vs_text] + dense_col + moe_col
        fade_all(scene, 14, 1.5, *all_s5)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 6 ─ FEED-FORWARD NETWORK ANATOMY  (~60 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Now let's zoom into the expert itself. Each expert in a MoE layer is a Feed-Forward Network. "
            "Let's understand what that means precisely. "
            "The FFN takes an input vector x — the token representation — of dimension d-model. "
            "It first projects UP into a higher-dimensional hidden space of size d-ff, "
            "typically four times d-model. "
            "This projection is a learned weight matrix W1, plus a bias b1, followed by a non-linear activation function. "
            "Modern transformers usually use SwiGLU or GELU — both smoother than the old ReLU. "
            "Then it projects back DOWN to d-model dimension with weight matrix W2 and bias b2. "
            "That's it. Two linear projections with a non-linearity between them. "
            "In GPT-2 for example, d-model is 768 and d-ff is 3072 — a 4x expansion. "
            "In Mixtral 8x7B, each expert FFN has d-model 4096 and d-ff 14336. "
            "The genius of MoE: instead of one big FFN, you have N smaller FFNs, "
            "each trained to specialize in different kinds of knowledge."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Inside the Expert: Feed-Forward Network Anatomy",
            position=(960, 75),
            font_size=52,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # Vertical FFN diagram (centered)
        # Input layer
        inp_box = Rectangle(
            top_left=(660, 160),
            width=600,
            height=80,
            stroke_style=StrokeStyle(color=CYAN, width=2),
            fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        inp_txt = Text(
            text="x  (token vector,  d_model = 4096)",
            position=(960, 200),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
            font_name=FONT_NAME,
        )

        arr1 = Arrow(
            start_point=(960, 240),
            end_point=(960, 290),
            arrow_head_type="->",
            arrow_head_size=18,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )

        # W1 projection (UP)
        w1_box = Rectangle(
            top_left=(560, 290),
            width=800,
            height=90,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        w1_txt = Text(
            text="Linear UP:  h = W₁·x + b₁   (d_ff = 14 336)",
            position=(960, 335),
            font_size=26,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )

        arr2 = Arrow(
            start_point=(960, 380),
            end_point=(960, 430),
            arrow_head_type="->",
            arrow_head_size=18,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )

        # Activation
        act_box = Rectangle(
            top_left=(660, 430),
            width=600,
            height=80,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        act_txt = Text(
            text="Activation:  a = SwiGLU(h)  or  GELU(h)",
            position=(960, 470),
            font_size=26,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )

        arr3 = Arrow(
            start_point=(960, 510),
            end_point=(960, 560),
            arrow_head_type="->",
            arrow_head_size=18,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )

        # W2 projection (DOWN)
        w2_box = Rectangle(
            top_left=(560, 560),
            width=800,
            height=90,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        w2_txt = Text(
            text="Linear DOWN:  y = W₂·a + b₂   (d_model = 4096)",
            position=(960, 605),
            font_size=26,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )

        arr4 = Arrow(
            start_point=(960, 650),
            end_point=(960, 700),
            arrow_head_type="->",
            arrow_head_size=18,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )

        # Output
        out_box = Rectangle(
            top_left=(660, 700),
            width=600,
            height=80,
            stroke_style=StrokeStyle(color=CYAN, width=2),
            fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        out_txt = Text(
            text="y  (output vector,  d_model = 4096)",
            position=(960, 740),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
            font_name=FONT_NAME,
        )

        # Right side notes
        note1 = Text(
            text="4× expansion",
            position=(1530, 335),
            font_size=22,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        note2 = Text(
            text="Non-linearity",
            position=(1530, 470),
            font_size=22,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )
        note3 = Text(
            text="Back to d_model",
            position=(1530, 605),
            font_size=22,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )

        # Bottom annotation
        formula = Text(
            text="FFN(x) = W₂ · SwiGLU(W₁·x + b₁) + b₂",
            position=(960, 840),
            font_size=34,
            stroke_style=StrokeStyle(color=INDIGO, width=2),
            font_name=FONT_NAME,
        )
        moe_note = Text(
            text="Each Expert = One FFN  |  MoE has N independent FFNs (typically 8–64)",
            position=(960, 920),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )

        items_s6 = [
            inp_box,
            inp_txt,
            arr1,
            w1_box,
            w1_txt,
            arr2,
            act_box,
            act_txt,
            arr3,
            w2_box,
            w2_txt,
            arr4,
            out_box,
            out_txt,
            note1,
            note2,
            note3,
            formula,
            moe_note,
        ]
        t = 1.5
        for it in items_s6:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.7), drawable=it
            )
            t += 0.45

        fade_all(scene, 15, 1.5, heading, *items_s6)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 7 ─ THE ROUTER / GATING NETWORK  (~70 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "The router — also called the gating network — is the brain of the MoE system. "
            "It decides, for every token, which experts to activate. "
            "Let's go step by step through how it works. "
            "Step one: the input token vector x is multiplied by a learned weight matrix W_g. "
            "This produces N raw scores, one for each expert. "
            "Step two: a Softmax is applied to get normalized probabilities across all experts. "
            "Step three: we pick the top-k highest probabilities. Typically k equals 1 or 2. "
            "Step four: only those top-k experts process the token. "
            "Their outputs are multiplied by the softmax probability and summed together. "
            "Mathematically: the output equals the sum over selected experts i, "
            "of softmax score i times expert-i applied to x. "
            "The weight matrix W_g is small — it has N rows and d-model columns, where N is just the number of experts. "
            "So routing adds minimal overhead. "
            "One critical challenge: the router can collapse — repeatedly choosing the same experts. "
            "This creates hot experts and cold experts, destroying the specialization benefit. "
            "To fix this, MoE training adds an auxiliary load-balancing loss "
            "that penalizes unequal expert utilization. "
            "DeepSeek V3 took a different approach — bias-based routing — "
            "adding a small learnable bias to router scores so experts are used more evenly "
            "without needing an auxiliary loss term."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="The Router / Gating Network — Step by Step",
            position=(960, 75),
            font_size=52,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # INPUT BOX
        in_box = Rectangle(
            top_left=(660, 140),
            width=600,
            height=75,
            stroke_style=StrokeStyle(color=CYAN, width=2),
            fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.4),
            sketch_style=SketchStyle(roughness=2),
        )
        in_txt = Text(
            text="Token vector  x  ∈ ℝ^(d_model)",
            position=(960, 178),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
            font_name=FONT_NAME,
        )

        # STEP 1 — W_g multiplication
        arr_r1 = Arrow(
            start_point=(960, 215),
            end_point=(960, 265),
            arrow_head_type="->",
            arrow_head_size=16,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )
        step1_box = Rectangle(
            top_left=(560, 265),
            width=800,
            height=85,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.4),
            sketch_style=SketchStyle(roughness=2),
        )
        step1_txt = Text(
            text="Step 1:  logits = W_g · x     (W_g ∈ ℝ^(N × d_model))",
            position=(960, 307),
            font_size=26,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )

        # STEP 2 — Softmax
        arr_r2 = Arrow(
            start_point=(960, 350),
            end_point=(960, 400),
            arrow_head_type="->",
            arrow_head_size=16,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )
        step2_box = Rectangle(
            top_left=(560, 400),
            width=800,
            height=85,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.4),
            sketch_style=SketchStyle(roughness=2),
        )
        step2_txt = Text(
            text="Step 2:  scores = Softmax(logits)   → probabilities 0–1",
            position=(960, 442),
            font_size=26,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )

        # STEP 3 — Top-k selection
        arr_r3 = Arrow(
            start_point=(960, 485),
            end_point=(960, 535),
            arrow_head_type="->",
            arrow_head_size=16,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )
        step3_box = Rectangle(
            top_left=(560, 535),
            width=800,
            height=85,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            sketch_style=SketchStyle(roughness=2),
        )
        step3_txt = Text(
            text="Step 3:  Top-K  selection  (k=1 or k=2)",
            position=(960, 577),
            font_size=26,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )

        # STEP 4 — Weighted sum
        arr_r4 = Arrow(
            start_point=(960, 620),
            end_point=(960, 670),
            arrow_head_type="->",
            arrow_head_size=16,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )
        step4_box = Rectangle(
            top_left=(560, 670),
            width=800,
            height=85,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.4),
            sketch_style=SketchStyle(roughness=2),
        )
        step4_txt = Text(
            text="Step 4:  Output = Σᵢ score_i · FFNᵢ(x)   for top-k experts",
            position=(960, 712),
            font_size=26,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )

        # Expert bars showing selection visually
        expert_scores = [
            ("E1", 0.55, GREEN, True),
            ("E2", 0.28, GREEN, True),
            ("E3", 0.10, GRAY, False),
            ("E4", 0.04, GRAY, False),
            ("E5", 0.02, GRAY, False),
            ("E6", 0.01, GRAY, False),
        ]
        ex_drawables = []
        for i, (name, score, col, sel) in enumerate(expert_scores):
            bx = 1430 + i * 72
            bar_h = int(score * 220)
            bar_y_top = 850 - bar_h
            bar = Rectangle(
                top_left=(bx - 24, bar_y_top),
                width=48,
                height=bar_h,
                stroke_style=StrokeStyle(color=col, width=2),
                fill_style=FillStyle(color=PASTEL_GREEN if sel else LIGHT_GRAY, opacity=0.7),
                sketch_style=SketchStyle(roughness=1),
            )
            lbl = Text(
                text=name,
                position=(bx, 870),
                font_size=20,
                stroke_style=StrokeStyle(color=col, width=1),
                font_name=FONT_NAME,
            )
            sc_lbl = Text(
                text=f"{score:.2f}",
                position=(bx, bar_y_top - 20),
                font_size=17,
                stroke_style=StrokeStyle(color=col, width=1),
                font_name=FONT_NAME,
            )
            ex_drawables.extend([bar, lbl, sc_lbl])

        bar_heading = Text(
            text="Router scores (k=2 selected)",
            position=(1630, 810),
            font_size=22,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        ex_drawables.append(bar_heading)

        # Load balance annotation
        lb_box = Rectangle(
            top_left=(80, 780),
            width=480,
            height=220,
            stroke_style=StrokeStyle(color=RED, width=2),
            fill_style=FillStyle(color=PASTEL_RED, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        lb_title = Text(
            text="⚠ Routing Collapse",
            position=(320, 820),
            font_size=26,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        lb_d1 = Text(
            text="Router keeps choosing E1 & E2",
            position=(320, 860),
            font_size=20,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        lb_d2 = Text(
            text="Fix: Auxiliary load-balance loss",
            position=(320, 895),
            font_size=20,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        lb_d3 = Text(
            text="Or: Bias routing (DeepSeek V3)",
            position=(320, 930),
            font_size=20,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        lb_d4 = Text(
            text="Or: Expert Choice routing",
            position=(320, 965),
            font_size=20,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )

        items_s7 = [
            in_box,
            in_txt,
            arr_r1,
            step1_box,
            step1_txt,
            arr_r2,
            step2_box,
            step2_txt,
            arr_r3,
            step3_box,
            step3_txt,
            arr_r4,
            step4_box,
            step4_txt,
            lb_box,
            lb_title,
            lb_d1,
            lb_d2,
            lb_d3,
            lb_d4,
        ] + ex_drawables

        t = 1.5
        for it in items_s7:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.6), drawable=it
            )
            t += 0.45

        fade_all(scene, 16, 1.5, heading, *items_s7)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 8 ─ FULL MoE LAYER DETAILED DIAGRAM  (~70 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Let's now put everything together in one diagram showing the full MoE layer. "
            "A sequence of tokens enters — let's say 'The capital of France'. "
            "Each token is processed independently through the MoE layer. "
            "The token vector x goes into the router. "
            "The router computes scores for all N experts — say 8 experts in Mixtral, "
            "or 256 experts in DeepSeek V3. "
            "Top-k are selected — say expert 3 and expert 7. "
            "Only those two FFNs receive x and compute their output. "
            "The outputs are weighted by the softmax scores and added together. "
            "The remaining 6 experts — or 254 in the DeepSeek case — do zero computation. "
            "They just sit in memory, unused for this token. "
            "This is called sparse conditional computation. "
            "Different tokens might activate completely different experts. "
            "Interestingly, researchers have found that experts do develop genuine specialization. "
            "Some experts handle syntax and grammar. Others handle factual knowledge. "
            "Others activate on specific languages or domains like code or math. "
            "This emergent specialization is one of the most exciting properties of MoE."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Full MoE Layer — Detailed Diagram",
            position=(960, 65),
            font_size=54,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # Tokens column (left)
        tokens = ["The", "capital", "of", "France"]
        tok_drawables = []
        for i, tok in enumerate(tokens):
            tb = Rectangle(
                top_left=(50, 200 + i * 100),
                width=180,
                height=70,
                stroke_style=StrokeStyle(color=CYAN, width=2),
                fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.5),
                sketch_style=SketchStyle(roughness=1),
            )
            tl = Text(
                text=f'"{tok}"',
                position=(140, 235 + i * 100),
                font_size=24,
                stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
                font_name=FONT_NAME,
            )
            tok_drawables.extend([tb, tl])

        tok_lbl = Text(
            text="Input Tokens",
            position=(140, 150),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        tok_drawables.append(tok_lbl)

        # Arrow from tokens to router
        tok_arr = Arrow(
            start_point=(230, 375),
            end_point=(380, 375),
            arrow_head_type="->",
            arrow_head_size=20,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=3),
        )
        tok_drawables.append(tok_arr)

        # Router box (center-left)
        router_big = Rectangle(
            top_left=(380, 280),
            width=320,
            height=190,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        router_t1 = Text(
            text="Router",
            position=(540, 330),
            font_size=34,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            font_name=FONT_NAME,
        )
        router_t2 = Text(
            text="W_g · x",
            position=(540, 375),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        router_t3 = Text(
            text="Softmax → Top-k",
            position=(540, 415),
            font_size=22,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )

        # Experts (right side, 8 boxes in 2 columns)
        expert_data = [
            ("Expert 1\n(FFN)", 900, 180, GRAY, LIGHT_GRAY, False),
            ("Expert 2\n(FFN)", 1100, 180, GRAY, LIGHT_GRAY, False),
            ("Expert 3 ★\n(FFN)", 900, 330, GREEN, PASTEL_GREEN, True),
            ("Expert 4\n(FFN)", 1100, 330, GRAY, LIGHT_GRAY, False),
            ("Expert 5\n(FFN)", 900, 480, GRAY, LIGHT_GRAY, False),
            ("Expert 6\n(FFN)", 1100, 480, GRAY, LIGHT_GRAY, False),
            ("Expert 7 ★\n(FFN)", 900, 630, GREEN, PASTEL_GREEN, True),
            ("Expert 8\n(FFN)", 1100, 630, GRAY, LIGHT_GRAY, False),
        ]
        expert_boxes = []
        active_centers = []
        for name, ex, ey, ec, efc, eactive in expert_data:
            eb = Rectangle(
                top_left=(ex - 90, ey - 55),
                width=180,
                height=110,
                stroke_style=StrokeStyle(color=ec, width=3 if eactive else 1),
                fill_style=FillStyle(color=efc, opacity=0.6 if eactive else 0.2),
                sketch_style=SketchStyle(roughness=2),
            )
            el = Text(
                text=name,
                position=(ex, ey),
                font_size=20,
                stroke_style=StrokeStyle(color=ec, width=2),
                font_name=FONT_NAME,
            )
            expert_boxes.extend([eb, el])
            if eactive:
                active_centers.append((ex, ey))

        experts_lbl = Text(
            text="Expert Bank (8 FFNs)",
            position=(1000, 110),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        expert_boxes.append(experts_lbl)

        # Arrows from router to active experts
        for ax, ay in active_centers:
            ea = Arrow(
                start_point=(700, 375),
                end_point=(ax - 90, ay),
                arrow_head_type="->",
                arrow_head_size=16,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=GREEN, width=2),
            )
            expert_boxes.append(ea)

        # Weighted sum box
        wsum = Rectangle(
            top_left=(1340, 280),
            width=280,
            height=190,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.45),
            sketch_style=SketchStyle(roughness=2),
        )
        wsum_t1 = Text(
            text="Weighted",
            position=(1480, 330),
            font_size=28,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        wsum_t2 = Text(
            text="Sum",
            position=(1480, 365),
            font_size=28,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        wsum_t3 = Text(
            text="s₃·FFN₃(x)",
            position=(1480, 400),
            font_size=20,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        wsum_t4 = Text(
            text="+ s₇·FFN₇(x)",
            position=(1480, 425),
            font_size=20,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )

        for ax, ay in active_centers:
            wa = Arrow(
                start_point=(ax + 90, ay),
                end_point=(1340, 375),
                arrow_head_type="->",
                arrow_head_size=16,
                arrow_head_angle=40,
                stroke_style=StrokeStyle(color=BLUE, width=2),
            )
            expert_boxes.append(wa)

        # Output arrow
        out_arr = Arrow(
            start_point=(1620, 375),
            end_point=(1760, 375),
            arrow_head_type="->",
            arrow_head_size=20,
            arrow_head_angle=40,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=3),
        )
        out_box = Rectangle(
            top_left=(1760, 310),
            width=130,
            height=130,
            stroke_style=StrokeStyle(color=CYAN, width=2),
            fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        out_lbl = Text(
            text="Output",
            position=(1825, 375),
            font_size=22,
            stroke_style=StrokeStyle(color=DARK_BLUE, width=2),
            font_name=FONT_NAME,
        )

        # Specialization note
        spec_box = Rectangle(
            top_left=(80, 810),
            width=1800,
            height=220,
            stroke_style=StrokeStyle(color=TEAL, width=2),
            fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.15),
            sketch_style=SketchStyle(roughness=2),
        )
        spec_t1 = Text(
            text="Emergent Expert Specialization",
            position=(960, 845),
            font_size=30,
            stroke_style=StrokeStyle(color=TEAL, width=2),
            font_name=FONT_NAME,
        )
        spec_items = [
            ("Syntax/Grammar experts", 300, 900),
            ("Factual knowledge experts", 600, 900),
            ("Code/Math experts", 900, 900),
            ("Language-specific experts", 1200, 900),
            ("Reasoning experts", 1500, 900),
        ]
        spec_drawables = [spec_box, spec_t1]
        for st, sx, sy in spec_items:
            s_lbl = Text(
                text=f"→ {st}",
                position=(sx, sy),
                font_size=20,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
                font_name=FONT_NAME,
            )
            spec_drawables.append(s_lbl)

        all_s8 = (
            [
                heading,
                tok_lbl,
                tok_arr,
                router_big,
                router_t1,
                router_t2,
                router_t3,
                experts_lbl,
                wsum,
                wsum_t1,
                wsum_t2,
                wsum_t3,
                wsum_t4,
                out_arr,
                out_box,
                out_lbl,
            ]
            + tok_drawables
            + expert_boxes
            + spec_drawables
        )

        t = 1.5
        for it in all_s8:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.55), drawable=it
            )
            t += 0.35

        fade_all(scene, 17, 1.5, *all_s8)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 9 ─ LOAD BALANCING  (~40 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "One key challenge in MoE is load balancing. "
            "If the router isn't trained carefully, it might send most tokens to just a few experts, "
            "leaving others almost completely idle. This is called routing collapse. "
            "The solution: add a special loss term during training that rewards even distribution "
            "of tokens across all experts. This ensures every expert gets used and learns something useful."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Load Balancing — Avoiding Routing Collapse",
            position=(960, 80),
            font_size=52,
            stroke_style=StrokeStyle(color=RED, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # UNBALANCED visual (left)
        unbal_lbl = Text(
            text="❌ Unbalanced (Bad)",
            position=(480, 180),
            font_size=36,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )

        unbal_experts = [
            ("E1", 160, 0.80, RED, PASTEL_RED),
            ("E2", 260, 0.72, RED, PASTEL_RED),
            ("E3", 360, 0.08, GRAY, LIGHT_GRAY),
            ("E4", 460, 0.05, GRAY, LIGHT_GRAY),
            ("E5", 560, 0.04, GRAY, LIGHT_GRAY),
            ("E6", 660, 0.03, GRAY, LIGHT_GRAY),
            ("E7", 760, 0.03, GRAY, LIGHT_GRAY),
            ("E8", 860, 0.02, GRAY, LIGHT_GRAY),
        ]
        unbal_drawables = [unbal_lbl]
        for name, bx, pct, col, fc in unbal_experts:
            bar_h = int(pct * 400)
            bar_y = 750 - bar_h
            bar = Rectangle(
                top_left=(bx - 38, bar_y),
                width=76,
                height=bar_h,
                stroke_style=StrokeStyle(color=col, width=2),
                fill_style=FillStyle(color=fc, opacity=0.7),
                sketch_style=SketchStyle(roughness=1),
            )
            bar_pct = Text(
                text=f"{int(pct * 100)}%",
                position=(bx, bar_y - 25),
                font_size=20,
                stroke_style=StrokeStyle(color=col, width=1),
                font_name=FONT_NAME,
            )
            bar_lbl = Text(
                text=name,
                position=(bx, 780),
                font_size=22,
                stroke_style=StrokeStyle(color=col, width=1),
                font_name=FONT_NAME,
            )
            unbal_drawables.extend([bar, bar_pct, bar_lbl])

        unbal_note = Text(
            text="Experts 1 & 2 do all the work\nOthers learn nothing",
            position=(510, 920),
            font_size=24,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        unbal_drawables.append(unbal_note)

        # BALANCED visual (right)
        bal_lbl = Text(
            text="✓ Balanced (Good)",
            position=(1440, 180),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )

        bal_experts = [
            ("E1", 1120, 0.125),
            ("E2", 1220, 0.125),
            ("E3", 1320, 0.125),
            ("E4", 1420, 0.125),
            ("E5", 1520, 0.125),
            ("E6", 1620, 0.125),
            ("E7", 1720, 0.125),
            ("E8", 1820, 0.125),
        ]
        bal_drawables = [bal_lbl]
        for name, bx, pct in bal_experts:
            bar_h = int(pct * 400)
            bar_y = 750 - bar_h
            bar = Rectangle(
                top_left=(bx - 38, bar_y),
                width=76,
                height=bar_h,
                stroke_style=StrokeStyle(color=GREEN, width=2),
                fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.7),
                sketch_style=SketchStyle(roughness=1),
            )
            bar_pct = Text(
                text="12.5%",
                position=(bx, bar_y - 25),
                font_size=18,
                stroke_style=StrokeStyle(color=GREEN, width=1),
                font_name=FONT_NAME,
            )
            bar_lbl = Text(
                text=name,
                position=(bx, 780),
                font_size=22,
                stroke_style=StrokeStyle(color=GREEN, width=1),
                font_name=FONT_NAME,
            )
            bal_drawables.extend([bar, bar_pct, bar_lbl])

        bal_note = Text(
            text="All experts share the work equally\nEveryone learns useful patterns",
            position=(1470, 920),
            font_size=24,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        bal_drawables.append(bal_note)

        all_s9 = [heading] + unbal_drawables + bal_drawables
        t = 1.5
        for it in all_s9:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.55), drawable=it
            )
            t += 0.32

        fade_all(scene, 12, 1.5, *all_s9)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 11 ─ MODERN MODELS  (~45 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Let's look at some real modern MoE models. "
            "Mixtral 8x7B was the first mainstream open-source MoE model. "
            "It has 47 billion total parameters but only 13 billion active per token, "
            "using 8 experts and activating 2 at a time. "
            "DeepSeek V3 is the most impressive example: 671 billion total parameters, "
            "but only 37 billion active per token. It uses 256 experts and activates 8 at once. "
            "It was trained for just 5.6 million dollars — a fraction of what GPT-4 cost. "
            "Today, nearly all frontier models like GPT-4, Gemini, and Claude are believed to use MoE."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Modern MoE Models",
            position=(960, 80),
            font_size=58,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # Simple cards for 3 key models
        models = [
            (
                "Mixtral 8x7B",
                "Dec 2023",
                "47B total / 13B active",
                "8 experts, k=2",
                "First mainstream open MoE",
                GREEN,
                150,
            ),
            (
                "DeepSeek V3",
                "Dec 2024",
                "671B total / 37B active",
                "256 experts, k=8",
                "Trained for $5.6M",
                CORAL,
                750,
            ),
            (
                "GPT-4 (rumored)",
                "2023",
                "~1.4T total / ~50B active",
                "Multiple experts",
                "Frontier model standard",
                PURPLE,
                1350,
            ),
        ]

        all_s11 = [heading]
        for name, year, params, experts, note, col, x in models:
            card = Rectangle(
                top_left=(x, 200),
                width=500,
                height=280,
                stroke_style=StrokeStyle(color=col, width=2),
                fill_style=FillStyle(color=(0.95, 0.95, 1.0), opacity=0.3),
                sketch_style=SketchStyle(roughness=2),
            )
            t_name = Text(
                text=name,
                position=(x + 250, 250),
                font_size=32,
                stroke_style=StrokeStyle(color=col, width=2),
                font_name=FONT_NAME,
            )
            t_year = Text(
                text=year,
                position=(x + 250, 300),
                font_size=22,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
                font_name=FONT_NAME,
            )
            t_params = Text(
                text=params,
                position=(x + 250, 350),
                font_size=24,
                stroke_style=StrokeStyle(color=BLUE, width=2),
                font_name=FONT_NAME,
            )
            t_experts = Text(
                text=experts,
                position=(x + 250, 400),
                font_size=22,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
                font_name=FONT_NAME,
            )
            t_note = Text(
                text=note,
                position=(x + 250, 450),
                font_size=24,
                stroke_style=StrokeStyle(color=GREEN, width=2),
                font_name=FONT_NAME,
            )
            all_s11.extend([card, t_name, t_year, t_params, t_experts, t_note])

        # Bottom summary
        summary = Text(
            text="2026: MoE is the standard for frontier AI models",
            position=(960, 600),
            font_size=32,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        all_s11.append(summary)

        t = 1.5
        for it in all_s11:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.6), drawable=it
            )
            t += 0.35

        fade_all(scene, 12, 1.5, *all_s11)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 14 ─ INFERENCE  (~35 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "Running MoE models at inference has one main challenge: "
            "you need all expert weights in memory, but only compute a few per token. "
            "The solution is quantization — using fewer bits per parameter. "
            "For example, Mixtral 8x7B in 4-bit quantization fits in about 24 gigabytes of VRAM, "
            "which runs on a single high-end consumer GPU. "
            "With the right setup, MoE gives you large-model intelligence at small-model speed."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Running MoE Models",
            position=(960, 100),
            font_size=58,
            stroke_style=StrokeStyle(color=INDIGO, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # Memory challenge box
        mem_box = Rectangle(
            top_left=(200, 200),
            width=700,
            height=200,
            stroke_style=StrokeStyle(color=RED, width=2),
            fill_style=FillStyle(color=PASTEL_RED, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        mem_t1 = Text(
            text="Memory Challenge",
            position=(550, 250),
            font_size=32,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        mem_t2 = Text(
            text="All experts in VRAM",
            position=(550, 310),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        mem_t3 = Text(
            text="But only compute a few per token",
            position=(550, 360),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )

        # Solution box
        sol_box = Rectangle(
            top_left=(1000, 200),
            width=700,
            height=200,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        sol_t1 = Text(
            text="Solution: Quantization",
            position=(1350, 250),
            font_size=32,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        sol_t2 = Text(
            text="4-bit or 8-bit weights",
            position=(1350, 310),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        sol_t3 = Text(
            text="Dramatically reduces memory",
            position=(1350, 360),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )

        # Example box
        ex_box = Rectangle(
            top_left=(400, 450),
            width=1100,
            height=180,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        ex_t1 = Text(
            text="Example: Mixtral 8x7B",
            position=(950, 500),
            font_size=32,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        ex_t2 = Text(
            text="47B total → 13B active per token",
            position=(950, 560),
            font_size=26,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        ex_t3 = Text(
            text="4-bit quantization = ~24 GB VRAM (fits on RTX 4090)",
            position=(950, 610),
            font_size=26,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )

        all_s14 = [
            heading,
            mem_box,
            mem_t1,
            mem_t2,
            mem_t3,
            sol_box,
            sol_t1,
            sol_t2,
            sol_t3,
            ex_box,
            ex_t1,
            ex_t2,
            ex_t3,
        ]

        t = 1.5
        for it in all_s14:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.6), drawable=it
            )
            t += 0.35

        fade_all(scene, 10, 1.5, *all_s14)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 15 ─ CONCLUSION  (~30 s)
    # ══════════════════════════════════════════════════════════════════════
    with scene.group(
        tts_provider=EdgeTTSProvider(),
        speech=(
            "To wrap up: Mixture of Experts is a fundamental idea in AI. "
            "Instead of activating all parameters for every input, "
            "MoE uses a router to send each token to only the most relevant experts. "
            "This gives you massive model capacity with efficient compute. "
            "From the hospital analogy to real models like Mixtral and DeepSeek V3, "
            "MoE has proven to be the standard for frontier AI models. "
            "It's not just an optimization — it's a different way of thinking about neural networks."
        ),
        voice="en-US-JennyNeural",
        rate="+6%",
    ):
        heading = Text(
            text="Conclusion",
            position=(960, 120),
            font_size=64,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=heading)

        # Key points
        points = [
            ("Sparse Activation", "Only a few experts active per token", GREEN, 200),
            ("Specialization", "Each expert learns unique patterns", ORANGE, 600),
            ("Efficiency", "Large capacity, small compute cost", PURPLE, 1000),
            ("Standard", "Used by nearly all frontier models", BLUE, 1400),
        ]

        all_s15 = [heading]
        for p_title, p_desc, col, px in points:
            p_box = Rectangle(
                top_left=(px, 250),
                width=380,
                height=180,
                stroke_style=StrokeStyle(color=col, width=2),
                fill_style=FillStyle(color=(0.95, 0.95, 1.0), opacity=0.3),
                sketch_style=SketchStyle(roughness=2),
            )
            p_t = Text(
                text=p_title,
                position=(px + 190, 300),
                font_size=28,
                stroke_style=StrokeStyle(color=col, width=2),
                font_name=FONT_NAME,
            )
            p_d = Text(
                text=p_desc,
                position=(px + 190, 360),
                font_size=22,
                stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
                font_name=FONT_NAME,
            )
            all_s15.extend([p_box, p_t, p_d])

        # Final summary
        final_box = Rectangle(
            top_left=(300, 500),
            width=1320,
            height=200,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.25),
            sketch_style=SketchStyle(roughness=2),
        )
        final_t1 = Text(
            text="MoE = Massive Capacity + Efficient Compute + Specialization",
            position=(960, 560),
            font_size=32,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        final_t2 = Text(
            text="The standard for frontier AI models",
            position=(960, 640),
            font_size=36,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        all_s15.extend([final_box, final_t1, final_t2])

        t = 1.5
        for it in all_s15:
            scene.add(
                SketchAnimation(start_time=scene.timeline_cursor + t, duration=0.6), drawable=it
            )
            t += 0.35

    # ══════════════════════════════════════════════════════════════════════
    # RENDER
    # ══════════════════════════════════════════════════════════════════════
    scene.render(output_path=output_path)


if __name__ == "__main__":
    main()
