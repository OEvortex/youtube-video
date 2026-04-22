"""
Multi-Head Latent Attention — Complete YouTube Explainer
=========================================================
Beginner-to-advanced whiteboard animation.

Sections
--------
 0. Cold Open / Hook
 1. Title Card
 2. Intro — What is MLA & why care?
 3. Transformer Primer — tokens, embeddings, attention heads (beginner)
 4. Standard Multi-Head Attention — full walkthrough with toy example
 5. The KV-Cache — what it is and why it explodes
 6. Existing Solutions — MQA and GQA explained
 7. The Core Idea of MLA — latent compression analogy
 8. Low-Rank Math — visual intuition (beginner-friendly)
 9. MLA Architecture — step-by-step diagram
10. MLA Equations — full mathematical treatment
11. Absorption / Pre-compute Trick
12. Memory Savings — side-by-side comparison bar chart
13. Quality Comparison — ablation results visualised
14. Inference Walkthrough — token-by-token animation
15. Post-Training Conversion (TransMLA)
16. Real-World Models using MLA
17. Trade-offs & When to Use MLA
18. Summary Cheat-Sheet
19. Outro / Call-to-Action
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
    PASTEL_RED, PASTEL_PURPLE, PASTEL_YELLOW,
)

# ── Canvas ────────────────────────────────────────────────────────────────────
WIDTH  = 1920
HEIGHT = 1080
FPS    = 24

# ── Voice ─────────────────────────────────────────────────────────────────────
VOICE        = "en-US-GuyNeural"
VOICE_RATE   = "+2%"
VOICE_VOLUME = 1.25
FONT_NAME    = "feasibly"

# ── Style constants ────────────────────────────────────────────────────────────
BG     = WHITE
SKETCH = SketchStyle(roughness=1.1, bowing=0.8, disable_font_mixture=True)
STK    = StrokeStyle(color=BLACK, width=3.0)
STK4   = StrokeStyle(color=BLACK, width=4.0)
STK6   = StrokeStyle(color=BLACK, width=6.0)

# ── Narration ─────────────────────────────────────────────────────────────────
NARRATION = """
<bookmark mark='cold_open'/>
What if I told you there's a single mathematical trick — borrowed from image compression — \
that lets the world's most powerful AI models run on a fraction of the memory they normally need, \
without losing any intelligence? That trick is called Multi-Head Latent Attention, or MLA. \
And by the end of this video, you'll understand it deeply — from the intuition a beginner can grasp \
all the way to the equations a researcher would write.

<bookmark mark='title'/>
Welcome. Today we are going to master Multi-Head Latent Attention.

<bookmark mark='intro'/>
Let me first tell you why you should care. DeepSeek — one of the most talked-about AI labs on the planet — \
uses MLA as the central innovation in their V2 and V3 models. \
Kimi K2, GLM-5, Mistral 3 Large, and Sarvam 105B have all adopted it. \
When you see MLA in an architecture card, it means the engineers cared deeply about making inference efficient \
without sacrificing model quality. So understanding MLA tells you something important about how frontier AI works.

<bookmark mark='transformer_primer'/>
Before we get to MLA, let's do a quick refresher on how transformers work — don't worry, we'll keep it beginner-friendly. \
A transformer takes a sequence of tokens — think of tokens as word-pieces, like "multi", "head", "latent" — \
and converts each token into a vector of numbers called an embedding. \
These embeddings flow into attention layers, where every token can look at every other token \
and decide: how much should I pay attention to you?

<bookmark mark='attention_heads'/>
Standard attention uses something called multi-head attention. \
Instead of doing this looking-around once, the model does it in parallel many times, \
each time with a slightly different "lens". Each lens is called an attention head. \
For each head, we compute three things: a Query, a Key, and a Value. \
The Query asks a question. The Keys are like labels on every token. \
The Values hold the actual information. \
Attention scores are computed by matching Queries to Keys, and then used to mix up the Values.

<bookmark mark='kv_cache_what'/>
Now here is the critical performance insight. During text generation, \
the model produces one token at a time. For each new token, \
it needs the Keys and Values of every previously generated token. \
Re-computing all those Keys and Values from scratch every step would be incredibly wasteful. \
So instead, we cache them. This is the KV-cache: a memory region that stores Keys and Values \
for all past tokens so we can reuse them.

<bookmark mark='kv_cache_problem'/>
But here is the catch. As you generate more and more tokens, \
the KV-cache keeps growing. For a standard model with many attention heads, \
the cache size equals: number of layers, times number of heads, times sequence length, \
times the head dimension, times two for K and V, times the bytes per number. \
At 128-thousand tokens with a large model, you can easily hit 40 to 80 gigabytes — \
just for the cache! That eats up your entire GPU memory budget, \
and performance collapses as the system starts swapping to slower memory.

<bookmark mark='mqa_gqa'/>
Researchers noticed this problem and came up with partial solutions. \
Multi-Query Attention, or MQA, uses just one shared Key-Value head for all query heads. \
This cuts the cache dramatically, but hurts quality noticeably. \
Then Grouped-Query Attention, or GQA — used in Llama, Mistral, and many others — \
found a middle ground: group the query heads into small clusters, \
and share one Key-Value pair per cluster. \
GQA saves significant memory and is the current industry standard. \
But it explicitly trades quality for memory. \
The bigger the groups, the more you lose. DeepSeek wanted a better deal.

<bookmark mark='mla_analogy'/>
Here is the key insight behind MLA. Think of it like image compression. \
When you save a photo as a JPEG, you don't store every pixel in full detail. \
Instead, you compress the image into a much smaller representation — \
the compressed bytes — and when you want to view the photo, \
you decompress it back to full quality. \
MLA does something remarkably similar with Key-Value pairs. \
Instead of storing full Keys and Values for every token, \
MLA compresses them into a tiny latent vector — just like a JPEG thumbnail — \
and stores that instead. When attention is needed, it reconstructs the full Keys and Values \
from those tiny latent vectors. Same information, far less storage.

<bookmark mark='low_rank_intuition'/>
The mathematics behind this compression is called low-rank approximation. \
Let me give you the intuition. Imagine a giant spreadsheet with one-thousand rows and one-thousand columns. \
That's one million numbers to store. \
Now imagine that the rows are not all unique — \
they share patterns. Maybe most rows are combinations of just ten basic row types. \
If that's true, you could represent the entire spreadsheet with just two smaller tables: \
one table of ten basic row patterns, and one table saying how to mix those patterns for each row. \
That's ten times one-thousand plus ten times one-thousand — just twenty-thousand numbers — \
fifty times smaller! This is low-rank approximation. \
The "rank" is the number of basic patterns — ten in our example. \
If the rank is much smaller than the matrix dimensions, you get massive compression.

<bookmark mark='low_rank_math'/>
Formally, a matrix M with n rows and m columns can be approximated as the product U times V, \
where U has n rows and r columns, and V has r rows and m columns. \
The number r is called the rank, or latent dimension. \
When r is much smaller than n and m, the storage drops from n times m \
down to r times open-parenthesis n plus m close-parenthesis — a huge saving. \
You might recognise this from LoRA — Low-Rank Adaptation — which uses exactly the same idea \
to fine-tune large language models with very few extra parameters.

<bookmark mark='mla_architecture'/>
So how does MLA apply this to attention? Let me walk you through the architecture step by step. \
In standard multi-head attention, the input vector X is projected directly \
into Queries Q, Keys K, and Values V using three large matrices. \
MLA replaces these direct projections with a two-stage process.

<bookmark mark='mla_step1'/>
Step one: Compression. \
The input X is multiplied by a small compression matrix W-KV-down, \
producing a latent vector c-KV. This latent vector has dimension r, \
which is much smaller than the full model dimension d. \
This latent vector c-KV is what gets stored in the KV-cache — not the full Keys and Values. \
One small vector per token instead of two large ones.

<bookmark mark='mla_step2'/>
Step two: Decompression. \
When we need to compute attention, we take the stored latent vector c-KV \
and multiply it by two decompression matrices — W-K-up and W-V-up — \
to recover approximate Keys and Values for each head. \
Each attention head has its own decompression matrices, \
so different heads can extract different information from the same compressed latent.

<bookmark mark='mla_query'/>
The Query side gets similar treatment. \
The input X is compressed into a query latent c-Q, \
which is then decompressed into the actual Query Q for each head. \
This reduces computation during the forward pass as well.

<bookmark mark='mla_equations'/>
Let's write the equations precisely. \
The KV latent is: c-KV equals X times W-KV-down. \
Keys are reconstructed as: K-h equals c-KV times W-K-up-h. \
Values are reconstructed as: V-h equals c-KV times W-V-up-h. \
Queries are: Q-h equals X times W-Q-down times W-Q-up-h. \
The attention output for head h is: softmax of Q-h times K-h-transpose \
divided by square-root of d-head, multiplied by V-h. \
All heads are concatenated and projected by an output matrix W-O.

<bookmark mark='absorption_trick'/>
Now here is an elegant optimization called the absorption trick. \
Notice that Keys are c-KV times W-K-up-h, and Queries are c-Q times W-Q-up-h. \
When we compute the attention score Q times K-transpose, we get: \
c-Q times W-Q-up-h times W-K-up-h-transpose times c-KV-transpose. \
The middle part — W-Q-up-h times W-K-up-h-transpose — does not depend on the input at all! \
We can pre-compute this product once for each head and store it as W-QK-h. \
This saves a matrix multiplication at inference time on every single forward pass. \
This is called weight absorption — folding weight matrices into each other.

<bookmark mark='memory_savings'/>
Let's quantify the memory savings concretely. \
In standard Multi-Head Attention with H heads, head dimension d-h, and sequence length L: \
KV-cache size equals L times H times 2 times d-h. \
In MLA, we store only the latent c-KV of dimension r: \
KV-cache size equals L times r. \
DeepSeek-V2 uses r equal to 512 while d equals 5120 and H equals 128. \
The full-size KV would be 128 times 2 times 64 equals 16384 per token. \
MLA stores only 512 — a compression ratio of over 32 times! \
At 128-thousand tokens, this is the difference between 26 gigabytes and under one gigabyte.

