"""
Mixture of Experts (MoE) — Complete YouTube Explainer
=====================================================
Beginner-to-advanced whiteboard animation.

Sections
--------
 0. Cold Open / Hook
 1. Title Card
 2. Intro — What is MoE & why care?
 3. Dense vs Sparse Primer — how traditional LLMs work
 4. The Core Idea — specialization analogy
 5. MoE Architecture — experts + router structure
 6. Routing Mechanism — Top-K gating explained
 7. Sparsity Explained — conditional computation
 8. Load Balancing Problem — expert imbalance
 9. Load Balancing Solutions — auxiliary loss, noise, capacity
10. Switch Transformer — simplified top-1 routing
11. Expert Choice Routing — advanced techniques
12. Training Challenges — fine-tuning issues
13. Inference Benefits — speed vs memory trade-off
14. Parameter Efficiency — total vs active parameters
15. Real-World Models — Mixtral, DeepSeek-V3, GPT-4, DBRX
16. Mathematical Formulation — MoE equations
17. Quantitative Comparison — dense vs MoE benchmarks
18. Trade-offs — when to use MoE vs dense
19. Summary Cheat-Sheet
20. Outro / Call-to-Action
"""

import asyncio
import os
import re
from pathlib import Path

try:
    import edge_tts
except ImportError as exc:
    raise SystemExit(
        "Install edge-tts first: pip install edge-tts"
    ) from exc

from handanim.animations import SketchAnimation, FadeInAnimation
from handanim.core import Scene, FillStyle, StrokeStyle, SketchStyle
from handanim.primitives import (
    Arrow, Circle, Curve, Eraser, FlowchartProcess,
    Line, Math, Table, Ellipse, Rectangle,
    RoundedRectangle, Text,
)
from handanim.stylings.color import (
    BLACK, BLUE, GREEN, ORANGE, PURPLE, RED, WHITE,
    GRAY, DARK_GRAY, LIGHT_GRAY,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_ORANGE,
    PASTEL_RED, PASTEL_PURPLE, PASTEL_YELLOW, PASTEL_GRAY,
)

# ── Canvas ────────────────────────────────────────────────────────────────────
WIDTH  = 1920
HEIGHT = 1088
FPS    = 24

# ── Voice ─────────────────────────────────────────────────────────────────────
VOICE        = "en-US-GuyNeural"
VOICE_RATE   = "+2%"
VOICE_VOLUME = 1.25
FONT_NAME    = "feasibly"

# ── Style constants ────────────────────────────────────────────────────────────
BG     = WHITE
SKETCH = SketchStyle(roughness=1.5, bowing=1.2, disable_font_mixture=True)
STK    = StrokeStyle(color=BLACK, width=2.0)
STK4   = StrokeStyle(color=BLACK, width=2.5)
STK6   = StrokeStyle(color=BLACK, width=3.0)

# ── Narration ─────────────────────────────────────────────────────────────────
NARRATION = """
<bookmark mark='cold_open'/>
What if I told you there's a way to have a model with 671 billion parameters \
that runs as fast as a 37 billion parameter model? \
That's not magic — that's Mixture of Experts, or MoE. \
And by the end of this video, you'll understand how the world's most powerful AI models \
use this technique to achieve massive scale without massive compute costs.

<bookmark mark='title'/>
Welcome. Today we are going to master Mixture of Experts.

<bookmark mark='intro'/>
Let me first tell you why you should care. \
GPT-4, one of the most capable AI systems ever built, is rumored to use MoE architecture. \
Mixtral 8x7B from Mistral AI became an instant sensation by using MoE to outperform \
much larger dense models. \
DeepSeek-V3 has 671 billion total parameters but only activates 37 billion per token — \
thanks to MoE. \
DBRX from Databricks set new records on open-source benchmarks using their own MoE design. \
When you see MoE in an architecture card, it means the engineers figured out how to \
scale model intelligence without scaling compute linearly.

<bookmark mark='dense_primer'/>
Before we dive into MoE, let's understand how traditional dense models work. \
In a standard transformer, every layer processes every token using the same parameters. \
Think of it like a generalist doctor — they see every patient and apply the same knowledge base. \
The feed-forward network, or FFN layer, is where most of the parameters live. \
For every token that passes through, the entire FFN activates — all parameters, all the time. \
This is called dense activation. \
If you want a smarter model, you make the FFN bigger — more parameters, more compute, every single token.

<bookmark mark='core_idea'/>
Here's the core insight behind MoE. \
Instead of one giant generalist, what if you had many specialists? \
Think of a hospital. You don't want a generalist for everything — \
you want a cardiologist for heart problems, a neurologist for brain issues, \
an orthopedist for bones. Each specialist is an expert in their domain. \
When a patient arrives, a receptionist routes them to the right specialist. \
MoE applies this exact idea to neural networks. \
Instead of one giant FFN that knows everything poorly, \
you have many smaller expert FFNs, each specializing in different types of tokens. \
A router network decides which expert should handle each token. \
The result: you can have many more total parameters, but only use a few per token.

<bookmark mark='architecture'/>
Let me walk you through the MoE architecture step by step. \
In a standard transformer layer, after attention, you have a dense FFN. \
In MoE, we replace this single FFN with a MoE layer consisting of two parts. \
First: the experts. These are typically multiple feed-forward networks — \
say 8 experts, or 32, or even 256 in large models. \
Each expert is a neural network that can process tokens independently. \
Second: the router, also called a gate network. \
The router looks at each token and decides which experts should process it. \
The router outputs weights for each expert — higher weights mean the expert is more relevant. \
The token is then sent to the top-k experts with the highest weights, \
where k is usually 1, 2, or a small number. \
The outputs from the selected experts are combined, typically by weighted sum, \
to produce the final layer output.

<bookmark mark='routing'/>
Let's dive deeper into how routing works. \
The routing process happens in three steps. \
Step one: the router computes a score for each expert. \
This is done with a learned linear projection followed by a softmax. \
The score represents how relevant each expert is for the current token. \
Step two: we select the top-k experts with the highest scores. \
This is where sparsity comes in — we only activate a few experts, not all of them. \
Step three: the token is sent to those selected experts, \
and their outputs are combined using the routing weights. \
In Mixtral 8x7B, there are 8 experts and k equals 2 — each token activates exactly 2 experts. \
In DeepSeek-V3, there are 256 experts and k equals 8 — each token activates 8 experts. \
The key insight: most experts are dormant for any given token, saving massive compute.

<bookmark mark='sparsity'/>
This selective activation is called sparsity or conditional computation. \
In dense models, every parameter activates for every input. \
In sparse MoE models, only a subset of parameters activate per input. \
This is the magic that makes MoE efficient. \
You can have a model with 10 times more parameters, \
but if only 10 percent of them activate per token, \
your compute cost stays roughly the same. \
It's like having a 100-person hospital but only needing 10 doctors for any given patient — \
the expertise is there when needed, but you're not paying for everyone to work on every case.

<bookmark mark='load_balancing_problem'/>
But there's a critical problem: load balancing. \
During training, the router learns which experts to use. \
Without any constraints, the router might converge to always sending tokens \
to the same few "popular" experts. \
This creates a vicious cycle: popular experts get more training data, \
so they become better, so the router sends them even more tokens. \
Meanwhile, other experts barely get used and fail to learn anything useful. \
This defeats the purpose of MoE — you're not actually using your diverse expert capacity. \
This is the load balancing problem, and it's one of the biggest challenges in training MoE models.

<bookmark mark='load_balancing_solutions'/>
Researchers have developed several solutions to load balancing. \
First: auxiliary loss. We add an extra term to the loss function that penalizes imbalance. \
The loss encourages uniform expert utilization — every expert should get roughly the same number of tokens. \
This is like giving the hospital receptionist a bonus for ensuring all doctors get equal patients. \
Second: noisy top-k gating. Before selecting top-k experts, we add random noise to the routing scores. \
This encourages exploration — the router occasionally tries less-used experts, \
helping them get training data and improve. \
Third: expert capacity. We set a hard limit on how many tokens each expert can process per batch. \
If an expert reaches capacity, extra tokens get routed to other experts or dropped entirely. \
This prevents any single expert from monopolizing tokens. \
All three techniques are often used together to ensure balanced expert utilization.

<bookmark mark='switch_transformer'/>
The Switch Transformer, introduced by Google in 2021, simplified MoE architecture significantly. \
Traditional MoE used top-k routing with k greater than 1, sending each token to multiple experts. \
Switch Transformer asked: what if we use top-1 routing instead? \
Each token goes to exactly one expert — the single best match. \
This simplifies the architecture dramatically — no need to combine multiple expert outputs. \
Surprisingly, top-1 routing works just as well as top-k, and sometimes better. \
The key insight is that with enough experts and proper load balancing, \
each token can find a truly specialized expert. \
Switch Transformer also introduced router z-loss, \
an additional regularization term that stabilizes training by preventing routing scores from becoming too extreme. \
This made training large MoE models much more stable and became the foundation for many modern MoE systems.

<bookmark mark='expert_choice'/>
More recent work introduced Expert Choice Routing, which flips the traditional paradigm. \
In standard routing, each token chooses its experts. \
In Expert Choice, each expert chooses which tokens it wants to process. \
Experts bid on tokens, and tokens are allocated to experts that bid highest for them. \
This ensures better load balancing because experts actively compete for tokens \
rather than passively waiting to be selected. \
Expert Choice can also handle variable numbers of experts per token — \
some tokens might need more expert attention than others. \
This approach achieved more than 2x training efficiency improvement over traditional MoE methods \
and is used in some of the most advanced systems today.

<bookmark mark='training_challenges'/>
MoE models come with unique training challenges beyond load balancing. \
First: fine-tuning instability. \
While MoE pretrains efficiently, fine-tuning can be problematic. \
The model may overfit to the fine-tuning data, especially if the fine-tuning dataset is small. \
Specialized experts that learned general patterns during pretraining \
might forget those patterns when fine-tuned on narrow tasks. \
Second: communication overhead. \
In distributed training, tokens need to be sent to the right experts, \
which might be on different GPUs. This all-to-all communication can become a bottleneck. \
Third: hyperparameter sensitivity. \
The number of experts, routing strategy, capacity factor, and loss weights \
all need careful tuning for stable training. \
Despite these challenges, the benefits of MoE make the effort worthwhile.

<bookmark mark='inference_benefits'/>
Let's talk about inference — actually using the model after it's trained. \
MoE models have a unique advantage: they can have massive parameter counts \
but still run fast at inference time. \
This is because only a subset of experts activate per token. \
Mixtral 8x7B has 46.7 billion total parameters, but only activates about 13 billion per token \
— it runs at the speed of a 13B dense model. \
DeepSeek-V3 has 671 billion total parameters but activates only 37 billion per token. \
The inference FLOPs scale with the number of active parameters, not total parameters. \
However, there's a catch: all parameters still need to be loaded in memory. \
Even if only 37 billion parameters activate, you need VRAM to hold all 671 billion. \
This means MoE models require more memory than dense models of the same inference speed. \
You trade memory for compute efficiency — a worthy trade in many scenarios.

<bookmark mark='parameter_efficiency'/>
Let's quantify this parameter efficiency. \
In a dense model, total parameters equals active parameters — everything activates all the time. \
In an MoE model, total parameters can be much larger than active parameters. \
The sparsity ratio is active parameters divided by total parameters. \
For Mixtral 8x7B: 8 experts of 7B each, but only 2 activate per token. \
The shared attention and embedding parameters are about 5B. \
So total is 8 times 7B plus 5B equals 61B, but active is about 13B — \
a sparsity ratio of roughly 21 percent. \
For DeepSeek-V3: 671B total, 37B active — sparsity ratio of about 5.5 percent. \
This incredible sparsity is what allows these models to be so capable \
while remaining computationally feasible. \
It's like having a massive encyclopedia but only needing to read a few pages per question.

<bookmark mark='real_world_models'/>
Let's survey the landscape of models using MoE. \
Mixtral 8x7B, released by Mistral AI in 2024, was a breakthrough open-source MoE model. \
It matched or exceeded the performance of much larger dense models like Llama-2 70B \
while running significantly faster. \
Mixtral 8x22B, a larger variant, achieved even stronger results on coding and reasoning benchmarks. \
DeepSeek-V2 introduced DeepSeekMoE, their proprietary MoE architecture with fine-grained experts. \
DeepSeek-V3 scaled this to 671B parameters with 256 experts, achieving state-of-the-art results. \
GPT-4 is widely believed to use MoE architecture, though OpenAI hasn't confirmed the details. \
DBRX from Databricks uses a unique MoE design with 16 experts and expert-choice routing, \
setting new records on open-source benchmarks. \
The trend is clear: the frontier models are increasingly adopting MoE architecture.

<bookmark mark='math_formulation'/>
Let's write down the mathematical formulation of MoE. \
For an input token x, the router computes gating weights g of x. \
g of x equals softmax of x times W-g, where W-g is the learned routing matrix. \
We then select the top-k gating weights using the KeepTopK function, \
which sets all non-top-k values to negative infinity. \
The final gating weights after top-k selection are g-hat of x. \
Each expert E-i processes the input independently: y-i equals E-i of x. \
The MoE output is the weighted sum of expert outputs: \
y equals sum over i of g-hat-i of x times y-i. \
In practice, we often add noise before top-k selection for load balancing: \
h of x equals x times W-g plus standard normal noise times softplus of x times W-noise. \
This noisy gating encourages exploration during training.

<bookmark mark='quantitative_comparison'/>
Let's compare dense vs MoE models quantitatively. \
Consider training a model with a fixed compute budget. \
A dense model might have 7 billion parameters and train for 1 trillion tokens. \
An MoE model with the same compute could have 8 experts of 7B each — 56B total parameters — \
and train for the same 1 trillion tokens. \
The MoE model would achieve better quality because it has more capacity \
for the same training cost. \
At inference time, the dense model uses all 7B parameters per token. \
The MoE model uses only 2 times 7B equals 14B active parameters per token \
plus shared parameters — roughly equivalent to a 13-14B dense model. \
So you get the quality of a 56B model with the inference speed of a 14B model. \
This is the MoE advantage: better pretraining efficiency and competitive inference speed.

<bookmark mark='tradeoffs'/>
MoE is not a free lunch, and I want to be honest about the trade-offs. \
First: memory requirements. All experts must be loaded in memory even if only some activate. \
For very large MoE models, this can require hundreds of gigabytes of VRAM. \
Second: implementation complexity. Routing, load balancing, and distributed training \
add significant engineering complexity compared to dense models. \
Third: fine-tuning challenges. MoE models can be harder to fine-tune effectively \
and may overfit on small datasets. \
Fourth: communication overhead. In distributed inference, routing tokens to experts \
on different devices adds latency. \
When should you use MoE? Use MoE when you have a large compute budget for pretraining \
and want to maximize model quality. Use MoE when you can afford the memory requirements \
and want faster inference. Use MoE for large-scale models where the parameter efficiency gains outweigh the complexity. \
Stick with dense models for smaller scales, simpler deployments, or when memory is constrained.

<bookmark mark='summary'/>
Let's bring it all together with a summary. \
MoE stands for Mixture of Experts. \
It replaces dense FFN layers with sparse MoE layers consisting of multiple expert networks and a router. \
The router selectively activates only a few experts per token using top-k routing. \
This sparsity allows models to have many more total parameters while keeping compute manageable. \
Load balancing techniques like auxiliary loss, noisy gating, and expert capacity \
ensure all experts are utilized during training. \
Switch Transformer simplified MoE with top-1 routing and router z-loss for stability. \
Expert Choice Routing flips the paradigm by having experts choose tokens. \
Real-world models like Mixtral, DeepSeek-V3, and likely GPT-4 use MoE to achieve massive scale. \
The trade-off is higher memory requirements and implementation complexity \
in exchange for better pretraining efficiency and competitive inference speed.

<bookmark mark='outro'/>
If this video helped you understand Mixture of Experts, please hit like and subscribe — \
it helps more people find this content. \
Drop a comment below: which MoE technique was most interesting — Switch Transformer, Expert Choice, or something else? \
I'll make a follow-up video on whichever topic gets the most requests.
<bookmark mark='final'/> Thanks for watching. See you in the next one.
"""