<bookmark mark='quality_comparison'/>
But does this compression hurt quality? \
DeepSeek ran careful ablation studies comparing MHA, GQA, and MLA \
across identical training runs. \
MLA matched or slightly exceeded MHA quality on nearly every benchmark. \
GQA with equivalent memory savings showed noticeable degradation. \
The reason MLA can do this is that the compression matrix is shared across all heads, \
so it learns a universal compressed representation of the sequence context, \
which each head then specialises from. This is strictly more expressive than GQA, \
where heads are simply grouped together with no learned compression.

<bookmark mark='inference_walkthrough'/>
Let me walk you through exactly what happens token by token during inference. \
When token number one is processed, we compute its KV latent c-KV-1 \
and store it in the cache. \
When token two comes in, we compute c-KV-2 and append it to the cache. \
Now when computing attention for token two, \
we decompress both c-KV-1 and c-KV-2 on the fly into Keys and Values, \
run attention, and produce the output. \
The cache grows by exactly r numbers per new token, \
regardless of how many attention heads the model has. \
This makes MLA cache growth dramatically slower than standard attention.

<bookmark mark='rope_note'/>
A quick technical note on positional encodings. \
MLA uses Rotary Positional Embeddings, or RoPE, but applies them in a special way. \
Because the Keys are reconstructed from the latent, \
we can't apply RoPE inside the compressed representation — \
it would break the weight absorption trick. \
So DeepSeek's implementation decouples the position information: \
a small additional key component carries the RoPE encoding separately, \
and is concatenated to the main key before attention. \
This keeps the absorption trick intact while preserving positional information.

<bookmark mark='transmla'/>
Here is exciting news: you don't have to train a model from scratch to get MLA's benefits. \
The TransMLA framework, published alongside DeepSeek-V2, \
shows that any model trained with standard GQA can be converted to MLA \
by factorising the projection matrices after training. \
The conversion finds the best low-rank factorisation of the existing weight matrices \
using singular value decomposition. \
After a short fine-tuning step, the converted model matches the original quality \
while gaining MLA's memory efficiency. \
This means Llama, Mistral, and other GQA-based models can be upgraded.

<bookmark mark='models_using_mla'/>
Let's survey the landscape of models that have adopted MLA. \
DeepSeek-V2 was the first to introduce MLA at scale in 2024, \
proving that a mixture-of-experts model could be both efficient and powerful. \
DeepSeek-V3 refined the implementation and achieved state-of-the-art results \
on coding and reasoning benchmarks while fitting in a dramatically smaller memory footprint. \
Kimi K2 from Moonshot AI uses MLA paired with linear attention for extreme efficiency. \
GLM-5 from Tsinghua uses MLA in their dense model architecture. \
Mistral 3 Large adopted MLA for their flagship model. \
Sarvam 105B is a large multilingual model using MLA for efficient serving.

<bookmark mark='tradeoffs'/>
MLA is not a free lunch, and I want to be honest about the trade-offs. \
First: implementation complexity. \
Standard attention is a clean, simple operation. \
MLA adds compression, decompression, and the RoPE decoupling — \
roughly three times more code to get right. \
Second: the absorption trick requires careful bookkeeping. \
The pre-computed matrices must be correctly shaped and indexed. \
Third: latency. Decompressing the latent at every attention step adds a small compute cost. \
For very short sequences, this overhead may not be worth the memory saving. \
MLA shines when sequence length is long and memory is the bottleneck.

<bookmark mark='when_to_use'/>
When should you choose MLA? \
Use MLA when you are serving very long sequences — \
code generation, document understanding, long-form reasoning. \
Use MLA when GPU memory is your binding constraint at inference time. \
Use MLA when you need MHA-level quality but GQA-level memory. \
Stick with GQA when simplicity matters more than peak efficiency, \
or when your sequences are short enough that the KV-cache is not the bottleneck.

<bookmark mark='summary'/>
Let's bring it all together with a summary. \
MLA stands for Multi-Head Latent Attention. \
It solves the KV-cache memory explosion by compressing Keys and Values \
into a tiny latent vector using low-rank matrix factorisation. \
The latent vector — not the full Keys and Values — is what gets stored in the cache. \
At inference time, the Keys and Values are reconstructed from the latent on demand. \
The weight absorption trick allows pre-computing part of the attention matrix, \
speeding up inference further. \
Compared to GQA, MLA achieves higher compression with no quality loss. \
It is used in DeepSeek, Kimi, GLM-5, Mistral, and Sarvam, \
and can be retrofitted onto existing GQA models via TransMLA.