BOOKMARK_RE = re.compile(r"<bookmark\s+mark\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

# ── Scene helpers ──────────────────────────────────────────────────────────────

scene = Scene(width=WIDTH, height=HEIGHT, fps=FPS, background_color=BG)
scene.set_viewport_to_identity()

def title(text: str, *, y: float, color=BLACK, size: int = 72) -> Text:
    return Text(text, position=(960, y), font_size=size, font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=color, width=2.5), sketch_style=SKETCH)

def body(text: str, *, x: float = 960, y: float, color=BLACK,
         align: str = "center", size: int = 44) -> Text:
    return Text(text, position=(x, y), font_size=size, font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=color, width=2.0), sketch_style=SKETCH, align=align)

def label(text: str, *, x: float, y: float, color=BLACK, size: int = 36) -> Text:
    return body(text, x=x, y=y, color=color, align="center", size=size)

def erase(objects: list, *, t: float, dur: float = 1.0) -> None:
    eraser = Eraser(
        objects_to_erase=objects,
        drawable_cache=scene.drawable_cache,
        erase_color=scene.background_color,
        glow_dot_hint={"color": LIGHT_GRAY, "radius": 14},
    )
    scene.add(SketchAnimation(start_time=t, duration=dur), drawable=eraser)

def anim(drawable, *, t: float, dur: float = 1.2):
    scene.add(SketchAnimation(start_time=t, duration=dur), drawable=drawable)
    return drawable

def bullets(items: list[str], *, x: float, y0: float, dy: float,
            color=BLACK, size: int = 48) -> list[Text]:
    return [body(f"• {it}", x=x, y=y0 + i * dy, color=color, align="left", size=size)
            for i, it in enumerate(items)]

def process_box(text: str, *, cx: float, cy: float, w: float, h: float,
                fill=PASTEL_BLUE, border=BLUE, fs: int = 48) -> FlowchartProcess:
    return FlowchartProcess(
        text, top_left=(cx - w/2, cy - h/2), width=w, height=h,
        font_size=fs,
        fill_style=FillStyle(color=fill, opacity=0.35),
        stroke_style=StrokeStyle(color=border, width=4),
        sketch_style=SKETCH,
    )

def rrect(*, cx: float, cy: float, w: float, h: float,
          fill=PASTEL_BLUE, border=BLUE, opacity: float = 0.35,
          border_width: float = 4) -> RoundedRectangle:
    return RoundedRectangle(
        top_left=(cx - w/2, cy - h/2), width=w, height=h,
        border_radius=0.08,
        fill_style=FillStyle(color=fill, opacity=opacity),
        stroke_style=StrokeStyle(color=border, width=border_width),
        sketch_style=SKETCH,
    )

def arrow(sx: float, sy: float, ex: float, ey: float,
          color=BLACK, width: float = 5) -> Arrow:
    return Arrow(start_point=(sx, sy), end_point=(ex, ey),
                 stroke_style=StrokeStyle(color=color, width=width),
                 sketch_style=SKETCH)

def hline(sx: float, sy: float, ex: float, ey: float,
          color=GRAY, width: float = 3) -> Line:
    return Line(start=(sx, sy), end=(ex, ey),
                stroke_style=StrokeStyle(color=color, width=width),
                sketch_style=SKETCH)

def circle_node(text: str, *, cx: float, cy: float, r: float = 50,
                fill=PASTEL_BLUE, border=BLUE) -> tuple:
    c = Circle(center=(cx, cy), radius=r,
               stroke_style=StrokeStyle(color=border, width=4),
               fill_style=FillStyle(color=fill, opacity=0.7),
               sketch_style=SKETCH)
    lbl = label(text, x=cx, y=cy, color=border, size=36)
    return c, lbl

# ── Audio synthesis ────────────────────────────────────────────────────────────

async def synthesize(audio_path: Path, *, regenerate: bool = False) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    if audio_path.exists() and not regenerate:
        return
    comm = edge_tts.Communicate(strip_bookmarks(NARRATION), VOICE,
                                rate=VOICE_RATE)
    await comm.save(str(audio_path))

# ══════════════════════════════════════════════════════════════════════════════
# SCENE BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def build_scene(audio_path: str) -> float:
    with scene.voiceover(audio_path, text=NARRATION, volume=VOICE_VOLUME) as trk:

        # ── collect bookmark times ────────────────────────────────────────────
        bm = {name: trk.bookmark_time(name) for name in [
            "cold_open", "title", "intro",
            "dense_primer", "core_idea",
            "architecture", "routing",
            "sparsity", "load_balancing_problem",
            "load_balancing_solutions", "switch_transformer",
            "expert_choice", "training_challenges",
            "inference_benefits", "parameter_efficiency",
            "real_world_models", "math_formulation",
            "quantitative_comparison", "tradeoffs",
            "summary", "outro", "final",
        ]}

        # ══════════════════════════════════════════════════════════════════════
        # §0  COLD OPEN — hook question
        # ══════════════════════════════════════════════════════════════════════
        t = bm["cold_open"]

        hook_q = title("671B parameters running like 37B?",
                        y=300, color=BLUE, size=80)
        hook_sub = body("(that's not magic — that's MoE)", y=450, color=DARK_GRAY, size=52)
        hook_ans = body("→  Mixture of Experts  ←",
                        y=620, color=ORANGE, size=60)

        anim(hook_q,   t=t + 0.3, dur=1.8)
        anim(hook_sub, t=t + 2.2, dur=1.2)
        anim(hook_ans, t=t + 4.0, dur=1.5)

        cold_open_items = [hook_q, hook_sub, hook_ans]

        # ══════════════════════════════════════════════════════════════════════
        # §1  TITLE CARD
        # ══════════════════════════════════════════════════════════════════════
        t = bm["title"]
        erase(cold_open_items, t=t - 1.0)

        ttl   = title("Mixture of Experts", y=280, color=BLUE, size=84)
        ttl2  = title("(MoE)", y=400, color=BLUE, size=68)
        by_lbl = body("Beginner → Advanced Complete Guide", y=540, color=ORANGE, size=52)
        ds_box = rrect(cx=960, cy=720, w=700, h=110,
                       fill=PASTEL_BLUE, border=BLUE, opacity=0.25)
        ds_lbl = body("As used in GPT-4 · Mixtral · DeepSeek-V3 · DBRX",
                      y=720, color=DARK_GRAY, size=46)

        anim(ttl,    t=t + 0.4, dur=1.8)
        anim(ttl2,   t=t + 2.0, dur=1.2)
        anim(by_lbl, t=t + 3.2, dur=1.2)
        anim(ds_box, t=t + 4.5, dur=1.0)
        anim(ds_lbl, t=t + 4.8, dur=1.0)

        title_items = [ttl, ttl2, by_lbl, ds_box, ds_lbl]

        # ══════════════════════════════════════════════════════════════════════
        # §2  INTRO — why care
        # ══════════════════════════════════════════════════════════════════════
        t = bm["intro"]
        erase(title_items, t=t - 1.0)

        why_title = title("Why Does MoE Matter?", y=100, color=BLACK)
        why_pts = bullets([
            "GPT-4 rumored to use MoE — one of the most capable AI systems",
            "Mixtral 8x7B outperformed much larger dense models",
            "DeepSeek-V3: 671B total, 37B active per token",
            "DBRX set open-source records with MoE architecture",
            "Scale intelligence without scaling compute linearly",
        ], x=220, y0=250, dy=100, color=BLACK, size=40)

        anim(why_title, t=t + 0.5, dur=1.0)
        for i, b in enumerate(why_pts):
            anim(b, t=t + 1.5 + i * 1.5, dur=1.2)

        intro_items = [why_title] + why_pts

        # ══════════════════════════════════════════════════════════════════════
        # §3  DENSE PRIMER — how traditional LLMs work
        # ══════════════════════════════════════════════════════════════════════
        t = bm["dense_primer"]
        erase(intro_items, t=t - 1.0)

        dense_title = title("Dense Models: The Traditional Approach", y=100, color=PURPLE)

        # Single FFN box
        ffn_box = rrect(cx=960, cy=350, w=600, h=180,
                       fill=PASTEL_PURPLE, border=PURPLE, opacity=0.35)
        ffn_lbl = label("Dense FFN Layer", x=960, y=350, color=PURPLE, size=52)

        # Tokens flowing in
        tok_in = rrect(cx=960, cy=180, w=400, h=80,
                      fill=PASTEL_BLUE, border=BLUE, opacity=0.3)
        tok_in_lbl = label("Token x", x=960, y=180, color=BLUE, size=40)

        arr_in = arrow(960, 220, 960, 260, color=GRAY, width=4)

        # Output
        tok_out = rrect(cx=960, cy=520, w=400, h=80,
                       fill=PASTEL_GREEN, border=GREEN, opacity=0.3)
        tok_out_lbl = label("Output y", x=960, y=520, color=GREEN, size=40)

        arr_out = arrow(960, 440, 960, 480, color=GRAY, width=4)

        # Annotation
        note = body("Every token → ALL parameters activate",
                   y=650, color=RED, size=42)
        generalist = body("Like a generalist doctor: same knowledge for every patient",
                         y=760, color=DARK_GRAY, size=38)

        anim(dense_title, t=t + 0.4, dur=1.0)
        anim(tok_in, t=t + 1.2, dur=0.8)
        anim(tok_in_lbl, t=t + 1.5, dur=0.6)
        anim(arr_in, t=t + 2.0, dur=0.5)
        anim(ffn_box, t=t + 2.5, dur=1.0)
        anim(ffn_lbl, t=t + 2.8, dur=0.8)
        anim(arr_out, t=t + 4.0, dur=0.5)
        anim(tok_out, t=t + 4.5, dur=0.8)
        anim(tok_out_lbl, t=t + 4.8, dur=0.6)
        anim(note, t=t + 6.0, dur=1.2)
        anim(generalist, t=t + 7.5, dur=1.2)

        dense_items = [dense_title, tok_in, tok_in_lbl, arr_in,
                      ffn_box, ffn_lbl, arr_out, tok_out, tok_out_lbl,
                      note, generalist]

        # ══════════════════════════════════════════════════════════════════════
        # §4  CORE IDEA — specialization analogy
        # ══════════════════════════════════════════════════════════════════════
        t = bm["core_idea"]
        erase(dense_items, t=t - 1.0)

        idea_title = title("The Core Idea: Specialization", y=80, color=BLUE)

        # Hospital analogy
        hosp_box = rrect(cx=960, cy=250, w=1400, h=120,
                        fill=PASTEL_YELLOW, border=ORANGE, opacity=0.25)
        hosp_lbl = body("Hospital Analogy: Specialists vs Generalist",
                       y=250, color=ORANGE, size=44)

        # Specialists
        specialists = [
            ("Cardiologist", "Heart", PASTEL_RED, RED, 360),
            ("Neurologist", "Brain", PASTEL_BLUE, BLUE, 620),
            ("Orthopedist", "Bones", PASTEL_GREEN, GREEN, 880),
            ("Dermatologist", "Skin", PASTEL_PURPLE, PURPLE, 1140),
            ("Generalist", "All", PASTEL_GRAY, GRAY, 1400),
        ]

        spec_boxes, spec_lbls, spec_subs = [], [], []
        for name, sub, fill, border, cx in specialists:
            sb = rrect(cx=cx, cy=420, w=220, h=140,
                      fill=fill, border=border, opacity=0.4)
            sl = label(name, x=cx, y=390, color=border, size=34)
            ss = label(sub, x=cx, y=450, color=border, size=36)
            spec_boxes.append(sb)
            spec_lbls.append(sl)
            spec_subs.append(ss)

        # Receptionist/router
        router_box = rrect(cx=880, cy=620, w=400, h=100,
                          fill=PASTEL_ORANGE, border=ORANGE, opacity=0.4)
        router_lbl = label("Router / Receptionist", x=880, y=620, color=ORANGE, size=40)

        # Patient
        patient = rrect(cx=400, cy=620, w=200, h=80,
                      fill=PASTEL_BLUE, border=BLUE, opacity=0.35)
        patient_lbl = label("Patient", x=400, y=620, color=BLUE, size=36)

        arr_to_router = arrow(500, 620, 680, 620, color=GRAY, width=4)
        arr_to_cardio = arrow(1080, 620, 1080, 530, color=RED, width=3)

        insight = body("MoE: Many specialized experts + router = smarter, more efficient",
                      y=780, color=BLUE, size=40)
        insight2 = body("Each token gets routed to the expert(s) best suited for it",
                       y=880, color=DARK_GRAY, size=36)

        anim(idea_title, t=t + 0.4, dur=1.0)
        anim(hosp_box, t=t + 1.2, dur=0.8)
        anim(hosp_lbl, t=t + 1.5, dur=0.8)
        for i in range(5):
            anim(spec_boxes[i], t=t + 2.0 + i*0.3, dur=0.6)
            anim(spec_lbls[i], t=t + 2.2 + i*0.3, dur=0.4)
            anim(spec_subs[i], t=t + 2.4 + i*0.3, dur=0.4)
        anim(patient, t=t + 4.5, dur=0.6)
        anim(patient_lbl, t=t + 4.8, dur=0.4)
        anim(router_box, t=t + 5.5, dur=0.8)
        anim(router_lbl, t=t + 5.8, dur=0.6)
        anim(arr_to_router, t=t + 6.5, dur=0.5)
        anim(arr_to_cardio, t=t + 7.0, dur=0.5)
        anim(insight, t=t + 8.5, dur=1.2)
        anim(insight2, t=t + 10.0, dur=1.0)

        idea_items = [idea_title, hosp_box, hosp_lbl, router_box, router_lbl,
                     patient, patient_lbl, arr_to_router, arr_to_cardio,
                     insight, insight2] + spec_boxes + spec_lbls + spec_subs

        # ══════════════════════════════════════════════════════════════════════
        # §5  MoE ARCHITECTURE — experts + router
        # ══════════════════════════════════════════════════════════════════════
        t = bm["architecture"]
        erase(idea_items, t=t - 1.0)

        arch_title = title("MoE Architecture", y=80, color=BLUE)

        # Input
        input_box = rrect(cx=960, cy=180, w=300, h=80,
                        fill=PASTEL_BLUE, border=BLUE, opacity=0.3)
        input_lbl = label("Input x", x=960, y=180, color=BLUE, size=40)

        # Router
        router_box_a = rrect(cx=960, cy=320, w=400, h=100,
                           fill=PASTEL_ORANGE, border=ORANGE, opacity=0.4)
        router_lbl_a = label("Router (Gate)", x=960, y=320, color=ORANGE, size=42)

        arr_in_router = arrow(960, 220, 960, 270, color=GRAY, width=4)

        # Experts (8 shown)
        expert_boxes, expert_lbls = [], []
        expert_colors = [PASTEL_RED, PASTEL_BLUE, PASTEL_GREEN, PASTEL_PURPLE,
                        PASTEL_YELLOW, PASTEL_ORANGE, PASTEL_RED, PASTEL_BLUE]
        expert_borders = [RED, BLUE, GREEN, PURPLE, ORANGE, ORANGE, RED, BLUE]
        
        for i in range(8):
            row = i // 4
            col = i % 4
            cx = 340 + col * 340
            cy = 500 + row * 160
            eb = rrect(cx=cx, cy=cy, w=280, h=110,
                      fill=expert_colors[i], border=expert_borders[i], opacity=0.35)
            el = label(f"Expert {i+1}", x=cx, y=cy, color=expert_borders[i], size=38)
            expert_boxes.append(eb)
            expert_lbls.append(el)

        # Routing arrows (showing token going to 2 experts)
        arr_to_e2 = arrow(960, 370, 520, 440, color=ORANGE, width=4)
        arr_to_e5 = arrow(960, 370, 1400, 440, color=ORANGE, width=4)

        # Output combination
        combine_box = rrect(cx=960, cy=860, w=500, h=100,
                          fill=PASTEL_GREEN, border=GREEN, opacity=0.35)
        combine_lbl = label("Combine (weighted sum)", x=960, y=860, color=GREEN, size=38)

        arr_from_e2 = arrow(520, 560, 780, 810, color=GREEN, width=3)
        arr_from_e5 = arrow(1400, 560, 1140, 810, color=GREEN, width=3)

        # Output
        output_box = rrect(cx=960, cy=980, w=300, h=80,
                         fill=PASTEL_PURPLE, border=PURPLE, opacity=0.3)
        output_lbl = label("Output y", x=960, y=980, color=PURPLE, size=40)

        arr_out_final = arrow(960, 910, 960, 940, color=GRAY, width=4)

        note_arch = body("Router selects top-k experts (e.g., k=2)",
                        y=240, color=ORANGE, size=36)

        anim(arch_title, t=t + 0.3, dur=1.0)
        anim(input_box, t=t + 1.0, dur=0.6)
        anim(input_lbl, t=t + 1.3, dur=0.4)
        anim(arr_in_router, t=t + 1.5, dur=0.4)
        anim(router_box_a, t=t + 2.0, dur=0.8)
        anim(router_lbl_a, t=t + 2.3, dur=0.6)
        anim(note_arch, t=t + 3.0, dur=0.8)
        for i in range(8):
            anim(expert_boxes[i], t=t + 3.5 + i*0.2, dur=0.5)
            anim(expert_lbls[i], t=t + 3.7 + i*0.2, dur=0.3)
        anim(arr_to_e2, t=t + 5.5, dur=0.6)
        anim(arr_to_e5, t=t + 5.8, dur=0.6)
        anim(arr_from_e2, t=t + 6.5, dur=0.5)
        anim(arr_from_e5, t=t + 6.7, dur=0.5)
        anim(combine_box, t=t + 7.5, dur=0.8)
        anim(combine_lbl, t=t + 7.8, dur=0.6)
        anim(arr_out_final, t=t + 8.8, dur=0.4)
        anim(output_box, t=t + 9.0, dur=0.6)
        anim(output_lbl, t=t + 9.3, dur=0.4)

        arch_items = [arch_title, input_box, input_lbl, arr_in_router,
                      router_box_a, router_lbl_a, note_arch,
                      combine_box, combine_lbl, arr_out_final,
                      output_box, output_lbl,
                      arr_to_e2, arr_to_e5, arr_from_e2, arr_from_e5] + \
                     expert_boxes + expert_lbls

        # ══════════════════════════════════════════════════════════════════════
        # §6  ROUTING MECHANISM — Top-K explained
        # ══════════════════════════════════════════════════════════════════════
        t = bm["routing"]
        erase(arch_items, t=t - 1.0)

        route_title = title("Routing Mechanism: Top-K Selection", y=80, color=ORANGE)

        # Step 1: Compute scores
        step1_box = rrect(cx=480, cy=250, w=500, h=140,
                         fill=PASTEL_BLUE, border=BLUE, opacity=0.3)
        step1_lbl = body("Step 1: Compute scores", x=480, y=220, color=BLUE, size=38)
        step1_desc = body("g(x) = softmax(x·W_g)", x=480, y=280, color=BLUE, size=34)

        # Score visualization
        scores = [0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.03, 0.02]
        score_bars = []
        for i, score in enumerate(scores):
            bar_w = score * 180
            sb = rrect(cx=320 + i*75, cy=380, w=bar_w, h=40,
                      fill=PASTEL_BLUE, border=BLUE, opacity=0.6, border_width=2)
            score_bars.append(sb)

        scores_lbl = label("Expert scores", x=480, y=450, color=BLUE, size=36)

        # Arrow to step 2
        arr_step2 = arrow(750, 250, 950, 250, color=GRAY, width=5)

        # Step 2: Top-K selection
        step2_box = rrect(cx=1200, cy=250, w=500, h=140,
                         fill=PASTEL_ORANGE, border=ORANGE, opacity=0.3)
        step2_lbl = body("Step 2: Select Top-K", x=1200, y=220, color=ORANGE, size=38)
        step2_desc = body("KeepTopK(g(x), k=2)", x=1200, y=280, color=ORANGE, size=34)

        # Selected scores highlighted
        sel_bars = []
        for i, score in enumerate([0.8, 0.6]):
            bar_w = score * 180
            sb = rrect(cx=1040 + i*75, cy=380, w=bar_w, h=40,
                      fill=PASTEL_GREEN, border=GREEN, opacity=0.8, border_width=3)
            sel_bars.append(sb)

        dim_bars = []
        for i, score in enumerate([0.4, 0.2, 0.1, 0.05, 0.03, 0.02]):
            bar_w = score * 180
            sb = rrect(cx=1190 + i*75, cy=380, w=bar_w, h=40,
                      fill=LIGHT_GRAY, border=GRAY, opacity=0.4, border_width=1)
            dim_bars.append(sb)

        selected_lbl = label("Selected (k=2)", x=1200, y=450, color=GREEN, size=36)

        # Step 3: Send to experts
        step3_box = rrect(cx=960, cy=580, w=600, h=120,
                         fill=PASTEL_PURPLE, border=PURPLE, opacity=0.3)
        step3_lbl = body("Step 3: Send to experts & combine", x=960, y=580, color=PURPLE, size=36)

        # Formula
        formula_route = Math(
            r"y = \sum_{i=1}^{n} \hat{g}_i(x) \cdot E_i(x)",
            position=(960, 750), font_size=64,
            stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)

        examples = body(
            "Mixtral 8x7B: 8 experts, k=2  |  DeepSeek-V3: 256 experts, k=8",
            y=880, color=DARK_GRAY, size=36)

        anim(route_title, t=t + 0.3, dur=1.0)
        anim(step1_box, t=t + 1.2, dur=0.8)
        anim(step1_lbl, t=t + 1.5, dur=0.6)
        anim(step1_desc, t=t + 1.8, dur=0.6)
        for i, sb in enumerate(score_bars):
            anim(sb, t=t + 2.2 + i*0.15, dur=0.3)
        anim(scores_lbl, t=t + 3.5, dur=0.6)
        anim(arr_step2, t=t + 4.0, dur=0.5)
        anim(step2_box, t=t + 4.5, dur=0.8)
        anim(step2_lbl, t=t + 4.8, dur=0.6)
        anim(step2_desc, t=t + 5.1, dur=0.6)
        for i, sb in enumerate(sel_bars):
            anim(sb, t=t + 5.5 + i*0.2, dur=0.3)
        for i, sb in enumerate(dim_bars):
            anim(sb, t=t + 6.0 + i*0.1, dur=0.2)
        anim(selected_lbl, t=t + 6.5, dur=0.6)
        anim(step3_box, t=t + 7.5, dur=0.8)
        anim(step3_lbl, t=t + 7.8, dur=0.6)
        anim(formula_route, t=t + 9.0, dur=2.0)
        anim(examples, t=t + 11.5, dur=1.2)

        route_items = [route_title, step1_box, step1_lbl, step1_desc,
                      step2_box, step2_lbl, step2_desc,
                      step3_box, step3_lbl, formula_route, examples,
                      arr_step2, scores_lbl, selected_lbl] + \
                     score_bars + sel_bars + dim_bars

        # ══════════════════════════════════════════════════════════════════════
        # §7  SPARSITY EXPLAINED
        # ══════════════════════════════════════════════════════════════════════
        t = bm["sparsity"]
        erase(route_items, t=t - 1.0)

        sparse_title = title("Sparsity: Conditional Computation", y=100, color=GREEN)

        # Dense model visualization
        dense_panel = rrect(cx=440, cy=350, w=480, h=380,
                          fill=PASTEL_RED, border=RED, opacity=0.2)
        dense_lbl = label("Dense Model", x=440, y=200, color=RED, size=48)

        # All parameters active
        dense_cells = []
        for row in range(6):
            for col in range(6):
                dc = rrect(cx=290 + col*52, cy=270 + row*52, w=42, h=42,
                          fill=PASTEL_RED, border=RED, opacity=0.7, border_width=2)
                dense_cells.append(dc)

        dense_note = body("ALL parameters\nactivate", x=440, y=560, color=RED, size=40)

        # Arrow
        arr_sparse = arrow(700, 350, 880, 350, color=GRAY, width=6)

        # Sparse model visualization
        sparse_panel = rrect(cx=1320, cy=350, w=480, h=380,
                           fill=PASTEL_GREEN, border=GREEN, opacity=0.2)
        sparse_lbl = label("MoE (Sparse)", x=1320, y=200, color=GREEN, size=48)

        # Only some parameters active
        sparse_cells = []
        active_indices = [(0,0), (0,1), (1,0), (1,1), (2,3), (3,2), (4,4), (5,5)]
        for row in range(6):
            for col in range(6):
                if (row, col) in active_indices:
                    fill = PASTEL_GREEN
                    border = GREEN
                    opacity = 0.8
                else:
                    fill = LIGHT_GRAY
                    border = GRAY
                    opacity = 0.2
                sc = rrect(cx=1170 + col*52, cy=270 + row*52, w=42, h=42,
                          fill=fill, border=border, opacity=opacity, border_width=2)
                sparse_cells.append(sc)

        sparse_note = body("Only SOME parameters\nactivate per token", x=1320, y=560, color=GREEN, size=40)

        # Bottom explanation
        hospital_analogy = body(
            "Like a 100-doctor hospital where only 10 work on any given patient",
            y=720, color=BLUE, size=38)
        benefit = body(
            "10× more parameters, similar compute cost!",
            y=820, color=ORANGE, size=44)

        anim(sparse_title, t=t + 0.3, dur=1.0)
        anim(dense_panel, t=t + 1.2, dur=0.8)
        anim(dense_lbl, t=t + 1.5, dur=0.6)
        for i, dc in enumerate(dense_cells):
            anim(dc, t=t + 1.8 + i*0.08, dur=0.2)
        anim(dense_note, t=t + 4.0, dur=0.8)
        anim(arr_sparse, t=t + 5.0, dur=0.6)
        anim(sparse_panel, t=t + 5.5, dur=0.8)
        anim(sparse_lbl, t=t + 5.8, dur=0.6)
        for i, sc in enumerate(sparse_cells):
            anim(sc, t=t + 6.2 + i*0.08, dur=0.2)
        anim(sparse_note, t=t + 8.0, dur=0.8)
        anim(hospital_analogy, t=t + 9.5, dur=1.2)
        anim(benefit, t=t + 11.0, dur=1.2)

        sparse_items = [sparse_title, dense_panel, dense_lbl, dense_note,
                       sparse_panel, sparse_lbl, sparse_note,
                       arr_sparse, hospital_analogy, benefit] + \
                      dense_cells + sparse_cells

        # ══════════════════════════════════════════════════════════════════════
        # §8  LOAD BALANCING PROBLEM
        # ══════════════════════════════════════════════════════════════════════
        t = bm["load_balancing_problem"]
        erase(sparse_items, t=t - 1.0)

        lb_title = title("The Load Balancing Problem", y=100, color=RED)

        # Imbalanced experts visualization
        experts_data = [
            ("Expert 1", 95, PASTEL_RED, RED),
            ("Expert 2", 88, PASTEL_RED, RED),
            ("Expert 3", 82, PASTEL_ORANGE, ORANGE),
            ("Expert 4", 45, PASTEL_YELLOW, ORANGE),
            ("Expert 5", 12, PASTEL_GREEN, GREEN),
            ("Expert 6", 8, PASTEL_GREEN, GREEN),
            ("Expert 7", 5, PASTEL_BLUE, BLUE),
            ("Expert 8", 2, PASTEL_BLUE, BLUE),
        ]

        expert_bars_lb, expert_lbls_lb, expert_counts_lb = [], [], []
        for i, (name, count, fill, border) in enumerate(experts_data):
            cx = 220 + i * 170
            bar_h = count * 5
            eb = rrect(cx=cx, cy=500 - bar_h/2, w=110, h=bar_h,
                      fill=fill, border=border, opacity=0.6, border_width=3)
            el = label(name, x=cx, y=650, color=border, size=32)
            ec = label(f"{count}%", x=cx, y=500 - bar_h/2, color=border, size=36)
            expert_bars_lb.append(eb)
            expert_lbls_lb.append(el)
            expert_counts_lb.append(ec)

        problem_note = body(
            "Router converges to always send tokens to same 'popular' experts",
            y=750, color=RED, size=38)
        vicious = body(
            "Vicious cycle: popular experts get more data → become better → get more tokens",
            y=850, color=DARK_GRAY, size=34)

        anim(lb_title, t=t + 0.3, dur=1.0)
        for i in range(8):
            anim(expert_bars_lb[i], t=t + 1.2 + i*0.15, dur=0.4)
            anim(expert_lbls_lb[i], t=t + 1.4 + i*0.15, dur=0.3)
            anim(expert_counts_lb[i], t=t + 1.6 + i*0.15, dur=0.3)
        anim(problem_note, t=t + 4.0, dur=1.2)
        anim(vicious, t=t + 5.5, dur=1.2)

        lb_items = [lb_title, problem_note, vicious] + \
                   expert_bars_lb + expert_lbls_lb + expert_counts_lb

        # ══════════════════════════════════════════════════════════════════════
        # §9  LOAD BALANCING SOLUTIONS
        # ══════════════════════════════════════════════════════════════════════
        t = bm["load_balancing_solutions"]
        erase(lb_items, t=t - 1.0)

        sol_title = title("Load Balancing Solutions", y=80, color=GREEN)

        # Solution 1: Auxiliary loss
        sol1_box = rrect(cx=440, cy=220, w=480, h=180,
                        fill=PASTEL_BLUE, border=BLUE, opacity=0.3)
        sol1_lbl = body("1. Auxiliary Loss", x=440, y=190, color=BLUE, size=38)
        sol1_desc = body("Penalize imbalance in loss\nEncourage uniform utilization",
                        x=440, y=260, color=BLUE, size=32)

        # Solution 2: Noisy gating
        sol2_box = rrect(cx=920, cy=220, w=480, h=180,
                        fill=PASTEL_ORANGE, border=ORANGE, opacity=0.3)
        sol2_lbl = body("2. Noisy Gating", x=920, y=190, color=ORANGE, size=38)
        sol2_desc = body("Add noise before top-K\nEncourage exploration",
                        x=920, y=260, color=ORANGE, size=32)

        # Solution 3: Expert capacity
        sol3_box = rrect(cx=1400, cy=220, w=480, h=180,
                        fill=PASTEL_PURPLE, border=PURPLE, opacity=0.3)
        sol3_lbl = body("3. Expert Capacity", x=1400, y=190, color=PURPLE, size=38)
        sol3_desc = body("Hard limit on tokens per expert\nPrevent monopolization",
                        x=1400, y=260, color=PURPLE, size=32)

        # Balanced visualization
        balanced_note = body("Result: Balanced expert utilization", y=480, color=GREEN, size=40)

        balanced_bars = []
        for i in range(8):
            cx = 220 + i * 170
            bar_h = 50 * 5  # All at ~50%
            bb = rrect(cx=cx, cy=500 - bar_h/2, w=110, h=bar_h,
                      fill=PASTEL_GREEN, border=GREEN, opacity=0.6, border_width=3)
            balanced_bars.append(bb)

        balanced_lbls = [label(f"E{i+1}", x=220 + i*170, y=650, color=GREEN, size=32)
                       for i in range(8)]

        hospital_bonus = body(
            "Like giving receptionist a bonus for ensuring all doctors get equal patients",
            y=750, color=DARK_GRAY, size=34)

        anim(sol_title, t=t + 0.3, dur=1.0)
        anim(sol1_box, t=t + 1.2, dur=0.8)
        anim(sol1_lbl, t=t + 1.5, dur=0.6)
        anim(sol1_desc, t=t + 1.8, dur=0.8)
        anim(sol2_box, t=t + 2.5, dur=0.8)
        anim(sol2_lbl, t=t + 2.8, dur=0.6)
        anim(sol2_desc, t=t + 3.1, dur=0.8)
        anim(sol3_box, t=t + 3.8, dur=0.8)
        anim(sol3_lbl, t=t + 4.1, dur=0.6)
        anim(sol3_desc, t=t + 4.4, dur=0.8)
        anim(balanced_note, t=t + 5.5, dur=1.0)
        for i, bb in enumerate(balanced_bars):
            anim(bb, t=t + 6.5 + i*0.1, dur=0.3)
        for i, bl in enumerate(balanced_lbls):
            anim(bl, t=t + 7.0 + i*0.1, dur=0.2)
        anim(hospital_bonus, t=t + 8.5, dur=1.2)

        sol_items = [sol_title, sol1_box, sol1_lbl, sol1_desc,
                    sol2_box, sol2_lbl, sol2_desc,
                    sol3_box, sol3_lbl, sol3_desc,
                    balanced_note, hospital_bonus] + \
                   balanced_bars + balanced_lbls

        # ══════════════════════════════════════════════════════════════════════
        # §10  SWITCH TRANSFORMER
        # ══════════════════════════════════════════════════════════════════════
        t = bm["switch_transformer"]
        erase(sol_items, t=t - 1.0)

        switch_title = title("Switch Transformer: Simplified MoE", y=80, color=BLUE)

        # Traditional MoE (top-k)
        trad_box = rrect(cx=440, cy=280, w=480, h=300,
                        fill=PASTEL_RED, border=RED, opacity=0.2)
        trad_lbl = label("Traditional MoE", x=440, y=180, color=RED, size=46)

        trad_experts = []
        for i in range(4):
            te = rrect(cx=340 + i*95, cy=350, w=80, h=80,
                      fill=PASTEL_RED, border=RED, opacity=0.5, border_width=2)
            trad_experts.append(te)

        trad_k = label("k > 1 (e.g., k=2)", x=440, y=450, color=RED, size=38)

        # Arrow
        arr_switch = arrow(700, 280, 880, 280, color=GRAY, width=6)

        # Switch Transformer (top-1)
        switch_box = rrect(cx=1320, cy=280, w=480, h=300,
                          fill=PASTEL_GREEN, border=GREEN, opacity=0.2)
        switch_lbl = label("Switch Transformer", x=1320, y=180, color=GREEN, size=46)

        switch_experts = []
        for i in range(4):
            se = rrect(cx=1220 + i*95, cy=350, w=80, h=80,
                      fill=PASTEL_GREEN, border=GREEN, opacity=0.5, border_width=2)
            switch_experts.append(se)

        # Highlight one expert
        highlighted = rrect(cx=1320, cy=350, w=80, h=80,
                           fill=PASTEL_ORANGE, border=ORANGE, opacity=0.9, border_width=4)

        switch_k = label("k = 1 (top-1)", x=1320, y=450, color=GREEN, size=38)

        # Benefits
        benefit1 = body("✓ Simpler architecture (no weighted sum)", x=440, y=580, color=BLUE, size=36)
        benefit2 = body("✓ Works just as well, sometimes better", x=440, y=680, color=BLUE, size=36)
        benefit3 = body("✓ Router z-loss for stability", x=440, y=780, color=BLUE, size=36)

        insight_switch = body(
            "With enough experts + load balancing, each token finds a truly specialized expert",
            y=880, color=ORANGE, size=38)

        anim(switch_title, t=t + 0.3, dur=1.0)
        anim(trad_box, t=t + 1.2, dur=0.8)
        anim(trad_lbl, t=t + 1.5, dur=0.6)
        for i, te in enumerate(trad_experts):
            anim(te, t=t + 1.8 + i*0.15, dur=0.3)
        anim(trad_k, t=t + 2.5, dur=0.6)
        anim(arr_switch, t=t + 3.0, dur=0.5)
        anim(switch_box, t=t + 3.5, dur=0.8)
        anim(switch_lbl, t=t + 3.8, dur=0.6)
        for i, se in enumerate(switch_experts):
            anim(se, t=t + 4.2 + i*0.15, dur=0.3)
        anim(highlighted, t=t + 5.0, dur=0.5)
        anim(switch_k, t=t + 5.3, dur=0.6)
        anim(benefit1, t=t + 6.0, dur=0.8)
        anim(benefit2, t=t + 7.0, dur=0.8)
        anim(benefit3, t=t + 8.0, dur=0.8)
        anim(insight_switch, t=t + 9.0, dur=1.2)

        switch_items = [switch_title, trad_box, trad_lbl, trad_k,
                        switch_box, switch_lbl, switch_k,
                        benefit1, benefit2, benefit3, insight_switch,
                        arr_switch, highlighted] + \
                       trad_experts + switch_experts

        # ══════════════════════════════════════════════════════════════════════
        # §11  EXPERT CHOICE ROUTING
        # ══════════════════════════════════════════════════════════════════════
        t = bm["expert_choice"]
        erase(switch_items, t=t - 1.0)

        ec_title = title("Expert Choice Routing", y=80, color=PURPLE)

        # Traditional: token chooses experts
        trad_panel = rrect(cx=440, cy=350, w=480, h=350,
                          fill=PASTEL_BLUE, border=BLUE, opacity=0.2)
        trad_title_ec = label("Traditional", x=440, y=180, color=BLUE, size=44)

        token_node = circle_node("Token", cx=480, cy=260, r=50, fill=PASTEL_YELLOW, border=ORANGE)

        experts_trad = []
        arrs_trad = []
        for i in range(4):
            angle = i * 90
            import math
            ex = 440 + 140 * math.cos(math.radians(angle))
            ey = 380 + 140 * math.sin(math.radians(angle))
            ee = circle_node(f"E{i+1}", cx=ex, cy=ey, r=40, fill=PASTEL_BLUE, border=BLUE)
            experts_trad.extend(ee)
            arrs_trad.append(arrow(440, 260, ex, ey - 40, color=BLUE, width=3))

        trad_desc = body("Token chooses experts", x=440, y=550, color=BLUE, size=32)

        # Arrow
        arr_ec = arrow(700, 350, 880, 350, color=GRAY, width=6)

        # Expert Choice: experts choose tokens
        ec_panel = rrect(cx=1320, cy=350, w=480, h=350,
                        fill=PASTEL_GREEN, border=GREEN, opacity=0.2)
        ec_title_lbl = label("Expert Choice", x=1320, y=180, color=GREEN, size=44)

        experts_ec = []
        arrs_ec = []
        for i in range(4):
            angle = i * 90
            import math
            ex = 1320 + 140 * math.cos(math.radians(angle))
            ey = 380 + 140 * math.sin(math.radians(angle))
            ee = circle_node(f"E{i+1}", cx=ex, cy=ey, r=40, fill=PASTEL_GREEN, border=GREEN)
            experts_ec.extend(ee)
            arrs_ec.append(arrow(ex, ey + 40, 1320, 260, color=GREEN, width=3))

        token_ec = circle_node("Token", cx=1440, cy=260, r=50, fill=PASTEL_YELLOW, border=ORANGE)

        ec_desc = body("Experts bid on tokens", x=1320, y=550, color=GREEN, size=32)

        benefits_ec = body(
            "✓ Better load balancing (experts compete)\n✓ Variable experts per token\n✓ 2x+ training efficiency",
            y=680, color=PURPLE, size=34)

        anim(ec_title, t=t + 0.3, dur=1.0)
        anim(trad_panel, t=t + 1.2, dur=0.8)
        anim(trad_title_ec, t=t + 1.5, dur=0.6)
        anim(token_node[0], t=t + 2.0, dur=0.6)
        anim(token_node[1], t=t + 2.3, dur=0.4)
        for i, ee in enumerate(experts_trad):
            anim(ee, t=t + 2.5 + i*0.15, dur=0.4)
        for i, arr in enumerate(arrs_trad):
            anim(arr, t=t + 3.2 + i*0.15, dur=0.3)
        anim(trad_desc, t=t + 4.0, dur=0.8)
        anim(arr_ec, t=t + 5.0, dur=0.5)
        anim(ec_panel, t=t + 5.5, dur=0.8)
        anim(ec_title_lbl, t=t + 5.8, dur=0.6)
        for i, ee in enumerate(experts_ec):
            anim(ee, t=t + 6.2 + i*0.15, dur=0.4)
        for i, arr in enumerate(arrs_ec):
            anim(arr, t=t + 6.9 + i*0.15, dur=0.3)
        anim(token_ec[0], t=t + 7.8, dur=0.6)
        anim(token_ec[1], t=t + 8.1, dur=0.4)
        anim(ec_desc, t=t + 8.5, dur=0.8)
        anim(benefits_ec, t=t + 9.5, dur=1.2)

        ec_items = [ec_title, trad_panel, trad_title_ec, trad_desc,
                    ec_panel, ec_title_lbl, ec_desc, benefits_ec,
                    arr_ec] + list(token_node) + experts_trad + arrs_trad + \
                    experts_ec + arrs_ec + list(token_ec)

        # ══════════════════════════════════════════════════════════════════════
        # §12  TRAINING CHALLENGES
        # ══════════════════════════════════════════════════════════════════════
        t = bm["training_challenges"]
        erase(ec_items, t=t - 1.0)

        train_title = title("Training Challenges", y=100, color=RED)

        challenges = [
            ("Fine-tuning Instability", "Model may overfit on small datasets\nExperts forget general patterns",
             PASTEL_RED, RED, 380),
            ("Communication Overhead", "All-to-all communication in distributed training\nTokens routed to different GPUs",
             PASTEL_ORANGE, ORANGE, 920),
            ("Hyperparameter Sensitivity", "Number of experts, routing strategy\nCapacity factor, loss weights all need tuning",
             PASTEL_PURPLE, PURPLE, 1460),
        ]

        challenge_boxes, challenge_lbls, challenge_descs = [], [], []
        for name, desc, fill, border, cx in challenges:
            cb = rrect(cx=cx, cy=380, w=420, h=220,
                      fill=fill, border=border, opacity=0.3)
            cl = label(name, x=cx, y=280, color=border, size=42)
            cd = body(desc, x=cx, y=400, color=border, size=34, align="center")
            challenge_boxes.append(cb)
            challenge_lbls.append(cl)
            challenge_descs.append(cd)

        note_train = body(
            "Despite challenges, MoE benefits make the effort worthwhile",
            y=660, color=BLUE, size=38)

        anim(train_title, t=t + 0.3, dur=1.0)
        for i in range(3):
            anim(challenge_boxes[i], t=t + 1.2 + i*1.0, dur=0.8)
            anim(challenge_lbls[i], t=t + 1.5 + i*1.0, dur=0.6)
            anim(challenge_descs[i], t=t + 1.8 + i*1.0, dur=1.0)
        anim(note_train, t=t + 5.0, dur=1.2)

        train_items = [train_title, note_train] + \
                      challenge_boxes + challenge_lbls + challenge_descs

        # ══════════════════════════════════════════════════════════════════════
        # §13  INFERENCE BENEFITS
        # ══════════════════════════════════════════════════════════════════════
        t = bm["inference_benefits"]
        erase(train_items, t=t - 1.0)

        inf_title = title("Inference Benefits", y=80, color=GREEN)

        # Mixtral example
        mixtral_box = rrect(cx=440, cy=280, w=480, h=300,
                          fill=PASTEL_BLUE, border=BLUE, opacity=0.25)
        mixtral_lbl = label("Mixtral 8x7B", x=440, y=180, color=BLUE, size=46)

        mixtral_total = body("Total: 46.7B params", x=440, y=260, color=BLUE, size=40)
        mixtral_active = body("Active: ~13B per token", x=440, y=340, color=GREEN, size=40)
        mixtral_speed = body("Speed: 13B dense model", x=440, y=420, color=ORANGE, size=40)

        # DeepSeek example
        deepseek_box = rrect(cx=1320, cy=280, w=480, h=300,
                           fill=PASTEL_PURPLE, border=PURPLE, opacity=0.25)
        deepseek_lbl = label("DeepSeek-V3", x=1320, y=180, color=PURPLE, size=46)

        deepseek_total = body("Total: 671B params", x=1320, y=260, color=PURPLE, size=40)
        deepseek_active = body("Active: 37B per token", x=1320, y=340, color=GREEN, size=40)
        deepseek_speed = body("Speed: 37B dense model", x=1320, y=420, color=ORANGE, size=40)

        # Key insight
        insight_inf = body(
            "FLOPs scale with ACTIVE parameters, not total",
            y=520, color=GREEN, size=40)

        # Trade-off
        tradeoff_box = rrect(cx=880, cy=680, w=1120, h=150,
                            fill=PASTEL_RED, border=RED, opacity=0.2)
        tradeoff_lbl = body(
            "Trade-off: All parameters must be loaded in memory\nHigher VRAM requirement for same inference speed",
            y=680, color=RED, size=36)

        anim(inf_title, t=t + 0.3, dur=1.0)
        anim(mixtral_box, t=t + 1.2, dur=0.8)
        anim(mixtral_lbl, t=t + 1.5, dur=0.6)
        anim(mixtral_total, t=t + 2.0, dur=0.6)
        anim(mixtral_active, t=t + 2.5, dur=0.6)
        anim(mixtral_speed, t=t + 3.0, dur=0.6)
        anim(deepseek_box, t=t + 3.5, dur=0.8)
        anim(deepseek_lbl, t=t + 3.8, dur=0.6)
        anim(deepseek_total, t=t + 4.3, dur=0.6)
        anim(deepseek_active, t=t + 4.8, dur=0.6)
        anim(deepseek_speed, t=t + 5.3, dur=0.6)
        anim(insight_inf, t=t + 6.0, dur=1.0)
        anim(tradeoff_box, t=t + 7.5, dur=0.8)
        anim(tradeoff_lbl, t=t + 7.8, dur=1.0)

        inf_items = [inf_title, insight_inf, tradeoff_box, tradeoff_lbl,
                     mixtral_box, mixtral_lbl, mixtral_total, mixtral_active, mixtral_speed,
                     deepseek_box, deepseek_lbl, deepseek_total, deepseek_active, deepseek_speed]

        # ══════════════════════════════════════════════════════════════════════
        # §14  PARAMETER EFFICIENCY
        # ══════════════════════════════════════════════════════════════════════
        t = bm["parameter_efficiency"]
        erase(inf_items, t=t - 1.0)

        param_title = title("Parameter Efficiency", y=80, color=BLUE)

        # Dense model
        dense_param_box = rrect(cx=440, cy=280, w=480, h=250,
                              fill=PASTEL_RED, border=RED, opacity=0.2)
        dense_param_lbl = label("Dense Model", x=440, y=180, color=RED, size=46)
        dense_eq = body("Total = Active", x=440, y=320, color=RED, size=44)
        dense_ex = body("7B total = 7B active", x=440, y=400, color=RED, size=40)

        # Arrow
        arr_param = arrow(700, 280, 880, 280, color=GRAY, width=6)

        # MoE model
        moe_param_box = rrect(cx=1320, cy=280, w=480, h=250,
                            fill=PASTEL_GREEN, border=GREEN, opacity=0.2)
        moe_param_lbl = label("MoE Model", x=1320, y=180, color=GREEN, size=46)
        moe_eq = body("Total >> Active", x=1320, y=320, color=GREEN, size=44)
        moe_ex = body("61B total, 13B active", x=1320, y=400, color=GREEN, size=40)

        # Sparsity ratio
        sparse_title = body("Sparsity Ratio = Active / Total", y=520, color=ORANGE, size=38)

        mixtral_sparse = body("Mixtral: 13B / 61B = 21%", x=440, y=620, color=BLUE, size=36)
        deepseek_sparse = body("DeepSeek-V3: 37B / 671B = 5.5%", x=1320, y=620, color=PURPLE, size=36)

        analogy = body(
            "Like a massive encyclopedia but only reading a few pages per question",
            y=720, color=DARK_GRAY, size=36)

        anim(param_title, t=t + 0.3, dur=1.0)
        anim(dense_param_box, t=t + 1.2, dur=0.8)
        anim(dense_param_lbl, t=t + 1.5, dur=0.6)
        anim(dense_eq, t=t + 2.0, dur=0.6)
        anim(dense_ex, t=t + 2.5, dur=0.6)
        anim(arr_param, t=t + 3.0, dur=0.5)
        anim(moe_param_box, t=t + 3.5, dur=0.8)
        anim(moe_param_lbl, t=t + 3.8, dur=0.6)
        anim(moe_eq, t=t + 4.3, dur=0.6)
        anim(moe_ex, t=t + 4.8, dur=0.6)
        anim(sparse_title, t=t + 5.5, dur=0.8)
        anim(mixtral_sparse, t=t + 6.5, dur=0.8)
        anim(deepseek_sparse, t=t + 7.5, dur=0.8)
        anim(analogy, t=t + 8.5, dur=1.2)

        param_items = [param_title, sparse_title, analogy,
                      dense_param_box, dense_param_lbl, dense_eq, dense_ex,
                      moe_param_box, moe_param_lbl, moe_eq, moe_ex,
                      arr_param, mixtral_sparse, deepseek_sparse]

        # ══════════════════════════════════════════════════════════════════════
        # §15  REAL-WORLD MODELS
        # ══════════════════════════════════════════════════════════════════════
        t = bm["real_world_models"]
        erase(param_items, t=t - 1.0)

        models_title = title("Real-World MoE Models", y=80, color=BLUE)

        models = [
            ("Mixtral 8x7B", "8 experts, k=2\nOutperformed Llama-2 70B", PASTEL_BLUE, BLUE, 340),
            ("Mixtral 8x22B", "Larger variant\nStrong coding/reasoning", PASTEL_BLUE, BLUE, 640),
            ("DeepSeek-V2", "DeepSeekMoE architecture\nFine-grained experts", PASTEL_PURPLE, PURPLE, 940),
            ("DeepSeek-V3", "671B total, 256 experts\nState-of-the-art results", PASTEL_PURPLE, PURPLE, 1240),
            ("GPT-4", "Rumored MoE\nMost capable AI system", PASTEL_ORANGE, ORANGE, 340, 640),
            ("DBRX", "16 experts, expert-choice\nOpen-source records", PASTEL_GREEN, GREEN, 940, 1240),
        ]

        model_boxes, model_lbls, model_descs = [], [], []
        for i, (name, desc, fill, border, cx, cy) in enumerate([(models[0][0], models[0][1], models[0][2], models[0][3], models[0][4], 280),
                                                                (models[1][0], models[1][1], models[1][2], models[1][3], models[1][4], 280),
                                                                (models[2][0], models[2][1], models[2][2], models[2][3], models[2][4], 280),
                                                                (models[3][0], models[3][1], models[3][2], models[3][3], models[3][4], 280),
                                                                (models[4][0], models[4][1], models[4][2], models[4][3], models[4][4], 560),
                                                                (models[5][0], models[5][1], models[5][2], models[5][3], models[5][4], 560)]):
            mb = rrect(cx=cx, cy=cy, w=280, h=170,
                      fill=fill, border=border, opacity=0.3)
            ml = label(name, x=cx, y=cy - 30, color=border, size=38)
            md = body(desc, x=cx, y=cy + 40, color=border, size=30, align="center")
            model_boxes.append(mb)
            model_lbls.append(ml)
            model_descs.append(md)

        trend = body(
            "Trend: Frontier models increasingly adopt MoE architecture",
            y=820, color=ORANGE, size=38)

        anim(models_title, t=t + 0.3, dur=1.0)
        for i in range(6):
            anim(model_boxes[i], t=t + 1.2 + i*0.4, dur=0.6)
            anim(model_lbls[i], t=t + 1.5 + i*0.4, dur=0.4)
            anim(model_descs[i], t=t + 1.8 + i*0.4, dur=0.6)
        anim(trend, t=t + 5.0, dur=1.2)

        models_items = [models_title, trend] + model_boxes + model_lbls + model_descs

        # ══════════════════════════════════════════════════════════════════════
        # §16  MATHEMATICAL FORMULATION
        # ══════════════════════════════════════════════════════════════════════
        t = bm["math_formulation"]
        erase(models_items, t=t - 1.0)

        math_title = title("Mathematical Formulation", y=80, color=PURPLE)

        equations = [
            (r"g(x) = \text{softmax}(x \cdot W_g)", 180, "Router scores"),
            (r"\hat{g}(x) = \text{Softmax}(\text{KeepTopK}(g(x), k))", 300, "Top-K selection"),
            (r"y_i = E_i(x)", 420, "Expert output"),
            (r"y = \sum_{i=1}^{n} \hat{g}_i(x) \cdot y_i", 560, "Weighted sum"),
            (r"h(x) = x \cdot W_g + \mathcal{N}(0,1) \cdot \text{softplus}(x \cdot W_{noise})", 700, "Noisy gating"),
        ]

        math_objs, math_anns = [], []
        for latex, ypos, ann in equations:
            mo = Math(latex, position=(480, ypos), font_size=56,
                     stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
            ma = label(ann, x=1400, y=ypos, color=BLUE, size=36)
            math_objs.append(mo)
            math_anns.append(ma)

        note_math = body(
            "Noise encourages exploration during training for better load balancing",
            y=880, color=ORANGE, size=34)

        anim(math_title, t=t + 0.3, dur=1.0)
        for i, (mo, ma) in enumerate(zip(math_objs, math_anns)):
            anim(mo, t=t + 1.2 + i*1.5, dur=1.2)
            anim(ma, t=t + 1.5 + i*1.5, dur=0.8)
        anim(note_math, t=t + 10.0, dur=1.2)

        math_items = [math_title, note_math] + math_objs + math_anns

        # ══════════════════════════════════════════════════════════════════════
        # §17  QUANTITATIVE COMPARISON
        # ══════════════════════════════════════════════════════════════════════
        t = bm["quantitative_comparison"]
        erase(math_items, t=t - 1.0)

        quant_title = title("Dense vs MoE: Quantitative Comparison", y=80, color=BLUE)

        # Dense model
        dense_quant_box = rrect(cx=440, cy=280, w=480, h=280,
                              fill=PASTEL_RED, border=RED, opacity=0.2)
        dense_quant_lbl = label("Dense (7B)", x=440, y=180, color=RED, size=46)
        dense_train = body("Train: 7B params, 1T tokens", x=440, y=300, color=RED, size=38)
        dense_inf = body("Inference: 7B active per token", x=440, y=380, color=RED, size=38)

        # Arrow
        arr_quant = arrow(700, 280, 880, 280, color=GRAY, width=6)

        # MoE model
        moe_quant_box = rrect(cx=1320, cy=280, w=480, h=280,
                            fill=PASTEL_GREEN, border=GREEN, opacity=0.2)
        moe_quant_lbl = label("MoE (8×7B)", x=1320, y=180, color=GREEN, size=46)
        moe_train = body("Train: 56B params, 1T tokens", x=1320, y=300, color=GREEN, size=38)
        moe_inf = body("Inference: 14B active per token", x=1320, y=380, color=GREEN, size=38)

        # Result
        result_box = rrect(cx=880, cy=530, w=1120, h=150,
                          fill=PASTEL_ORANGE, border=ORANGE, opacity=0.3)
        result_lbl = body(
            "Result: Quality of 56B model with inference speed of 14B model",
            y=530, color=ORANGE, size=38)

        advantage = body(
            "MoE Advantage: Better pretraining efficiency + competitive inference speed",
            y=720, color=BLUE, size=40)

        anim(quant_title, t=t + 0.3, dur=1.0)
        anim(dense_quant_box, t=t + 1.2, dur=0.8)
        anim(dense_quant_lbl, t=t + 1.5, dur=0.6)
        anim(dense_train, t=t + 2.0, dur=0.6)
        anim(dense_inf, t=t + 2.5, dur=0.6)
        anim(arr_quant, t=t + 3.0, dur=0.5)
        anim(moe_quant_box, t=t + 3.5, dur=0.8)
        anim(moe_quant_lbl, t=t + 3.8, dur=0.6)
        anim(moe_train, t=t + 4.3, dur=0.6)
        anim(moe_inf, t=t + 4.8, dur=0.6)
        anim(result_box, t=t + 5.5, dur=0.8)
        anim(result_lbl, t=t + 5.8, dur=1.0)
        anim(advantage, t=t + 7.0, dur=1.2)

        quant_items = [quant_title, result_box, result_lbl, advantage,
                      dense_quant_box, dense_quant_lbl, dense_train, dense_inf,
                      moe_quant_box, moe_quant_lbl, moe_train, moe_inf,
                      arr_quant]

        # ══════════════════════════════════════════════════════════════════════
        # §18  TRADE-OFFS
        # ══════════════════════════════════════════════════════════════════════
        t = bm["tradeoffs"]
        erase(quant_items, t=t - 1.0)

        trade_title = title("Trade-offs: When to Use MoE", y=80, color=ORANGE)

        # Trade-offs
        trade_cons = [
            ("Memory Requirements", "All experts loaded\nHundreds of GB VRAM", PASTEL_RED, RED, 380, 280),
            ("Implementation Complexity", "Routing, load balancing\nDistributed training", PASTEL_RED, RED, 920, 280),
            ("Fine-tuning Challenges", "Harder to fine-tune\nRisk of overfitting", PASTEL_RED, RED, 1460, 280),
            ("Communication Overhead", "Routing tokens across devices\nAdds latency", PASTEL_RED, RED, 640, 500),
        ]

        con_boxes, con_lbls, con_descs = [], [], []
        for name, desc, fill, border, cx, cy in trade_cons:
            cb = rrect(cx=cx, cy=cy, w=360, h=150,
                      fill=fill, border=border, opacity=0.3)
            cl = label(name, x=cx, y=cy - 30, color=border, size=36)
            cd = body(desc, x=cx, y=cy + 30, color=border, size=30, align="center")
            con_boxes.append(cb)
            con_lbls.append(cl)
            con_descs.append(cd)

        # When to use
        use_title = body("When to Use MoE:", y=700, color=GREEN, size=38)
        use_pts = bullets([
            "Large compute budget for pretraining",
            "Can afford memory requirements",
            "Want faster inference",
            "Large-scale models where efficiency gains outweigh complexity",
        ], x=280, y0=780, dy=75, color=GREEN, size=32)

        stick_dense = body("Stick with dense for: smaller scales, simpler deployments, memory-constrained environments",
                          y=1020, color=DARK_GRAY, size=30)

        anim(trade_title, t=t + 0.3, dur=1.0)
        for i in range(4):
            anim(con_boxes[i], t=t + 1.2 + i*0.5, dur=0.6)
            anim(con_lbls[i], t=t + 1.5 + i*0.5, dur=0.4)
            anim(con_descs[i], t=t + 1.8 + i*0.5, dur=0.6)
        anim(use_title, t=t + 4.0, dur=0.8)
        for i, up in enumerate(use_pts):
            anim(up, t=t + 5.0 + i*0.6, dur=0.6)
        anim(stick_dense, t=t + 8.5, dur=1.0)

        trade_items = [trade_title, use_title, stick_dense] + \
                      con_boxes + con_lbls + con_descs + use_pts

        # ══════════════════════════════════════════════════════════════════════
        # §19  SUMMARY
        # ══════════════════════════════════════════════════════════════════════
        t = bm["summary"]
        erase(trade_items, t=t - 1.0)

        sum_title = title("Summary: MoE Cheat Sheet", y=80, color=BLUE)

        summary_pts = bullets([
            "MoE = Mixture of Experts: sparse activation instead of dense",
            "Replaces dense FFN with multiple expert networks + router",
            "Router selects top-k experts per token (conditional computation)",
            "Sparsity enables more total parameters with same compute",
            "Load balancing: auxiliary loss, noisy gating, expert capacity",
            "Switch Transformer: simplified top-1 routing + z-loss",
            "Expert Choice: experts bid on tokens (better load balancing)",
            "Real-world: Mixtral, DeepSeek-V3, likely GPT-4, DBRX",
            "Trade-off: higher memory + complexity for better efficiency",
        ], x=200, y0=180, dy=85, color=BLACK, size=40)

        final_note = body(
            "Key insight: Scale intelligence without scaling compute linearly",
            y=960, color=ORANGE, size=40)

        anim(sum_title, t=t + 0.3, dur=1.0)
        for i, sp in enumerate(summary_pts):
            anim(sp, t=t + 1.2 + i*0.5, dur=0.6)
        anim(final_note, t=t + 7.0, dur=1.2)

        sum_items = [sum_title, final_note] + summary_pts

        # ══════════════════════════════════════════════════════════════════════
        # §20  OUTRO
        # ══════════════════════════════════════════════════════════════════════
        t = bm["outro"]
        erase(sum_items, t=t - 1.0)

        outro_title = title("Thanks for Watching!", y=350, color=BLUE, size=84)
        outro_sub = body("If this helped you understand MoE, please like and subscribe",
                         y=520, color=DARK_GRAY, size=44)
        outro_ask = body("Comment: Switch Transformer, Expert Choice, or other?",
                         y=640, color=ORANGE, size=40)
        outro_follow = body("I'll make a follow-up on the most requested topic",
                            y=760, color=GREEN, size=36)
        outro_final = body("See you in the next one!", y=880, color=BLUE, size=42)

        anim(outro_title, t=t + 0.3, dur=1.5)
        anim(outro_sub, t=t + 2.0, dur=1.0)
        anim(outro_ask, t=t + 3.5, dur=1.0)
        anim(outro_follow, t=t + 5.0, dur=1.0)
        anim(outro_final, t=t + 6.5, dur=1.0)

        outro_items = [outro_title, outro_sub, outro_ask, outro_follow, outro_final]

        return trk.duration

# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    output_dir = Path("output")
    audio_path = output_dir / "moe_explained_audio.mp3"
    video_path = output_dir / "moe_explained_video.mp4"
    
    # Generate audio
    asyncio.run(synthesize(audio_path))
    
    # Build scene
    build_scene(str(audio_path))
    
    # Render video
    scene.render(str(video_path))
    
    print(f"Video saved to {video_path}")