<bookmark mark='outro'/>
If this video helped you understand MLA, please hit like and subscribe — \
it helps more people find this content. \
Drop a comment below: which part was hardest to understand? \
I'll make a follow-up video on whichever topic gets the most requests. \
<bookmark mark='final'/> Thanks for watching. See you in the next one.
"""

BOOKMARK_RE = re.compile(r"<bookmark\s+mark\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

# ── Scene helpers ──────────────────────────────────────────────────────────────

scene = Scene(width=WIDTH, height=HEIGHT, fps=FPS, background_color=BG)
scene.set_viewport_to_identity()

def title(text: str, *, y: float, color=BLACK, size: int = 88) -> Text:
    return Text(text, position=(960, y), font_size=size, font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=color, width=4.0), sketch_style=SKETCH)

def body(text: str, *, x: float = 960, y: float, color=BLACK,
         align: str = "center", size: int = 54) -> Text:
    return Text(text, position=(x, y), font_size=size, font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=color, width=3.2), sketch_style=SKETCH, align=align)

def label(text: str, *, x: float, y: float, color=BLACK, size: int = 44) -> Text:
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
            "transformer_primer", "attention_heads",
            "kv_cache_what", "kv_cache_problem",
            "mqa_gqa",
            "mla_analogy", "low_rank_intuition", "low_rank_math",
            "mla_architecture", "mla_step1", "mla_step2", "mla_query",
            "mla_equations", "absorption_trick",
            "memory_savings", "quality_comparison",
            "inference_walkthrough", "rope_note",
            "transmla", "models_using_mla",
            "tradeoffs", "when_to_use",
            "summary", "outro", "final",
        ]}

        # ══════════════════════════════════════════════════════════════════════
        # §0  COLD OPEN — hook question
        # ══════════════════════════════════════════════════════════════════════
        t = bm["cold_open"]

        hook_q = title("What if a single math trick\ncould halve your AI's memory?",
                        y=340, color=BLUE, size=96)
        hook_sub = body("(without losing any intelligence)", y=560, color=DARK_GRAY, size=64)
        hook_ans = body("→  Multi-Head Latent Attention  ←",
                        y=720, color=ORANGE, size=72)

        anim(hook_q,   t=t + 0.3, dur=1.8)
        anim(hook_sub, t=t + 2.2, dur=1.2)
        anim(hook_ans, t=t + 4.5, dur=1.5)

        cold_open_items = [hook_q, hook_sub, hook_ans]

        # ══════════════════════════════════════════════════════════════════════
        # §1  TITLE CARD
        # ══════════════════════════════════════════════════════════════════════
        t = bm["title"]
        erase(cold_open_items, t=t - 1.0)

        ttl   = title("Multi-Head Latent Attention", y=280, color=BLUE, size=100)
        ttl2  = title("(MLA)", y=400, color=BLUE, size=80)
        by_lbl = body("Beginner → Advanced Complete Guide", y=540, color=ORANGE, size=64)
        ds_box = rrect(cx=960, cy=720, w=700, h=110,
                       fill=PASTEL_BLUE, border=BLUE, opacity=0.25)
        ds_lbl = body("As used in DeepSeek · Kimi · Mistral · GLM-5",
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

        why_title = title("Why Does MLA Matter?", y=130, color=BLACK)
        why_pts = bullets([
            "DeepSeek-V2 & V3 built on MLA — frontier results at lower cost",
            "Kimi K2, GLM-5, Mistral 3 Large, Sarvam 105B all adopted it",
            "Enables running massive models on fewer GPUs",
            "Solves a fundamental bottleneck every LLM deployment hits",
        ], x=220, y0=280, dy=130, color=BLACK, size=52)

        anim(why_title, t=t + 0.5, dur=1.0)
        for i, b in enumerate(why_pts):
            anim(b, t=t + 1.5 + i * 1.8, dur=1.2)

        intro_items = [why_title] + why_pts

        # ══════════════════════════════════════════════════════════════════════
        # §3  TRANSFORMER PRIMER — tokens & embeddings
        # ══════════════════════════════════════════════════════════════════════
        t = bm["transformer_primer"]
        erase(intro_items, t=t - 1.0)

        prim_title = title("Quick Refresher: How Transformers Work", y=100, color=PURPLE)

        # Token pipeline: text → tokens → embeddings → attention
        tok_labels = ["\"Multi\"", "\"Head\"", "\"Latent\"", "\"Attention\""]
        tok_boxes, tok_txts = [], []
        for i, tok in enumerate(tok_labels):
            bx = rrect(cx=180 + i * 420, cy=320, w=340, h=110,
                       fill=PASTEL_PURPLE, border=PURPLE, opacity=0.3)
            tx = label(tok, x=180 + i*420, y=320, color=PURPLE, size=44)
            tok_boxes.append(bx)
            tok_txts.append(tx)

        arr_tok2emb = arrow(1760, 320, 1860, 320, color=GRAY)  # out of frame, placeholder
        emb_lbl = body("↓ Embedding layer ↓", y=430, color=DARK_GRAY, size=44)

        # Embedding vectors (simplified as coloured rectangles)
        emb_rects, emb_txts = [], []
        for i in range(4):
            er = rrect(cx=180 + i*420, cy=580, w=80, h=200,
                       fill=PASTEL_GREEN, border=GREEN, opacity=0.5)
            et = label(f"v{i+1}", x=180 + i*420, y=580, color=GREEN, size=40)
            emb_rects.append(er)
            emb_txts.append(et)

        attn_box = rrect(cx=960, cy=850, w=1400, h=130,
                         fill=PASTEL_BLUE, border=BLUE, opacity=0.3)
        attn_lbl = body("Attention Layer  (tokens look at each other)", y=850, color=BLUE, size=52)

        # draw arrows from embeddings to attention
        emb_arrows = [arrow(180 + i*420, 690, 180 + i*420, 785, color=BLUE, width=4)
                      for i in range(4)]

        anim(prim_title, t=t + 0.5, dur=1.0)
        for i in range(4):
            anim(tok_boxes[i], t=t + 1.2 + i*0.4, dur=0.8)
            anim(tok_txts[i],  t=t + 1.5 + i*0.4, dur=0.6)
        anim(emb_lbl, t=t + 3.5, dur=0.8)
        for i in range(4):
            anim(emb_rects[i], t=t + 4.5 + i*0.3, dur=0.6)
            anim(emb_txts[i],  t=t + 4.7 + i*0.3, dur=0.4)
        for i in range(4):
            anim(emb_arrows[i], t=t + 6.5, dur=0.4)
        anim(attn_box, t=t + 7.0, dur=1.0)
        anim(attn_lbl, t=t + 7.3, dur=0.8)

        primer_items = [prim_title, emb_lbl, attn_box, attn_lbl] + \
                       tok_boxes + tok_txts + emb_rects + emb_txts + emb_arrows

        # ══════════════════════════════════════════════════════════════════════
        # §4  ATTENTION HEADS — Q K V explained
        # ══════════════════════════════════════════════════════════════════════
        t = bm["attention_heads"]
        erase(primer_items, t=t - 1.0)

        head_title = title("Multi-Head Attention: Q, K, V", y=100, color=BLUE)

        # Central token node
        tok_circ = Circle(center=(960, 380), radius=80,
                          stroke_style=StrokeStyle(color=BLUE, width=5),
                          fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.5),
                          sketch_style=SKETCH)
        tok_lbl = label("Token\n(embedding)", x=960, y=380, color=BLUE, size=40)

        # Q K V boxes
        q_box = rrect(cx=480,  cy=680, w=280, h=110, fill=PASTEL_BLUE,   border=BLUE)
        k_box = rrect(cx=960,  cy=680, w=280, h=110, fill=PASTEL_RED,    border=RED)
        v_box = rrect(cx=1440, cy=680, w=280, h=110, fill=PASTEL_GREEN,  border=GREEN)
        q_lbl = label("Query (Q)\nWhat am I\nlooking for?", x=480,  y=680, color=BLUE,  size=38)
        k_lbl = label("Key (K)\nWhat do I\noffer?",        x=960,  y=680, color=RED,   size=38)
        v_lbl = label("Value (V)\nActual\ninformation",    x=1440, y=680, color=GREEN, size=38)

        q_arr = arrow(960, 460, 540,  620, color=BLUE,  width=4)
        k_arr = arrow(960, 460, 960,  625, color=RED,   width=4)
        v_arr = arrow(960, 460, 1400, 620, color=GREEN, width=4)

        score_lbl = body("Score = softmax(Q · Kᵀ / √d)  →  weights for mixing V",
                         y=860, color=BLACK, size=52)

        # Multiple heads annotation
        heads_box = rrect(cx=960, cy=980, w=1500, h=80,
                          fill=PASTEL_YELLOW, border=ORANGE, opacity=0.4)
        heads_note = body("This whole process is repeated H times in parallel (H attention heads)",
                          y=980, color=ORANGE, size=42)

        anim(head_title, t=t + 0.4, dur=1.0)
        anim(tok_circ,   t=t + 1.2, dur=1.0)
        anim(tok_lbl,    t=t + 1.5, dur=0.8)
        anim(q_arr,  t=t + 2.5, dur=0.6)
        anim(k_arr,  t=t + 2.8, dur=0.6)
        anim(v_arr,  t=t + 3.1, dur=0.6)
        anim(q_box,  t=t + 3.5, dur=0.8)
        anim(k_box,  t=t + 3.7, dur=0.8)
        anim(v_box,  t=t + 3.9, dur=0.8)
        anim(q_lbl,  t=t + 4.0, dur=0.6)
        anim(k_lbl,  t=t + 4.2, dur=0.6)
        anim(v_lbl,  t=t + 4.4, dur=0.6)
        anim(score_lbl, t=t + 6.0, dur=1.5)
        anim(heads_box,  t=t + 9.0, dur=1.0)
        anim(heads_note, t=t + 9.3, dur=1.0)

        heads_items = [head_title, tok_circ, tok_lbl,
                       q_box, k_box, v_box, q_lbl, k_lbl, v_lbl,
                       q_arr, k_arr, v_arr, score_lbl, heads_box, heads_note]

        # ══════════════════════════════════════════════════════════════════════
        # §5  KV-CACHE — what it is
        # ══════════════════════════════════════════════════════════════════════
        t = bm["kv_cache_what"]
        erase(heads_items, t=t - 1.0)

        kvc_title = title("The KV-Cache: What & Why", y=100, color=DARK_GRAY)

        # Timeline of token generation
        step_labels = ["Token 1", "Token 2", "Token 3", "Token N"]
        step_xs = [260, 720, 1180, 1640]
        step_boxes, step_txts, step_caches = [], [], []
        for i, (lbl_t, sx) in enumerate(zip(step_labels, step_xs)):
            sb = rrect(cx=sx, cy=280, w=320, h=100,
                       fill=PASTEL_BLUE, border=BLUE, opacity=0.4)
            st = label(lbl_t, x=sx, y=280, color=BLUE, size=44)
            # cache stack grows
            for j in range(i+1):
                sc = rrect(cx=sx, cy=480 + j*70, w=260, h=56,
                           fill=PASTEL_RED if j%2==0 else PASTEL_GREEN,
                           border=RED if j%2==0 else GREEN, opacity=0.55)
                step_caches.append(sc)
            step_boxes.append(sb)
            step_txts.append(st)

        cache_title = body("KV Cache grows one row per token →", y=430, color=RED, size=48)
        cache_note  = body("Re-using stored K, V avoids recomputing them from scratch each step.",
                           y=800, color=DARK_GRAY, size=48)

        arr_gen1 = arrow(420, 280, 565,  280, color=GRAY, width=4)
        arr_gen2 = arrow(880, 280, 1025, 280, color=GRAY, width=4)
        arr_gen3 = arrow(1340,280, 1485, 280, color=GRAY, width=4)

        anim(kvc_title, t=t + 0.4, dur=1.0)
        for i in range(4):
            anim(step_boxes[i], t=t + 1.5 + i*1.5, dur=0.8)
            anim(step_txts[i],  t=t + 1.7 + i*1.5, dur=0.6)
        anim(arr_gen1, t=t + 2.5, dur=0.4)
        anim(arr_gen2, t=t + 4.0, dur=0.4)
        anim(arr_gen3, t=t + 5.5, dur=0.4)
        anim(cache_title, t=t + 3.0, dur=1.0)
        for i, sc in enumerate(step_caches):
            anim(sc, t=t + 2.0 + i*0.4, dur=0.5)
        anim(cache_note, t=t + 10.0, dur=1.5)

        kvc_what_items = [kvc_title, cache_title, cache_note,
                          arr_gen1, arr_gen2, arr_gen3] + \
                         step_boxes + step_txts + step_caches

        # ══════════════════════════════════════════════════════════════════════
        # §6  KV-CACHE PROBLEM — size explosion
        # ══════════════════════════════════════════════════════════════════════
        t = bm["kv_cache_problem"]
        erase(kvc_what_items, t=t - 1.0)

        prob_title = title("The KV-Cache Memory Explosion 💥", y=100, color=RED)

        formula = Math(
            r"\text{KV size} = L \times H \times 2 \times d_h \times \text{bytes}",
            position=(960, 260), font_size=72,
            stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)

        # Worked example
        ex_box = rrect(cx=960, cy=460, w=1500, h=180,
                       fill=PASTEL_ORANGE, border=ORANGE, opacity=0.25)
        ex_txt = body(
            "Example: L=128k  H=128  dₕ=64  bfloat16 (2 bytes)\n"
            "→  128,000 × 128 × 2 × 64 × 2  =  ~42 GB  just for cache!",
            y=460, color=ORANGE, size=46)

        # Bar showing memory usage
        bar_bg   = rrect(cx=960, cy=720, w=1600, h=80, fill=LIGHT_GRAY, border=GRAY,
                         opacity=0.4, border_width=2)
        bar_fill = rrect(cx=460, cy=720, w=800, h=60, fill=PASTEL_RED, border=RED,
                         opacity=0.8, border_width=2)
        bar_lbl  = label("42 GB KV-Cache", x=460, y=720, color=RED, size=40)
        gpu_lbl  = body("← Entire 80 GB GPU VRAM →", y=800, color=DARK_GRAY, size=44)

        consequence = body(
            "Performance collapses → data swaps to slow CPU RAM → inference grinds to a halt.",
            y=940, color=RED, size=50)

        anim(prob_title, t=t + 0.4, dur=1.0)
        anim(formula,    t=t + 1.5, dur=2.0)
        anim(ex_box,     t=t + 4.0, dur=1.0)
        anim(ex_txt,     t=t + 4.3, dur=1.5)
        anim(bar_bg,     t=t + 7.0, dur=0.6)
        anim(bar_fill,   t=t + 7.5, dur=1.2)
        anim(bar_lbl,    t=t + 8.8, dur=0.8)
        anim(gpu_lbl,    t=t + 9.5, dur=0.8)
        anim(consequence,t=t + 11.0, dur=1.5)

        prob_items = [prob_title, formula, ex_box, ex_txt,
                      bar_bg, bar_fill, bar_lbl, gpu_lbl, consequence]

        # ══════════════════════════════════════════════════════════════════════
        # §7  MQA & GQA
        # ══════════════════════════════════════════════════════════════════════
        t = bm["mqa_gqa"]
        erase(prob_items, t=t - 1.0)

        gqa_title = title("Prior Solutions: MQA and GQA", y=100, color=ORANGE)

        # Three panels: MHA / GQA / MQA
        panel_data = [
            ("MHA\n(Standard)",  200,  PASTEL_BLUE,  BLUE,   "H KV heads\nMax memory\nMax quality"),
            ("GQA\n(Grouped)",   760,  PASTEL_ORANGE,ORANGE, "H/G KV heads\nReduced mem\nSlightly lower quality"),
            ("MQA\n(Multi-Query)",1320, PASTEL_RED,   RED,    "1 KV head\nMin memory\nNotable quality loss"),
        ]
        panels, panel_lbls, panel_descs = [], [], []
        for pname, px, pfill, pborder, pdesc in panel_data:
            pb = rrect(cx=px, cy=420, w=440, h=580,
                       fill=pfill, border=pborder, opacity=0.25)
            pl = label(pname, x=px, y=260, color=pborder, size=52)
            pd = body(pdesc, x=px, y=470, color=pborder, size=40)
            panels.append(pb)
            panel_lbls.append(pl)
            panel_descs.append(pd)

            # Draw heads (circles)
            if "MHA" in pname:
                num_heads = 4
            elif "GQA" in pname:
                num_heads = 2
            else:
                num_heads = 1
            for h in range(num_heads):
                cx2 = px - (num_heads-1)*45 + h*90
                qc = Circle(center=(cx2, 640), radius=30,
                            stroke_style=StrokeStyle(color=BLUE, width=3),
                            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.7),
                            sketch_style=SKETCH)
                panels.append(qc)

        verdict = body("GQA = industry standard but sacrifices quality for memory.",
                       y=930, color=RED, size=52)
        want    = body("DeepSeek wanted: same memory savings AND same quality → MLA",
                       y=1010, color=GREEN, size=50)

        anim(gqa_title, t=t + 0.4, dur=1.0)
        for i in range(3):
            anim(panels[i],      t=t + 1.5 + i*1.2, dur=1.0)
            anim(panel_lbls[i],  t=t + 1.8 + i*1.2, dur=0.8)
            anim(panel_descs[i], t=t + 2.2 + i*1.2, dur=0.8)
        for i in range(3, len(panels)):
            anim(panels[i], t=t + 5.5, dur=0.4)
        anim(verdict, t=t + 8.0, dur=1.2)
        anim(want,    t=t + 9.5, dur=1.2)

        gqa_items = [gqa_title, verdict, want] + panels + panel_lbls + panel_descs

        # ══════════════════════════════════════════════════════════════════════
        # §8  MLA ANALOGY — JPEG compression
        # ══════════════════════════════════════════════════════════════════════
        t = bm["mla_analogy"]
        erase(gqa_items, t=t - 1.0)

        ana_title = title("The Big Idea: Think of JPEG Compression", y=100, color=BLUE)

        # Left: "full image" many small squares
        full_img_lbl = body("Full K, V per token\n(expensive to store)", x=380, y=230,
                            color=RED, size=46)
        squares = []
        for row in range(6):
            for col in range(6):
                sq = rrect(cx=170 + col*75, cy=380 + row*75, w=62, h=62,
                           fill=PASTEL_RED, border=RED, opacity=0.55,
                           border_width=2)
                squares.append(sq)
        full_size = label("6×6 = 36 values", x=380, y=870, color=RED, size=44)

        # Arrow
        compress_arrow = arrow(640, 540, 850, 540, color=PURPLE, width=7)
        compress_lbl   = label("Compress\n(W_down)", x=745, y=490, color=PURPLE, size=40)

        # Middle: tiny latent
        lat_lbl = body("Latent c_KV\n(tiny, cached!)", x=960, y=230, color=ORANGE, size=46)
        lat_squares = []
        for row in range(2):
            for col in range(2):
                lsq = rrect(cx=900 + col*90, cy=430 + row*90, w=75, h=75,
                            fill=PASTEL_YELLOW, border=ORANGE, opacity=0.8,
                            border_width=3)
                lat_squares.append(lsq)
        lat_size = label("2×2 = 4 values\n(8× smaller!)", x=960, y=640, color=ORANGE, size=44)

        # Arrow
        decompress_arrow = arrow(1080, 540, 1290, 540, color=GREEN, width=7)
        decompress_lbl   = label("Decompress\n(W_up)", x=1185, y=490, color=GREEN, size=40)

        # Right: reconstructed
        rec_lbl = body("Reconstructed K, V\n(approx. original)", x=1560, y=230,
                       color=GREEN, size=46)
        rec_squares = []
        for row in range(6):
            for col in range(6):
                rsq = rrect(cx=1350 + col*75, cy=380 + row*75, w=62, h=62,
                            fill=PASTEL_GREEN, border=GREEN, opacity=0.5,
                            border_width=2)
                rec_squares.append(rsq)
        rec_size = label("6×6 ≈ original\n(good approx)", x=1560, y=870, color=GREEN, size=44)

        insight = body(
            "Store only the tiny latent in the KV-Cache. Reconstruct full K, V on demand.",
            y=980, color=BLUE, size=54)

        anim(ana_title,  t=t + 0.4, dur=1.0)
        anim(full_img_lbl, t=t + 1.2, dur=0.8)
        for i, sq in enumerate(squares):
            anim(sq, t=t + 1.5 + i*0.06, dur=0.3)
        anim(full_size, t=t + 5.5, dur=0.8)
        anim(compress_arrow, t=t + 6.0, dur=0.8)
        anim(compress_lbl,   t=t + 6.5, dur=0.6)
        anim(lat_lbl,    t=t + 7.0, dur=0.8)
        for i, lsq in enumerate(lat_squares):
            anim(lsq, t=t + 7.5 + i*0.2, dur=0.4)
        anim(lat_size, t=t + 9.0, dur=0.8)
        anim(decompress_arrow, t=t + 9.5, dur=0.8)
        anim(decompress_lbl,   t=t + 10.0, dur=0.6)
        anim(rec_lbl, t=t + 10.5, dur=0.8)
        for i, rsq in enumerate(rec_squares):
            anim(rsq, t=t + 11.0 + i*0.05, dur=0.25)
        anim(rec_size, t=t + 14.5, dur=0.8)
        anim(insight, t=t + 15.5, dur=1.5)

        analogy_items = ([ana_title, full_img_lbl, full_size,
                          compress_arrow, compress_lbl,
                          lat_lbl, lat_size,
                          decompress_arrow, decompress_lbl,
                          rec_lbl, rec_size, insight] +
                         squares + lat_squares + rec_squares)

        # ══════════════════════════════════════════════════════════════════════
        # §9  LOW-RANK INTUITION — spreadsheet analogy
        # ══════════════════════════════════════════════════════════════════════
        t = bm["low_rank_intuition"]
        erase(analogy_items, t=t - 1.0)

        lr_title = title("Low-Rank Approximation: The Intuition", y=100, color=PURPLE)

        # Big grid → sparse basis
        grid_lbl = body("Big matrix M  (1000 × 1000 = 1,000,000 numbers)", x=400, y=220,
                        color=BLACK, size=46)

        # Simplified grid (12×12 visual)
        grid_cells = []
        for row in range(8):
            for col in range(8):
                fill_c = PASTEL_PURPLE if (row + col) % 3 == 0 else (
                    PASTEL_BLUE if (row + col) % 3 == 1 else PASTEL_GREEN)
                gc = rrect(cx=120 + col*70, cy=360 + row*70, w=60, h=60,
                           fill=fill_c, border=GRAY, opacity=0.5, border_width=1)
                grid_cells.append(gc)

        approx_arrow = arrow(700, 540, 860, 540, color=ORANGE, width=6)
        approx_lbl   = label("≈", x=780, y=490, color=ORANGE, size=80)

        # U and V small matrices
        u_lbl_vis = body("U\n(1000×10)", x=980, y=380, color=PURPLE, size=44)
        u_cells = []
        for row in range(8):
            uc = rrect(cx=960, cy=310 + row*60, w=60, h=52,
                       fill=PASTEL_PURPLE, border=PURPLE, opacity=0.6, border_width=2)
            u_cells.append(uc)

        times_lbl = label("×", x=1110, y=450, color=BLACK, size=64)

        v_lbl_vis = body("V\n(10×1000)", x=1290, y=220, color=GREEN, size=44)
        v_cells = []
        for col in range(8):
            vc = rrect(cx=1180 + col*60, cy=450, w=52, h=60,
                       fill=PASTEL_GREEN, border=GREEN, opacity=0.6, border_width=2)
            v_cells.append(vc)

        saving = body(
            "Storage: 1,000,000  →  10×(1000+1000) = 20,000   (50× smaller!)",
            y=750, color=RED, size=48)
        rank_note = body(
            "'r = 10' is the rank — the number of basic patterns shared across rows.",
            y=860, color=PURPLE, size=46)
        lora_note = body(
            "LoRA uses exactly this trick for fine-tuning LLMs with few extra parameters.",
            y=970, color=DARK_GRAY, size=44)

        anim(lr_title, t=t + 0.4, dur=1.0)
        anim(grid_lbl, t=t + 1.2, dur=0.8)
        for i, gc in enumerate(grid_cells):
            anim(gc, t=t + 1.5 + i*0.05, dur=0.3)
        anim(approx_arrow, t=t + 6.0, dur=0.6)
        anim(approx_lbl,   t=t + 6.3, dur=0.4)
        for i, uc in enumerate(u_cells):
            anim(uc, t=t + 7.0 + i*0.1, dur=0.3)
        anim(u_lbl_vis, t=t + 8.2, dur=0.6)
        anim(times_lbl, t=t + 9.0, dur=0.4)
        for i, vc in enumerate(v_cells):
            anim(vc, t=t + 9.5 + i*0.1, dur=0.3)
        anim(v_lbl_vis, t=t + 10.5, dur=0.6)
        anim(saving,    t=t + 12.0, dur=1.2)
        anim(rank_note, t=t + 13.5, dur=1.0)
        anim(lora_note, t=t + 15.0, dur=1.0)

        lr_int_items = ([lr_title, grid_lbl, approx_arrow, approx_lbl,
                         u_lbl_vis, times_lbl, v_lbl_vis, saving, rank_note, lora_note] +
                        grid_cells + u_cells + v_cells)

        # ══════════════════════════════════════════════════════════════════════
        # §10  LOW-RANK MATH — formal definition
        # ══════════════════════════════════════════════════════════════════════
        t = bm["low_rank_math"]
        erase(lr_int_items, t=t - 1.0)

        lrm_title = title("Low-Rank Approximation: The Math", y=100, color=PURPLE)

        main_eq = Math(
            r"M_{n \times m} \approx U_{n \times r} \cdot V_{r \times m}",
            position=(960, 290), font_size=90,
            stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)

        # Visual rectangle dimensions
        m_rect  = rrect(cx=310, cy=530, w=300, h=250, fill=PASTEL_BLUE,   border=BLUE,   opacity=0.4)
        u_rect  = rrect(cx=750, cy=530, w=90,  h=250, fill=PASTEL_PURPLE, border=PURPLE, opacity=0.5)
        v_rect  = rrect(cx=1020,cy=530, w=300, h=90,  fill=PASTEL_GREEN,  border=GREEN,  opacity=0.5)
        eq_txt  = label("≈", x=560, y=530, color=BLACK, size=90)
        x_txt   = label("×", x=900, y=530, color=BLACK, size=64)
        m_ann   = label("n × m", x=310,  y=530, color=BLUE,   size=40)
        u_ann   = label("n×r",   x=750,  y=530, color=PURPLE, size=36)
        v_ann   = label("r × m", x=1020, y=530, color=GREEN,  size=36)

        r_note = body("r ≪ n, m  →  r is the latent rank  (small!)", y=730, color=RED, size=52)
        storage = body(
            "Storage: n·m  →  r·(n+m)     when r = 10, n = m = 1000: 1M → 20k (50×)",
            y=840, color=DARK_GRAY, size=46)

        anim(lrm_title, t=t + 0.4, dur=1.0)
        anim(main_eq,   t=t + 1.5, dur=2.0)
        anim(m_rect,    t=t + 4.0, dur=0.8)
        anim(eq_txt,    t=t + 4.5, dur=0.5)
        anim(u_rect,    t=t + 5.0, dur=0.8)
        anim(x_txt,     t=t + 5.5, dur=0.4)
        anim(v_rect,    t=t + 6.0, dur=0.8)
        anim(m_ann,     t=t + 7.0, dur=0.6)
        anim(u_ann,     t=t + 7.3, dur=0.6)
        anim(v_ann,     t=t + 7.6, dur=0.6)
        anim(r_note,    t=t + 9.0, dur=1.2)
        anim(storage,   t=t + 11.0, dur=1.5)

        lrm_items = [lrm_title, main_eq, m_rect, u_rect, v_rect,
                     eq_txt, x_txt, m_ann, u_ann, v_ann, r_note, storage]

        # ══════════════════════════════════════════════════════════════════════
        # §11  MLA ARCHITECTURE — step-by-step
        # ══════════════════════════════════════════════════════════════════════
        t = bm["mla_architecture"]
        erase(lrm_items, t=t - 1.0)

        arch_title = title("MLA Architecture Overview", y=80, color=BLUE)

        # Input X
        x_box = rrect(cx=960, cy=200, w=320, h=100, fill=PASTEL_BLUE, border=BLUE, opacity=0.4)
        x_lbl = label("Input X\n(token embedding)", x=960, y=200, color=BLUE, size=40)

        # Split into KV path and Q path
        arr_kv = arrow(820, 250, 560, 370, color=RED,  width=5)
        arr_q  = arrow(1100,250, 1360,370, color=BLUE, width=5)

        # KV compression
        kv_down = rrect(cx=480, cy=430, w=300, h=100, fill=PASTEL_RED, border=RED, opacity=0.4)
        kv_down_lbl = label("W_KV_down\n(compress)", x=480, y=430, color=RED, size=38)
        arr_lat = arrow(480, 480, 480, 560, color=ORANGE, width=5)

        # Latent c_KV  ← CACHED
        c_kv = rrect(cx=480, cy=630, w=320, h=110, fill=PASTEL_YELLOW, border=ORANGE,
                     opacity=0.85, border_width=5)
        c_kv_lbl = label("c_KV  ← CACHED\n(tiny latent)", x=480, y=630, color=ORANGE, size=40)

        # Decompression to K and V
        arr_to_k = arrow(360, 685, 220,  790, color=RED,   width=4)
        arr_to_v = arrow(600, 685, 740,  790, color=GREEN, width=4)

        k_box = rrect(cx=180, cy=840, w=260, h=100, fill=PASTEL_RED,   border=RED,   opacity=0.45)
        v_box = rrect(cx=780, cy=840, w=260, h=100, fill=PASTEL_GREEN, border=GREEN, opacity=0.45)
        k_lbl_a = label("K (per head)", x=180, y=840, color=RED,   size=38)
        v_lbl_a = label("V (per head)", x=780, y=840, color=GREEN, size=38)

        wku_lbl = label("W_K_up", x=240, y=750, color=RED,   size=34)
        wvu_lbl = label("W_V_up", x=700, y=750, color=GREEN, size=34)

        # Q path
        q_down = rrect(cx=1440, cy=430, w=300, h=100, fill=PASTEL_BLUE, border=BLUE, opacity=0.4)
        q_down_lbl = label("W_Q_down\n(compress)", x=1440, y=430, color=BLUE, size=38)
        arr_cq  = arrow(1440, 480, 1440, 555, color=PURPLE, width=5)
        c_q_box = rrect(cx=1440, cy=615, w=280, h=90, fill=PASTEL_PURPLE, border=PURPLE,
                        opacity=0.6, border_width=4)
        c_q_lbl = label("c_Q (query latent)", x=1440, y=615, color=PURPLE, size=36)
        arr_qu  = arrow(1440, 660, 1440, 745, color=BLUE, width=4)
        q_final = rrect(cx=1440, cy=820, w=260, h=90, fill=PASTEL_BLUE, border=BLUE, opacity=0.45)
        q_final_lbl = label("Q (per head)", x=1440, y=820, color=BLUE, size=38)
        wqu_lbl = label("W_Q_up", x=1530, y=705, color=BLUE, size=34)

        # Attention merge
        attn_node = rrect(cx=960, cy=960, w=700, h=90, fill=PASTEL_GREEN, border=GREEN, opacity=0.4)
        attn_lbl_a = label("Attention(Q, K, V)  →  Output", x=960, y=960, color=GREEN, size=44)
        arr_qout = arrow(1440, 865, 1160, 950, color=BLUE,  width=4)
        arr_kout = arrow(180,  890, 700,  950, color=RED,   width=4)
        arr_vout = arrow(780,  890, 810,  950, color=GREEN, width=4)

        anim(arch_title, t=t + 0.3, dur=1.0)
        anim(x_box,     t=t + 1.0, dur=0.8)
        anim(x_lbl,     t=t + 1.3, dur=0.6)

        # Step 1: KV path
        t1 = bm["mla_step1"]
        anim(arr_kv,     t=t1 + 0.3, dur=0.6)
        anim(kv_down,    t=t1 + 0.8, dur=0.8)
        anim(kv_down_lbl,t=t1 + 1.1, dur=0.6)
        anim(arr_lat,    t=t1 + 1.8, dur=0.5)
        anim(c_kv,       t=t1 + 2.2, dur=1.0)
        anim(c_kv_lbl,   t=t1 + 2.5, dur=0.8)
        anim(arr_to_k,   t=t1 + 4.5, dur=0.5)
        anim(arr_to_v,   t=t1 + 4.7, dur=0.5)
        anim(wku_lbl,    t=t1 + 5.0, dur=0.5)
        anim(wvu_lbl,    t=t1 + 5.2, dur=0.5)
        anim(k_box,      t=t1 + 5.5, dur=0.8)
        anim(v_box,      t=t1 + 5.7, dur=0.8)
        anim(k_lbl_a,    t=t1 + 5.9, dur=0.6)
        anim(v_lbl_a,    t=t1 + 6.1, dur=0.6)

        # Step 2: Q path
        t2 = bm["mla_query"]
        anim(arr_q,      t=t2 + 0.3, dur=0.6)
        anim(q_down,     t=t2 + 0.8, dur=0.8)
        anim(q_down_lbl, t=t2 + 1.1, dur=0.6)
        anim(arr_cq,     t=t2 + 1.8, dur=0.5)
        anim(c_q_box,    t=t2 + 2.2, dur=0.8)
        anim(c_q_lbl,    t=t2 + 2.5, dur=0.6)
        anim(arr_qu,     t=t2 + 3.2, dur=0.5)
        anim(wqu_lbl,    t=t2 + 3.5, dur=0.5)
        anim(q_final,    t=t2 + 4.0, dur=0.8)
        anim(q_final_lbl,t=t2 + 4.3, dur=0.6)
        anim(arr_qout,   t=t2 + 6.0, dur=0.5)
        anim(arr_kout,   t=t2 + 6.2, dur=0.5)
        anim(arr_vout,   t=t2 + 6.4, dur=0.5)
        anim(attn_node,  t=t2 + 6.8, dur=0.8)
        anim(attn_lbl_a, t=t2 + 7.1, dur=0.6)

        arch_items = [
            arch_title, x_box, x_lbl,
            arr_kv, arr_q,
            kv_down, kv_down_lbl, arr_lat, c_kv, c_kv_lbl,
            arr_to_k, arr_to_v, wku_lbl, wvu_lbl,
            k_box, v_box, k_lbl_a, v_lbl_a,
            q_down, q_down_lbl, arr_cq, c_q_box, c_q_lbl,
            arr_qu, wqu_lbl, q_final, q_final_lbl,
            arr_qout, arr_kout, arr_vout, attn_node, attn_lbl_a,
        ]

        # ══════════════════════════════════════════════════════════════════════
        # §12  MLA EQUATIONS
        # ══════════════════════════════════════════════════════════════════════
        t = bm["mla_equations"]
        erase(arch_items, t=t - 1.0)

        eq_title = title("MLA: Full Equations", y=90, color=BLUE)

        eqs = [
            (r"c_{KV} = X \cdot W_{KV}^{\downarrow}",   250),
            (r"K_h = c_{KV} \cdot W_{K,h}^{\uparrow}",  370),
            (r"V_h = c_{KV} \cdot W_{V,h}^{\uparrow}",  490),
            (r"c_Q  = X   \cdot W_Q^{\downarrow}",       610),
            (r"Q_h = c_Q  \cdot W_{Q,h}^{\uparrow}",     730),
            (r"A_h = \text{softmax}\!\left(\frac{Q_h K_h^T}{\sqrt{d_h}}\right) V_h",  880),
        ]
        eq_objs = []
        for latex, ypos in eqs:
            eq_obj = Math(latex, position=(840, ypos), font_size=68,
                          stroke_style=StrokeStyle(color=BLACK, width=2.5),
                          sketch_style=SKETCH)
            eq_objs.append(eq_obj)

        # Annotations
        ann_ckv = body("← compress KV (shared across heads)", x=1550, y=250,
                       color=ORANGE, size=38, align="left")
        ann_k   = body("← decompress per-head key",           x=1550, y=370,
                       color=RED, size=38, align="left")
        ann_v   = body("← decompress per-head value",         x=1550, y=490,
                       color=GREEN, size=38, align="left")
        ann_cq  = body("← compress Q (optional)",             x=1550, y=610,
                       color=PURPLE, size=38, align="left")
        ann_q   = body("← decompress per-head query",         x=1550, y=730,
                       color=BLUE, size=38, align="left")
        ann_a   = body("← standard scaled dot-product",       x=1550, y=880,
                       color=DARK_GRAY, size=38, align="left")

        annotations = [ann_ckv, ann_k, ann_v, ann_cq, ann_q, ann_a]

        shared_note = body("K & V share one compression matrix W_KV_down — key savings!",
                           y=1000, color=RED, size=50)

        anim(eq_title, t=t + 0.3, dur=1.0)
        for i, (eq_obj, ann) in enumerate(zip(eq_objs, annotations)):
            anim(eq_obj, t=t + 1.5 + i*2.0, dur=1.5)
            anim(ann,    t=t + 2.2 + i*2.0, dur=0.8)
        anim(shared_note, t=t + 14.0, dur=1.5)

        eq_items = [eq_title, shared_note] + eq_objs + annotations

        # ══════════════════════════════════════════════════════════════════════
        # §13  ABSORPTION TRICK
        # ══════════════════════════════════════════════════════════════════════
        t = bm["absorption_trick"]
        erase(eq_items, t=t - 1.0)

        abs_title = title("The Absorption Trick (Weight Pre-computation)", y=90, color=ORANGE)

        step1_lbl = body("Attention score for head h:", y=200, color=BLACK, size=52)
        step1_eq  = Math(
            r"Q_h K_h^T = (c_Q W_{Q,h}^{\uparrow})(c_{KV} W_{K,h}^{\uparrow})^T",
            position=(960, 310), font_size=72,
            stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)

        expand_lbl = body("Expand and rearrange:", y=430, color=BLACK, size=52)
        expand_eq  = Math(
            r"= c_Q \underbrace{(W_{Q,h}^{\uparrow} (W_{K,h}^{\uparrow})^T)}_{W_{QK,h}} c_{KV}^T",
            position=(960, 560), font_size=72,
            stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)

        insight_box = rrect(cx=960, cy=730, w=1400, h=130,
                            fill=PASTEL_ORANGE, border=ORANGE, opacity=0.3)
        insight_lbl = body(
            "W_QKh  =  W_Q_up_h × W_K_up_hᵀ  is input-independent!\n"
            "Pre-compute once per head → saves one matmul every forward pass.",
            y=730, color=ORANGE, size=44)

        benefit_arr = arrow(760, 730, 200, 900, color=ORANGE, width=4)
        benefit_lbl = body("Fold into cached weights\n→ no runtime cost!", x=350, y=950,
                           color=ORANGE, size=44, align="center")

        anim(abs_title,  t=t + 0.3, dur=1.0)
        anim(step1_lbl,  t=t + 1.2, dur=0.8)
        anim(step1_eq,   t=t + 2.0, dur=2.0)
        anim(expand_lbl, t=t + 5.0, dur=0.8)
        anim(expand_eq,  t=t + 6.0, dur=2.0)
        anim(insight_box,t=t + 9.5, dur=1.0)
        anim(insight_lbl,t=t + 10.0,dur=1.2)
        anim(benefit_arr,t=t + 12.0,dur=0.8)
        anim(benefit_lbl,t=t + 12.5,dur=1.0)

        abs_items = [abs_title, step1_lbl, step1_eq, expand_lbl, expand_eq,
                     insight_box, insight_lbl, benefit_arr, benefit_lbl]

        # ══════════════════════════════════════════════════════════════════════
        # §14  MEMORY SAVINGS — bar chart
        # ══════════════════════════════════════════════════════════════════════
        t = bm["memory_savings"]
        erase(abs_items, t=t - 1.0)

        mem_title = title("Memory Savings: MHA vs GQA vs MLA", y=90, color=BLUE)

        # Bar chart (horizontal)
        chart_data = [
            ("Standard MHA",  1600, RED,    "42 GB  (H=128, dh=64, L=128k)"),
            ("GQA  (G=8)",     600, ORANGE, "~15 GB  (8× fewer KV heads)"),
            ("MLA  (r=512)",   200, GREEN,  "~1.3 GB  (latent only)"),
        ]
        bar_items = []
        for i, (lbl_t, bar_w, color, note) in enumerate(chart_data):
            y_c = 310 + i * 220
            # bar background
            bg = rrect(cx=960, cy=y_c, w=1600, h=130,
                       fill=LIGHT_GRAY, border=GRAY, opacity=0.2, border_width=1)
            # bar fill
            bf = rrect(cx=260 + bar_w//2, cy=y_c, w=bar_w, h=110,
                       fill=color, border=color, opacity=0.5, border_width=3)
            bl = label(lbl_t, x=260 + bar_w + 80, y=y_c - 18, color=color, size=44)
            bn = label(note, x=260 + bar_w + 80, y=y_c + 25, color=DARK_GRAY, size=36)
            bar_items.extend([bg, bf, bl, bn])

        ratio_lbl = body("MLA achieves 32× compression vs MHA with no quality loss!",
                         y=920, color=GREEN, size=56)
        formula_note = Math(
            r"\text{MLA cache} = L \times r \quad \text{vs} \quad L \times H \times 2 \times d_h",
            position=(960, 1010), font_size=56,
            stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)

        anim(mem_title, t=t + 0.3, dur=1.0)
        for i in range(3):
            base = t + 1.5 + i * 2.0
            anim(bar_items[i*4 + 0], t=base,       dur=0.6)
            anim(bar_items[i*4 + 1], t=base + 0.4, dur=1.0)
            anim(bar_items[i*4 + 2], t=base + 1.2, dur=0.6)
            anim(bar_items[i*4 + 3], t=base + 1.5, dur=0.6)
        anim(ratio_lbl,   t=t + 10.0, dur=1.5)
        anim(formula_note,t=t + 12.0, dur=1.5)

        mem_items = [mem_title, ratio_lbl, formula_note] + bar_items

        # ══════════════════════════════════════════════════════════════════════
        # §15  QUALITY COMPARISON
        # ══════════════════════════════════════════════════════════════════════
        t = bm["quality_comparison"]
        erase(mem_items, t=t - 1.0)

        qual_title = title("Quality: MLA vs GQA vs MHA", y=90, color=BLUE)

        qual_table = Table(
            data=[
                ["Method",        "KV Cache", "Memory",  "Quality",   "Verdict"],
                ["MHA (standard)","Per head", "Massive", "Best",      "Baseline"],
                ["GQA (G=8)",     "Shared",  "Medium",  "Lower",     "OK trade-off"],
                ["MQA",           "1 shared","Minimal", "Noticeably lower", "Too lossy"],
                ["MLA (r=512)",   "Latent",  "Smallest","≈ MHA",     "Best of both!"],
            ],
            top_left=(120, 230),
            col_widths=[300, 290, 240, 340, 340],
            row_heights=[90, 90, 90, 90, 90],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.5),
            fill_style=FillStyle(color=WHITE),
            stroke_style=StrokeStyle(color=BLACK, width=3),
            sketch_style=SKETCH
        )

        ablation_note = body(
            "DeepSeek ablation studies: MLA slightly exceeds MHA baseline\n"
            "on multiple benchmarks, GQA with equivalent memory budget falls behind.",
            y=870, color=DARK_GRAY, size=46)

        why_box = rrect(cx=960, cy=990, w=1600, h=90,
                        fill=PASTEL_GREEN, border=GREEN, opacity=0.3)
        why_lbl = body(
            "Why? MLA's shared compression learns universal context — more expressive than grouping.",
            y=990, color=GREEN, size=44)

        anim(qual_title,    t=t + 0.3, dur=1.0)
        anim(qual_table,    t=t + 1.5, dur=4.0)
        anim(ablation_note, t=t + 12.0, dur=1.5)
        anim(why_box,       t=t + 15.0, dur=1.0)
        anim(why_lbl,       t=t + 15.3, dur=1.0)

        qual_items = [qual_title, qual_table, ablation_note, why_box, why_lbl]

        # ══════════════════════════════════════════════════════════════════════
        # §16  INFERENCE WALKTHROUGH — token-by-token
        # ══════════════════════════════════════════════════════════════════════
        t = bm["inference_walkthrough"]
        erase(qual_items, t=t - 1.0)

        inf_title = title("Inference: Token-by-Token Walkthrough", y=80, color=BLUE)

        # Step labels
        steps = [
            ("Token 1 arrives", "Compute c_KV_1 = X1·W_KV_down\nStore c_KV_1 in cache  (size: r)",
             PASTEL_BLUE, BLUE, 220),
            ("Token 2 arrives", "Compute c_KV_2, append to cache\nCache now has 2 × r numbers",
             PASTEL_GREEN, GREEN, 460),
            ("Attention for T2", "Decompress c_KV_1 → K1,V1\nDecompress c_KV_2 → K2,V2\nRun attention",
             PASTEL_ORANGE, ORANGE, 700),
            ("Token N arrives", "Cache = N × r  (grows slowly!)\nNo matter how many heads H is",
             PASTEL_PURPLE, PURPLE, 900),
        ]
        step_boxes_inf, step_lbls_inf, step_descs_inf = [], [], []
        for name, desc, fill, border, y_c in steps:
            sb = rrect(cx=360, cy=y_c, w=580, h=110, fill=fill, border=border, opacity=0.35)
            sl = label(name, x=360, y=y_c, color=border, size=44)
            sd = body(desc, x=980, y=y_c, color=border, size=40, align="left")
            step_boxes_inf.append(sb)
            step_lbls_inf.append(sl)
            step_descs_inf.append(sd)

        # Arrows between steps
        step_arrows = [arrow(360, y_c + 55, 360, y_c + 145, color=GRAY, width=4)
                       for _, _, _, _, y_c in steps[:-1]]

        cache_grow = body(
            "Cache per token = r  (constant per token, independent of number of heads!)",
            y=1020, color=RED, size=48)

        anim(inf_title, t=t + 0.3, dur=1.0)
        for i in range(4):
            anim(step_boxes_inf[i],  t=t + 1.5 + i*2.5, dur=0.8)
            anim(step_lbls_inf[i],   t=t + 1.8 + i*2.5, dur=0.6)
            anim(step_descs_inf[i],  t=t + 2.0 + i*2.5, dur=1.0)
            if i < 3:
                anim(step_arrows[i], t=t + 3.0 + i*2.5, dur=0.4)
        anim(cache_grow, t=t + 13.0, dur=1.5)

        inf_items = ([inf_title, cache_grow] +
                     step_boxes_inf + step_lbls_inf + step_descs_inf + step_arrows)

        # ══════════════════════════════════════════════════════════════════════
        # §17  RoPE NOTE
        # ══════════════════════════════════════════════════════════════════════
        t = bm["rope_note"]
        erase(inf_items, t=t - 1.0)

        rope_title = title("Technical Note: RoPE & Positional Encoding", y=90, color=DARK_GRAY)

        rope_prob_box = rrect(cx=480, cy=350, w=760, h=340,
                              fill=PASTEL_RED, border=RED, opacity=0.2)
        rope_prob_lbl = body(
            "Problem:\nRoPE must be applied to Keys\nbefore attention.\nBut Keys are reconstructed\nfrom the latent c_KV.\nApplying RoPE inside the latent\nbreaks the absorption trick!",
            x=480, y=350, color=RED, size=40)

        arrow_rope = arrow(870, 350, 1010, 350, color=GRAY, width=6)
        solution_lbl = label("DeepSeek's\nSolution →", x=940, y=310, color=GRAY, size=38)

        rope_sol_box = rrect(cx=1440, cy=350, w=760, h=340,
                             fill=PASTEL_GREEN, border=GREEN, opacity=0.2)
        rope_sol_lbl = body(
            "Solution:\nAdd a small decoupled RoPE\nkey component k_rope.\nk_rope is separate from the\nlow-rank key and carries\nonly the position signal.\nConcatenate at attention time.",
            x=1440, y=350, color=GREEN, size=40)

        rope_eq = Math(
            r"K_h = [c_{KV} W_{K,h}^{\uparrow} \;;\; k^{\text{rope}}]",
            position=(960, 760), font_size=72,
            stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)

        rope_note_txt = body("This keeps absorption intact while preserving positional information.",
                             y=900, color=DARK_GRAY, size=48)

        anim(rope_title,    t=t + 0.3, dur=1.0)
        anim(rope_prob_box, t=t + 1.2, dur=1.0)
        anim(rope_prob_lbl, t=t + 1.5, dur=1.5)
        anim(arrow_rope,    t=t + 5.0, dur=0.8)
        anim(solution_lbl,  t=t + 5.5, dur=0.6)
        anim(rope_sol_box,  t=t + 6.0, dur=1.0)
        anim(rope_sol_lbl,  t=t + 6.3, dur=1.5)
        anim(rope_eq,       t=t + 10.0, dur=2.0)
        anim(rope_note_txt, t=t + 12.5, dur=1.2)

        rope_items = [rope_title, rope_prob_box, rope_prob_lbl, arrow_rope,
                      solution_lbl, rope_sol_box, rope_sol_lbl, rope_eq, rope_note_txt]

        # ══════════════════════════════════════════════════════════════════════
        # §18  TransMLA — post-training conversion
        # ══════════════════════════════════════════════════════════════════════
        t = bm["transmla"]
        erase(rope_items, t=t - 1.0)

        trans_title = title("Post-Training Conversion: TransMLA", y=90, color=BLUE)

        # Pipeline
        pipe = [
            ("Existing GQA Model\n(e.g. Llama, Mistral)", PASTEL_ORANGE, ORANGE),
            ("SVD Factorisation\nof KV projection weights", PASTEL_PURPLE, PURPLE),
            ("Short Fine-tuning\n(< 1% of training)", PASTEL_BLUE, BLUE),
            ("MLA-efficient Model\n(same quality, less memory!)", PASTEL_GREEN, GREEN),
        ]
        pipe_xs = [210, 660, 1110, 1640]
        pipe_boxes, pipe_lbls = [], []
        for i, ((txt, fill, border), px) in enumerate(zip(pipe, pipe_xs)):
            pb = rrect(cx=px, cy=500, w=380, h=240, fill=fill, border=border, opacity=0.35)
            pl = label(txt, x=px, y=500, color=border, size=40)
            pipe_boxes.append(pb)
            pipe_lbls.append(pl)

        pipe_arrows = [arrow(pipe_xs[i]+190, 500, pipe_xs[i+1]-190, 500, color=GRAY, width=6)
                       for i in range(3)]

        svd_note = body(
            "SVD (Singular Value Decomposition) finds the best low-rank factors\n"
            "W_KV ≈ U_r · Σ_r · V_rᵀ  →  set W_KV_down = U_r · Σ_r,  W_K_up = V_rᵀ",
            y=770, color=PURPLE, size=42)

        free_lbl = body(
            "→  Existing GQA models get MLA efficiency without retraining from scratch!",
            y=900, color=GREEN, size=54)

        anim(trans_title, t=t + 0.3, dur=1.0)
        for i in range(4):
            anim(pipe_boxes[i], t=t + 1.5 + i*1.5, dur=1.0)
            anim(pipe_lbls[i],  t=t + 1.8 + i*1.5, dur=0.8)
            if i < 3:
                anim(pipe_arrows[i], t=t + 2.5 + i*1.5, dur=0.5)
        anim(svd_note, t=t + 9.0, dur=1.5)
        anim(free_lbl, t=t + 12.0, dur=1.5)

        trans_items = [trans_title, svd_note, free_lbl] + pipe_boxes + pipe_lbls + pipe_arrows

        # ══════════════════════════════════════════════════════════════════════
        # §19  MODELS USING MLA — mind map
        # ══════════════════════════════════════════════════════════════════════
        t = bm["models_using_mla"]
        erase(trans_items, t=t - 1.0)

        mod_title = title("Frontier Models Using MLA", y=80, color=BLACK)

        center = Ellipse(center=(960, 540), width=380, height=160,
                         stroke_style=StrokeStyle(color=PURPLE, width=6),
                         fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.5),
                         sketch_style=SKETCH)
        center_lbl = label("MLA", x=960, y=540, color=PURPLE, size=72)

        sat_data = [
            ("DeepSeek V2\n(pioneer, 2024)", 960,  210, PASTEL_BLUE,   BLUE,   "First at scale"),
            ("DeepSeek V3\n(SOTA coding)",   1600, 380, PASTEL_GREEN,  GREEN,  "MoE + MLA"),
            ("Kimi K2\n(Moonshot AI)",        1580, 700, PASTEL_ORANGE, ORANGE, "+ linear attn"),
            ("GLM-5\n(Tsinghua)",             960,  870, PASTEL_RED,    RED,    "Dense + MLA"),
            ("Mistral 3 Large",               340,  700, PASTEL_PURPLE, PURPLE, "Flagship model"),
            ("Sarvam 105B\n(multilingual)",   340,  380, PASTEL_YELLOW, ORANGE, "105B params"),
        ]
        sat_items = []
        for txt, cx, cy, fill, border, note in sat_data:
            ln  = hline(960, 540, cx, cy, color=LIGHT_GRAY, width=3)
            bx  = rrect(cx=cx, cy=cy, w=370, h=130, fill=fill, border=border,
                        opacity=0.55, border_width=4)
            lbl_s = label(txt,  x=cx, y=cy - 12, color=border, size=38)
            nt  = label(note, x=cx, y=cy + 42,  color=DARK_GRAY, size=30)
            sat_items.extend([ln, bx, lbl_s, nt])

        anim(mod_title, t=t + 0.3, dur=1.0)
        anim(center,    t=t + 1.2, dur=1.0)
        anim(center_lbl,t=t + 1.5, dur=0.6)
        for i in range(6):
            base = t + 2.5 + i*1.3
            anim(sat_items[i*4 + 0], t=base,       dur=0.5)  # line
            anim(sat_items[i*4 + 1], t=base + 0.3, dur=0.8)  # box
            anim(sat_items[i*4 + 2], t=base + 0.6, dur=0.5)  # label
            anim(sat_items[i*4 + 3], t=base + 0.8, dur=0.4)  # note

        mod_items = [mod_title, center, center_lbl] + sat_items

        # ══════════════════════════════════════════════════════════════════════
        # §20  TRADE-OFFS
        # ══════════════════════════════════════════════════════════════════════
        t = bm["tradeoffs"]
        erase(mod_items, t=t - 1.0)

        trade_title = title("Trade-offs: Honest Assessment", y=90, color=ORANGE)

        cons_hdr  = title("Drawbacks", y=210, color=RED, size=64)
        cons_list = bullets([
            "Implementation ~3× more complex than standard attention",
            "Decompression adds small compute overhead per forward pass",
            "RoPE decoupling adds an extra engineering concern",
            "Absorption trick requires careful weight shape management",
            "Short-sequence inference may not benefit (overhead ≫ savings)",
        ], x=200, y0=290, dy=110, color=RED, size=46)

        pros_hdr  = title("Benefits", y=870, color=GREEN, size=64)  # placed separately
        # Actually arrange side by side
        # redo as two columns
        erase([cons_hdr] + cons_list, t=t - 1.0)  # just building, not erasing yet

        col_con = rrect(cx=480, cy=560, w=780, h=720,
                        fill=PASTEL_RED, border=RED, opacity=0.12, border_width=3)
        col_pro = rrect(cx=1440, cy=560, w=780, h=720,
                        fill=PASTEL_GREEN, border=GREEN, opacity=0.12, border_width=3)
        con_hdr2 = label("⚠  Drawbacks", x=480, y=200, color=RED, size=60)
        pro_hdr2 = label("✓  Benefits",  x=1440,y=200, color=GREEN, size=60)

        con_bullets = bullets([
            "3× more complex code",
            "Decompression overhead",
            "RoPE decoupling needed",
            "Weight shape bookkeeping",
            "Short-seq. little benefit",
        ], x=130, y0=280, dy=110, color=RED, size=46)
        pro_bullets = bullets([
            "32× smaller KV-Cache",
            "MHA-level quality",
            "Enables longer contexts",
            "Works without retraining",
            "Frontier-proven at scale",
        ], x=1090, y0=280, dy=110, color=GREEN, size=46)

        verdict2 = body(
            "For large-scale serving of long sequences: the complexity is absolutely worth it.",
            y=970, color=BLACK, size=52)

        anim(trade_title, t=t + 0.3, dur=1.0)
        anim(col_con,     t=t + 1.0, dur=0.8)
        anim(col_pro,     t=t + 1.0, dur=0.8)
        anim(con_hdr2,    t=t + 1.5, dur=0.8)
        anim(pro_hdr2,    t=t + 1.5, dur=0.8)
        for i in range(5):
            anim(con_bullets[i], t=t + 2.5 + i*1.0, dur=0.8)
            anim(pro_bullets[i], t=t + 2.5 + i*1.0, dur=0.8)
        anim(verdict2, t=t + 10.0, dur=1.5)

        trade_items = ([trade_title, col_con, col_pro, con_hdr2, pro_hdr2, verdict2] +
                       con_bullets + pro_bullets)

        # ══════════════════════════════════════════════════════════════════════
        # §21  WHEN TO USE
        # ══════════════════════════════════════════════════════════════════════
        t = bm["when_to_use"]
        erase(trade_items, t=t - 1.0)

        wtu_title = title("When Should YOU Use MLA?", y=90, color=BLUE)

        use_box = rrect(cx=480, cy=490, w=780, h=620,
                        fill=PASTEL_GREEN, border=GREEN, opacity=0.2, border_width=3)
        use_hdr = label("✓  Use MLA when…", x=480, y=210, color=GREEN, size=58)
        use_pts = bullets([
            "Serving long sequences\n  (code gen, docs, reasoning)",
            "GPU memory is the\n  binding constraint",
            "You need MHA quality\n  with GQA memory",
            "Building new frontier\n  model architecture",
        ], x=130, y0=280, dy=140, color=GREEN, size=44)

        skip_box = rrect(cx=1440, cy=490, w=780, h=620,
                         fill=PASTEL_RED, border=RED, opacity=0.2, border_width=3)
        skip_hdr = label("✗  Stick with GQA when…", x=1440, y=210, color=RED, size=58)
        skip_pts = bullets([
            "Simplicity is paramount\n  (research prototype)",
            "Short sequences —\n  cache not the bottleneck",
            "Limited engineering\n  bandwidth for serving stack",
            "Fine-tuning a GQA model\n  (convert via TransMLA)",
        ], x=1090, y0=280, dy=140, color=RED, size=44)

        anim(wtu_title, t=t + 0.3, dur=1.0)
        anim(use_box,   t=t + 1.0, dur=0.8)
        anim(skip_box,  t=t + 1.0, dur=0.8)
        anim(use_hdr,   t=t + 1.5, dur=0.8)
        anim(skip_hdr,  t=t + 1.5, dur=0.8)
        for i in range(4):
            anim(use_pts[i],  t=t + 2.5 + i*1.5, dur=1.0)
            anim(skip_pts[i], t=t + 2.5 + i*1.5, dur=1.0)

        wtu_items = ([wtu_title, use_box, skip_box, use_hdr, skip_hdr] +
                     use_pts + skip_pts)

        # ══════════════════════════════════════════════════════════════════════
        # §22  SUMMARY CHEAT-SHEET
        # ══════════════════════════════════════════════════════════════════════
        t = bm["summary"]
        erase(wtu_items, t=t - 1.0)

        sum_title = title("Summary Cheat-Sheet", y=80, color=BLUE)

        sum_table = Table(
            data=[
                ["Concept",            "Key Point"],
                ["KV-Cache Bottleneck","Cache grows as L×H×2×dh → explodes at long seqs"],
                ["Low-Rank Approx.",   "M ≈ U·V  where rank r ≪ n, m"],
                ["MLA Compression",    "c_KV = X·W_down  (tiny, r-dim, cached)"],
                ["MLA Decompression",  "K = c_KV·W_K_up,  V = c_KV·W_V_up (per head)"],
                ["Absorption Trick",   "W_QK = W_Q_up·W_K_upᵀ  pre-computed offline"],
                ["Memory Saving",      "32× vs MHA  (r=512 vs H×2×dh=16384)"],
                ["Quality",            "≈ MHA  (better than GQA at same budget)"],
                ["TransMLA",           "Convert existing GQA → MLA via SVD"],
                ["Use When",           "Long seqs, memory-bound, frontier serving"],
            ],
            top_left=(80, 180),
            col_widths=[380, 1380],
            row_heights=[70, 72, 72, 72, 72, 72, 72, 72, 72, 72],
            font_size=38,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.5),
            fill_style=FillStyle(color=WHITE),
            stroke_style=StrokeStyle(color=BLACK, width=3),
            sketch_style=SKETCH
        )

        anim(sum_title, t=t + 0.3, dur=1.0)
        anim(sum_table, t=t + 1.5, dur=5.0)

        sum_items = [sum_title, sum_table]

        # ══════════════════════════════════════════════════════════════════════
        # §23  OUTRO
        # ══════════════════════════════════════════════════════════════════════
        t = bm["outro"]
        erase(sum_items, t=t - 1.0)

        outro_title = title("You Now Understand MLA!", y=260, color=BLUE, size=100)
        outro_sub   = body("From beginner intuition to advanced equations.", y=400,
                           color=DARK_GRAY, size=64)
        cta_box = rrect(cx=960, cy=600, w=1400, h=220,
                        fill=PASTEL_ORANGE, border=ORANGE, opacity=0.3, border_width=5)
        cta_lbl = body("👍 Like  ·  🔔 Subscribe  ·  💬 Comment your question below",
                       y=590, color=ORANGE, size=60)
        cta_sub = body("What should the next video cover?", y=660, color=ORANGE, size=46)

        final_lbl = body(
            "Thanks for watching. See you in the next one.",
            y=870, color=BLACK, size=60)

        anim(outro_title, t=t + 0.3, dur=1.8)
        anim(outro_sub,   t=t + 2.2, dur=1.2)
        anim(cta_box,     t=t + 4.0, dur=1.0)
        anim(cta_lbl,     t=t + 4.3, dur=1.0)
        anim(cta_sub,     t=t + 5.0, dur=0.8)

        tf = bm["final"]
        anim(final_lbl, t=tf + 0.5, dur=2.0)

        return trk.end_time + 2.5


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, "mla_youtube_narration.mp3")
    video_path = os.path.join(output_dir, "mla_youtube_complete.mp4")

    asyncio.run(synthesize(Path(audio_path)))
    duration = build_scene(audio_path)

    print(f"Rendering complete YouTube MLA explainer  ({duration:.0f} s)…")
    scene.render(video_path, max_length=duration)
    print(f"Done → {video_path}")


if __name__ == "__main__":
    main()