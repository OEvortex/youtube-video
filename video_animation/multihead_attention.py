import os
import asyncio
import edge_tts
from handanim.core import Scene, FillStyle, StrokeStyle, SketchStyle, DrawableGroup
from handanim.primitives.eraser import Eraser
from handanim.core.scene import tts_speech
from handanim.animations import SketchAnimation, FadeInAnimation, FadeOutAnimation
from handanim.primitives import (
    Text, Rectangle, Circle, Line, Arrow, Polygon, Ellipse
)

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS & LAYOUT CONSTANTS  (1920 × 1080)
# ═══════════════════════════════════════════════════════════════════════════════
W, H = 1920, 1080
CX = W // 2
CY = H // 2

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BLACK = (0.05, 0.05, 0.05)
WHITE = (0.98, 0.98, 0.98)
GRAY = (0.55, 0.55, 0.55)
DARK_GRAY = (0.22, 0.22, 0.22)
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
MAGENTA = (0.85, 0.25, 0.65)

PINK = (0.92, 0.30, 0.65)
TEAL = (0.10, 0.65, 0.65)
INDIGO = (0.30, 0.25, 0.78)
YELLOW = (0.95, 0.85, 0.15)

GLOW_BLUE = (0.60, 0.80, 1.00)
GLOW_GREEN = (0.60, 0.95, 0.70)
GLOW_ORANGE = (1.00, 0.75, 0.50)

FONT = "cabin_sketch"
COLOR_PRIMARY = BLUE
FPS = 24
VOICE = "en-US-JennyNeural"
RATE = "+5%"

# ═══════════════════════════════════════════════════════════════════════════════
# TTS PROVIDER
# ═══════════════════════════════════════════════════════════════════════════════
class EdgeTTSProvider:
    @tts_speech
    def synthesize(self, speech: str, output_path: str, **kwargs) -> str:
        communicate = edge_tts.Communicate(speech, **kwargs)
        asyncio.run(communicate.save(output_path))
        return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def heading(text, color=BLUE, size=54):
    return Text(text=text, position=(CX, 75), font_size=size,
                stroke_style=StrokeStyle(color=color, width=3), font_name=FONT)

def label(text, x, y, color=DARK_GRAY, size=26, width=2):
    return Text(text=text, position=(x, y), font_size=size,
                stroke_style=StrokeStyle(color=color, width=width), font_name=FONT)

def small_label(text, x, y, color=GRAY, size=20):
    return Text(text=text, position=(x, y), font_size=size,
                stroke_style=StrokeStyle(color=color, width=1), font_name=FONT)

def token_circle(x, y, text_content, color, radius=45):
    circle = Circle(
        center=(x, y), radius=radius,
        stroke_style=StrokeStyle(color=color, width=3),
        fill_style=FillStyle(color=WHITE, opacity=0.9),
        sketch_style=SketchStyle(roughness=1.5)
    )
    txt = Text(text=text_content, position=(x, y+5), font_size=24,
               stroke_style=StrokeStyle(color=color, width=2), font_name=FONT)
    return circle, txt

def matrix_grid(x, y, rows, cols, color, cell_size=40, gap=8):
    cells = []
    for r in range(rows):
        for c in range(cols):
            cx = x + c * (cell_size + gap) + cell_size//2
            cy = y + r * (cell_size + gap) + cell_size//2
            cell = Circle(
                center=(cx, cy), radius=cell_size//3,
                stroke_style=StrokeStyle(color=color, width=1),
                fill_style=FillStyle(color=color, opacity=0.3 + (r+c)*0.05),
                sketch_style=SketchStyle(roughness=0.5)
            )
            cells.append(cell)
    return cells

def matrix_outline(x, y, rows, cols, color, cell_size=40, gap=8):
    w = cols * (cell_size + gap) - gap
    h = rows * (cell_size + gap) - gap
    return Rectangle(
        top_left=(x-5, y-5), width=w+10, height=h+10,
        stroke_style=StrokeStyle(color=color, width=2),
        fill_style=None,
        sketch_style=SketchStyle(roughness=1)
    )

def connection_line(x1, y1, x2, y2, color, width=2, dashed=False):
    return Line(
        start=(x1, y1), end=(x2, y2),
        stroke_style=StrokeStyle(color=color, width=width, dash_pattern=[8,4] if dashed else None)
    )

def curved_arrow(x1, y1, x2, y2, color, curvature=0.3):
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    ctrl_x = mid_x + (y2 - y1) * curvature
    ctrl_y = mid_y - (x2 - x1) * curvature
    return Arrow(
        start=(x1, y1), end=(x2, y2),
        arrow_head_type="->", arrow_head_size=15, arrow_head_angle=35,
        stroke_style=StrokeStyle(color=color, width=2),
        control_points=[(ctrl_x, ctrl_y)]
    )

def flow_arrow(x1, y1, x2, y2, color=ORANGE, width=3):
    return Arrow(
        start=(x1, y1), end=(x2, y2),
        arrow_head_type="->", arrow_head_size=18, arrow_head_angle=38,
        stroke_style=StrokeStyle(color=color, width=width)
    )

def node_with_label(x, y, label_text, node_color, label_color, size=50):
    node = Circle(
        center=(x, y), radius=size//2,
        stroke_style=StrokeStyle(color=node_color, width=3),
        fill_style=FillStyle(color=WHITE, opacity=0.95),
        sketch_style=SketchStyle(roughness=1.5)
    )
    lbl = Text(text=label_text, position=(x, y + size//2 + 25), font_size=20,
               stroke_style=StrokeStyle(color=label_color, width=1.5), font_name=FONT)
    return node, lbl

def operation_node(x, y, text, color):
    size = 50
    points = [
        (x, y - size),
        (x + size, y),
        (x, y + size),
        (x - size, y),
    ]
    diamond = Polygon(
        points=points,
        stroke_style=StrokeStyle(color=color, width=2),
        fill_style=FillStyle(color=WHITE, opacity=0.9),
        sketch_style=SketchStyle(roughness=1.5)
    )
    txt = Text(text=text, position=(x, y+3), font_size=18,
               stroke_style=StrokeStyle(color=color, width=1.5), font_name=FONT)
    return diamond, txt

def cloud_shape(x, y, w, h, color):
    circles = []
    offsets = [
        (0, 0, w//3), (w//4, -h//6, w//4), (-w//4, -h//6, w//4),
        (w//3, 0, w//5), (-w//3, 0, w//5), (0, h//5, w//4)
    ]
    for dx, dy, r in offsets:
        c = Circle(
            center=(x + dx, y + dy), radius=r,
            stroke_style=StrokeStyle(color=color, width=2),
            fill_style=FillStyle(color=WHITE, opacity=0.85),
            sketch_style=SketchStyle(roughness=2)
        )
        circles.append(c)
    return circles

def attention_arc(x1, y1, x2, y2, color, height=80):
    mid_x = (x1 + x2) / 2
    mid_y = min(y1, y2) - height
    return Arrow(
        start=(x1, y1), end=(x2, y2),
        arrow_head_type="->", arrow_head_size=12, arrow_head_angle=35,
        stroke_style=StrokeStyle(color=color, width=3),
        control_points=[(mid_x, mid_y)]
    )

def equation_text(x, y, text, color=PURPLE, size=28):
    return Text(text=text, position=(x, y), font_size=size,
                stroke_style=StrokeStyle(color=color, width=2), font_name=FONT)

def icon_circle(x, y, emoji_text, color, radius=35):
    circle = Circle(
        center=(x, y), radius=radius,
        stroke_style=StrokeStyle(color=color, width=3),
        fill_style=FillStyle(color=WHITE, opacity=0.95),
        sketch_style=SketchStyle(roughness=1.5)
    )
    txt = Text(text=emoji_text, position=(x, y+5), font_size=28,
               stroke_style=StrokeStyle(color=color, width=2), font_name=FONT)
    return circle, txt

def pipeline_segment(x, y, w, h, label_text, color):
    left_cap = Ellipse(center=(x, y+h//2), width=h, height=h,
                       stroke_style=StrokeStyle(color=color, width=2),
                       fill_style=FillStyle(color=WHITE, opacity=0.9))
    right_cap = Ellipse(center=(x+w, y+h//2), width=h, height=h,
                        stroke_style=StrokeStyle(color=color, width=2),
                        fill_style=FillStyle(color=WHITE, opacity=0.9))
    connector = Rectangle(
        top_left=(x, y), width=w, height=h,
        stroke_style=StrokeStyle(color=color, width=2),
        fill_style=None
    )
    lbl = Text(text=label_text, position=(x + w//2, y + h//2 + 5), font_size=22,
               stroke_style=StrokeStyle(color=color, width=2), font_name=FONT)
    return [left_cap, connector, right_cap, lbl]

def sketch(scene, drawable, t, dur=0.8):
    scene.add(SketchAnimation(start_time=scene.timeline_cursor + t, duration=dur),
              drawable=drawable)

def sketch_all(scene, drawables, t, dur=0.8, stagger=0):
    for i, d in enumerate(drawables):
        sketch(scene, d, t + i*stagger, dur)

def erase(scene, objects_to_erase, at, duration=1.5):
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
# SCENE 1  ─  CINEMATIC TITLE  (~55 s)
# ══════════════════════════════════════════════
def scene_title(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Multi-Head Attention is the beating heart of every modern transformer model. "
            "From GPT-4 to DeepSeek to Gemini, this mechanism is what allows AI to understand "
            "context, relationships, and meaning across entire sequences of text. "
            "In this video, we will dive deep into exactly how it works — the Query, Key, and Value matrices, "
            "the attention scores, the softmax operation, and why we need multiple heads. "
            "By the end, you will understand the complete mathematical flow and the intuition behind "
            "why this architecture has revolutionized artificial intelligence."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        shadow = Text("Multi-Head Attention", position=(CX+4, 344),
                      font_size=132, font_name=FONT,
                      stroke_style=StrokeStyle(color=LIGHT_GRAY, width=7))
        title = Text("Multi-Head Attention", position=(CX, 340),
                     font_size=132, font_name=FONT,
                     stroke_style=StrokeStyle(color=COLOR_PRIMARY, width=5))
        sub = label("The Core Mechanism Behind Modern AI", CX, 500, DARK_GRAY, 40, 2)
        tag = label("Query · Key · Value · Attention Scores · Softmax · Multiple Heads",
                    CX, 580, ORANGE, 32, 2)
        formula = label("Attention(Q,K,V) = softmax(QK^T / √d_k) · V",
                        CX, 680, PURPLE, 36, 2)
        credit = label("A Complete Technical Deep Dive", CX, 860, GRAY, 28, 1)

        all_els = [shadow, title, sub, tag, formula, credit]

        sketch(scene, shadow, 0.0, 3.0)
        sketch(scene, title, 0.3, 3.0)
        sketch(scene, sub, 2.8, 2.0)
        sketch(scene, tag, 4.2, 1.8)
        sketch(scene, formula, 5.5, 2.0)
        sketch(scene, credit, 7.5, 1.5)

        erase(scene, all_els, track.end_time - scene.timeline_cursor - 1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE 2  ─  THE ATTENTION INTUITION  (~70 s)
# FIX: strong attention arc height reduced (120→50) to avoid overlapping heading
# ═══════════════════════════════════════════════════════════════════════════════
def scene_attention_intuition(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Before diving into the mathematics, let's understand the core intuition. "
            "Imagine you are reading a sentence: 'The cat sat on the mat because it was tired.' "
            "When you process the word 'it', you need to know what 'it' refers to. "
            "Your brain automatically looks back and focuses attention on 'cat' — not 'mat'. "
            "This is exactly what attention does in neural networks. "
            "It allows each word — or token — to 'look' at every other word in the sequence, "
            "decide which ones are most relevant, and blend their information together. "
            "The result is a context-aware representation where each token knows about the entire sequence. "
            "This is the breakthrough that made transformers possible — and why they outperform "
            "every previous architecture in natural language processing."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        hd = heading("The Core Intuition", BLUE)
        sketch(scene, hd, 0.0, 2.0)

        token_data = [
            ("The", 180, BLUE), ("cat", 360, RED), ("sat", 520, BLUE),
            ("on", 660, BLUE), ("the", 800, BLUE), ("mat", 940, BLUE),
            ("because", 1100, BLUE), ("it", 1280, ORANGE), ("was", 1440, BLUE), ("tired", 1620, BLUE)
        ]

        all_elements = [hd]
        token_circles = {}
        t = 1.5

        for word, x, color in token_data:
            circle, txt = token_circle(x, 220, word, color, radius=40)
            sketch(scene, circle, t, 0.5)
            sketch(scene, txt, t + 0.2, 0.4)
            token_circles[word] = (circle, txt, x, 220)
            all_elements.extend([circle, txt])
            t += 0.3

        t += 0.5
        it_x, it_y = token_circles["it"][2], token_circles["it"][3]

        # FIX: height reduced from 120 → 50 so arc control point stays below heading (y~102)
        # With height=50: bezier midpoint ≈ y=185, well below heading bottom at y≈102
        strong_conn = attention_arc(
            it_x, it_y - 40,
            token_circles["cat"][2], token_circles["cat"][3] - 40,
            RED, height=50
        )
        sketch(scene, strong_conn, t, 1.0)
        strong_lbl = label("strong attention", 820, 150, RED, 20, 1)
        sketch(scene, strong_lbl, t + 0.8, 0.5)
        all_elements.extend([strong_conn, strong_lbl])

        weak_words = ["The", "sat", "on", "the", "mat", "because"]
        for i, word in enumerate(weak_words):
            wx, wy = token_circles[word][2], token_circles[word][3]
            conn = connection_line(it_x, it_y - 40, wx, wy - 40, GRAY, width=1, dashed=True)
            sketch(scene, conn, t + 0.2 + i * 0.1, 0.6)
            all_elements.append(conn)

        t += 2.0

        query_icon, query_lbl = icon_circle(300, 450, "Q?", ORANGE, 35)
        query_txt = label("1. Token queries all others", 420, 450, DARK_GRAY, 22, 1)
        sketch(scene, query_icon, t, 0.6)
        sketch(scene, query_lbl, t + 0.2, 0.4)
        sketch(scene, query_txt, t + 0.4, 0.5)
        all_elements.extend([query_icon, query_lbl, query_txt])

        t += 1.0
        score_icon, score_lbl = icon_circle(300, 540, "S", TEAL, 35)
        score_txt = label("2. Relevance scores computed", 420, 560, DARK_GRAY, 22, 1)
        sketch(scene, score_icon, t, 0.6)
        sketch(scene, score_lbl, t + 0.2, 0.4)
        sketch(scene, score_txt, t + 0.4, 0.5)
        all_elements.extend([score_icon, score_lbl, score_txt])

        t += 1.0
        blend_icon, blend_lbl = icon_circle(300, 630, "M", PURPLE, 35)
        blend_txt = label("3. Information blended by weights", 420, 650, DARK_GRAY, 22, 1)
        sketch(scene, blend_icon, t, 0.6)
        sketch(scene, blend_lbl, t + 0.2, 0.4)
        sketch(scene, blend_txt, t + 0.4, 0.5)
        all_elements.extend([blend_icon, blend_lbl, blend_txt])

        t += 1.0
        cloud_circles = cloud_shape(1300, 560, 200, 120, GREEN)
        cloud_lbl = label("Context-Aware Vector", 1300, 560, GREEN, 24, 2)
        sketch_all(scene, cloud_circles, t, 0.5, 0.1)
        sketch(scene, cloud_lbl, t + 0.8, 0.6)
        all_elements.extend(cloud_circles + [cloud_lbl])

        t += 1.5
        vec_lbls = [
            ("50% cat meaning", 1120, 490, RED),
            ("20% position", 1500, 490, BLUE),
            ("30% pattern", 1300, 680, PURPLE)
        ]
        for txt, x, y, col in vec_lbls:
            vl = label(txt, x, y, col, 18, 1)
            sketch(scene, vl, t, 0.4)
            all_elements.append(vl)
            t += 0.2

        erase(scene, all_elements, track.end_time - scene.timeline_cursor - 1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE 3  ─  QUERY KEY VALUE EXPLAINED  (~80 s)
# FIX: matrix y-spacing increased from 140px to 180px so matrices don't overlap
#      (each matrix outline is ~168px tall; 140px spacing caused 28px overlap)
# FIX: database analogy repositioned to center-align with the three matrices
# ═══════════════════════════════════════════════════════════════════════════════
def scene_qkv_explained(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Now let's understand the three matrices that make attention possible: Query, Key, and Value. "
            "Think of it like a database search. When you want to find information, you write a Query — "
            "what you are looking for. The database has Keys — descriptions of what is stored. "
            "When your Query matches a Key, you get the corresponding Value — the actual information. "
            "In transformers, every token produces all three: a Query describing what it needs, "
            "a Key describing what it offers, and a Value containing its actual information. "
            "Each token's Query is compared against ALL other tokens' Keys. "
            "High similarity means high attention — that token's Value will be important for understanding this token. "
            "This is implemented using learned linear projections — three separate weight matrices that transform "
            "the input embeddings into Q, K, and V matrices."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        hd = heading("Query, Key, and Value", BLUE)
        sketch(scene, hd, 0.0, 2.0)

        all_elements = [hd]
        t = 1.5

        # Input tokens — FIX: y-step 140→180 to match matrix spacing
        input_tokens = []
        words = ["cat", "sat", "mat"]
        colors = [RED, BLUE, BLUE]
        for i, (word, col) in enumerate(zip(words, colors)):
            y = 280 + i * 180          # FIX: was 280 + i * 140
            circle, txt = token_circle(200, y, word, col, radius=45)
            sketch(scene, circle, t + i*0.4, 0.5)
            sketch(scene, txt, t + i*0.4 + 0.2, 0.4)
            input_tokens.extend([circle, txt])
        all_elements.extend(input_tokens)

        input_lbl = label("Input Embeddings", 200, 180, DARK_GRAY, 24, 1)
        sketch(scene, input_lbl, t + 0.5, 0.6)
        all_elements.append(input_lbl)

        t += 2.0

        # Linear projection diamond nodes — FIX: y-step 140→180
        projections = []
        proj_data = [
            ("Query\nW_Q", 480, 280, ORANGE),
            ("Key\nW_K",   480, 460, GREEN),    # FIX: was 420
            ("Value\nW_V", 480, 640, BLUE)       # FIX: was 560
        ]
        for txt, x, y, col in proj_data:
            diamond, lbl = operation_node(x, y, txt, col)
            sketch(scene, diamond, t, 0.7)
            sketch(scene, lbl, t + 0.3, 0.5)
            projections.extend([diamond, lbl])
            t += 0.4
        all_elements.extend(projections)

        # Arrows from input tokens to projection nodes — FIX: y-step 140→180
        t += 0.5
        for i in range(3):
            y_in = 280 + i * 180       # FIX: was 140
            for j in range(3):
                y_proj = 280 + j * 180  # FIX: was 140
                if i == j:
                    arr = flow_arrow(255, y_in, 430, y_proj, colors[i], 2)
                else:
                    arr = connection_line(255, y_in, 430, y_proj, LIGHT_GRAY, 1, dashed=True)
                sketch(scene, arr, t + i*0.1, 0.4)
                all_elements.append(arr)

        # Q, K, V matrices — FIX: y-positions 280/420/560 → 280/460/640 (168px tall each)
        t += 1.5
        matrix_data = [
            ("Q (Query)", 750, 280, ORANGE),
            ("K (Key)",   750, 460, GREEN),    # FIX: was 420
            ("V (Value)", 750, 640, BLUE)       # FIX: was 560
        ]

        matrices = []
        for name, x, y, col in matrix_data:
            outline = matrix_outline(x, y, 4, 3, col, cell_size=35, gap=6)
            sketch(scene, outline, t, 0.6)
            matrices.append(outline)

            cells = matrix_grid(x, y, 4, 3, col, cell_size=35, gap=6)
            for i, cell in enumerate(cells):
                sketch(scene, cell, t + 0.3 + i*0.03, 0.2)
            matrices.extend(cells)

            mat_lbl = label(name, x + 70, y - 28, col, 20, 1)
            sketch(scene, mat_lbl, t + 0.5, 0.4)
            matrices.append(mat_lbl)
            t += 0.3
        all_elements.extend(matrices)

        # Arrows from projections to matrices — FIX: y-step 140→180
        t += 0.5
        for i, (_, _, y_proj, col) in enumerate(proj_data):
            y_mat = 280 + i * 180      # FIX: was 280 + i * 140
            arr = flow_arrow(530, y_proj, 720, y_mat, col, 2)
            sketch(scene, arr, t + i*0.1, 0.4)
            all_elements.append(arr)

        # Database analogy — FIX: repositioned to vertically center with matrices (y≈460)
        t += 1.5
        query_icon, _ = icon_circle(1100, 460, "Q", ORANGE, 30)
        query_txt = label("Search", 1100, 520, ORANGE, 18, 1)
        sketch(scene, query_icon, t, 0.5)
        sketch(scene, query_txt, t + 0.2, 0.4)
        all_elements.extend([query_icon, query_txt])

        key_icon, _ = icon_circle(1250, 460, "K", GREEN, 30)
        key_txt = label("Index", 1250, 520, GREEN, 18, 1)
        sketch(scene, key_icon, t + 0.2, 0.5)
        sketch(scene, key_txt, t + 0.4, 0.4)
        all_elements.extend([key_icon, key_txt])

        val_icon, _ = icon_circle(1400, 460, "V", BLUE, 30)
        val_txt = label("Content", 1400, 520, BLUE, 18, 1)
        sketch(scene, val_icon, t + 0.4, 0.5)
        sketch(scene, val_txt, t + 0.6, 0.4)
        all_elements.extend([val_icon, val_txt])

        analogy_lbl = label("Database Analogy: Search → Match → Retrieve", 1250, 600, AMBER, 22, 2)
        sketch(scene, analogy_lbl, t + 1.0, 0.7)
        all_elements.append(analogy_lbl)

        erase(scene, all_elements, track.end_time - scene.timeline_cursor - 1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE 4  ─  ATTENTION SCORE CALCULATION  (~90 s)
# FIX: weights_lbl/sum_lbl y-overlap corrected (420/440 → 435/462)
# FIX: V-multiply section moved to right side (x>1460) instead of y=520-720
#      (old layout placed elements below y=1080 canvas boundary and had
#       disconnected arrows that didn't form a coherent spatial flow)
# ═══════════════════════════════════════════════════════════════════════════════
def scene_attention_scores(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Now we arrive at the heart of the attention mechanism: computing attention scores. "
            "Here is the complete formula: Attention equals the softmax of Query times Key transpose, "
            "divided by the square root of the key dimension, all multiplied by Value. "
            "Step by step: First, we multiply the Query matrix by the transpose of the Key matrix. "
            "This computes similarity scores — how much each token's query matches every other token's key. "
            "Second, we scale by dividing by the square root of the key dimension. This prevents "
            "the dot products from becoming too large, which would push the softmax into regions "
            "with extremely small gradients. Third, we apply softmax to normalize the scores "
            "into a probability distribution — all positive, all summing to one. "
            "Finally, we multiply by the Value matrix. This creates a weighted sum where each token "
            "receives information from other tokens proportional to their attention scores. "
            "The result is the context-aware output."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        hd = heading("Computing Attention Scores", PURPLE)
        sketch(scene, hd, 0.0, 2.0)

        all_elements = [hd]

        formula = equation_text(CX, 140, "Attention(Q,K,V) = softmax(QK^T / √d_k) · V", PURPLE, 32)
        sketch(scene, formula, 1.5, 1.2)
        all_elements.append(formula)

        # ── Step 1: Q × K^T ─────────────────────────────────────────────────
        t = 3.5
        step1_lbl = label("1. Q × K^T (Similarity)", 350, 230, ORANGE, 24, 2)
        sketch(scene, step1_lbl, t, 0.7)
        all_elements.append(step1_lbl)

        q_outline = matrix_outline(150, 285, 4, 3, ORANGE, 30, 5)
        q_cells   = matrix_grid(150, 285, 4, 3, ORANGE, 30, 5)
        sketch(scene, q_outline, t+0.5, 0.6)
        for i, cell in enumerate(q_cells):
            sketch(scene, cell, t+0.7+i*0.02, 0.15)
        all_elements.extend([q_outline] + q_cells)

        mult_txt = label("×", 355, 320, DARK_GRAY, 36, 2)
        sketch(scene, mult_txt, t+1.2, 0.4)
        all_elements.append(mult_txt)

        k_outline = matrix_outline(420, 285, 3, 4, GREEN, 30, 5)
        k_cells   = matrix_grid(420, 285, 3, 4, GREEN, 30, 5)
        sketch(scene, k_outline, t+1.0, 0.6)
        for i, cell in enumerate(k_cells):
            sketch(scene, cell, t+1.2+i*0.02, 0.15)
        all_elements.extend([k_outline] + k_cells)

        arr1 = flow_arrow(605, 320, 755, 320, RED, 3)
        sketch(scene, arr1, t+2.0, 0.5)
        all_elements.append(arr1)

        scores_outline = matrix_outline(785, 285, 4, 4, RED, 30, 5)
        scores_cells   = matrix_grid(785, 285, 4, 4, RED, 30, 5)
        sketch(scene, scores_outline, t+2.3, 0.6)
        for i, cell in enumerate(scores_cells):
            sketch(scene, cell, t+2.5+i*0.015, 0.12)
        scores_lbl = label("Raw Scores", 880, 435, RED, 20, 1)
        sketch(scene, scores_lbl, t+3.0, 0.5)
        all_elements.extend([scores_outline, scores_lbl] + scores_cells)

        # ── Step 2: Scale ÷√d_k ─────────────────────────────────────────────
        t += 3.5
        arr2 = flow_arrow(940, 320, 1000, 320, DARK_GRAY, 2)
        sketch(scene, arr2, t, 0.4)
        all_elements.append(arr2)

        scale_diamond, scale_lbl = operation_node(1055, 320, "÷√d_k", TEAL)
        sketch(scene, scale_diamond, t, 0.7)
        sketch(scene, scale_lbl, t+0.3, 0.5)
        all_elements.extend([scale_diamond, scale_lbl])

        # ── Step 3: Softmax ──────────────────────────────────────────────────
        t += 1.5
        arr3 = flow_arrow(1110, 320, 1155, 320, PURPLE, 2)
        sketch(scene, arr3, t, 0.4)
        all_elements.append(arr3)

        soft_diamond, soft_lbl = operation_node(1210, 320, "softmax", PURPLE)
        sketch(scene, soft_diamond, t, 0.7)
        sketch(scene, soft_lbl, t+0.3, 0.5)
        all_elements.extend([soft_diamond, soft_lbl])

        arr4 = flow_arrow(1265, 320, 1315, 320, PURPLE, 2)
        sketch(scene, arr4, t+0.5, 0.4)
        all_elements.append(arr4)

        # Attention weights matrix
        t += 1.0
        weights_outline = matrix_outline(1325, 285, 4, 4, PURPLE, 30, 5)
        weight_cells = []
        for r in range(4):
            for c in range(4):
                opacity = 0.2 + (0.5 if r == c else 0.1)
                cell = Circle(
                    center=(1325 + c*35 + 15, 285 + r*35 + 15),
                    radius=8,
                    stroke_style=StrokeStyle(color=PURPLE, width=1),
                    fill_style=FillStyle(color=PURPLE, opacity=opacity),
                    sketch_style=SketchStyle(roughness=0.5)
                )
                weight_cells.append(cell)

        sketch(scene, weights_outline, t, 0.6)
        for i, cell in enumerate(weight_cells):
            sketch(scene, cell, t+0.3+i*0.02, 0.15)

        # FIX: weights_lbl y: 420→435; sum_lbl y: 440→462 (were overlapping at 20px apart with 20/16px fonts)
        weights_lbl = label("Attention Weights", 1415, 435, PURPLE, 20, 1)
        sum_lbl     = label("(sum = 1.0)",       1415, 462, GRAY, 16, 1)
        sketch(scene, weights_lbl, t+0.8, 0.5)
        sketch(scene, sum_lbl, t+1.0, 0.4)
        all_elements.extend([weights_outline, weights_lbl, sum_lbl] + weight_cells)

        # ── Step 4: Multiply by V  (FIX: compact right-side layout) ─────────
        # OLD layout had V at y=580 and output at y=720 with a confusing backward
        # arrow and an arr5 that landed in empty space between elements.
        # NEW layout keeps everything in the same horizontal band (y≈285-450):
        #   weights → arrow → multiply_op → arrow → output
        #                           ↑
        #                         V matrix (below multiply op)
        t += 2.0

        # Arrow from weights right edge to multiply op
        arr_w_mult = flow_arrow(1475, 320, 1540, 320, PURPLE, 2)
        sketch(scene, arr_w_mult, t, 0.4)
        all_elements.append(arr_w_mult)

        # Multiply operation diamond
        mult_op, mult_op_lbl = operation_node(1590, 320, "·V", DARK_GREEN)
        sketch(scene, mult_op, t+0.3, 0.6)
        sketch(scene, mult_op_lbl, t+0.5, 0.4)
        all_elements.extend([mult_op, mult_op_lbl])

        # V matrix below multiply op (3×3, small cells to stay compact)
        v_outline = matrix_outline(1555, 420, 3, 3, BLUE, 25, 4)
        v_cells   = matrix_grid(1555, 420, 3, 3, BLUE, 25, 4)
        v_name_lbl = label("V", 1635, 404, BLUE, 18, 1)
        sketch(scene, v_outline, t+0.4, 0.5)
        for i, cell in enumerate(v_cells):
            sketch(scene, cell, t+0.6+i*0.02, 0.12)
        sketch(scene, v_name_lbl, t+0.5, 0.4)
        all_elements.extend([v_outline, v_name_lbl] + v_cells)

        # Arrow from V top up into multiply op
        arr_v_mult = flow_arrow(1591, 420, 1591, 373, BLUE, 2)
        sketch(scene, arr_v_mult, t+0.8, 0.4)
        all_elements.append(arr_v_mult)

        # Arrow from multiply to output
        arr_mult_out = flow_arrow(1643, 320, 1710, 320, DARK_GREEN, 3)
        sketch(scene, arr_mult_out, t+1.0, 0.4)
        all_elements.append(arr_mult_out)

        # Output matrix (4×3, small cells)
        output_outline = matrix_outline(1725, 285, 4, 3, DARK_GREEN, 25, 4)
        output_cells   = matrix_grid(1725, 285, 4, 3, DARK_GREEN, 25, 4)
        output_lbl     = label("Output", 1800, 268, DARK_GREEN, 18, 2)
        sketch(scene, output_outline, t+1.2, 0.6)
        for i, cell in enumerate(output_cells):
            sketch(scene, cell, t+1.4+i*0.015, 0.10)
        sketch(scene, output_lbl, t+1.8, 0.5)
        all_elements.extend([output_outline, output_lbl] + output_cells)

        erase(scene, all_elements, track.end_time - scene.timeline_cursor - 1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE 5  ─  WHY MULTIPLE HEADS  (~75 s)
# FIX: head_configs attention arc targets had wrong coordinates.
#      Old: (1150, 300), (1150, 1000) etc. — referenced wrong positions
#      New: actual token (x, y) positions from token_data
# ═══════════════════════════════════════════════════════════════════════════════
def scene_multiple_heads(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Now we understand single attention — but why do we need MULTIPLE heads? "
            "The answer is that a single attention mechanism can only capture ONE type of relationship. "
            "But language is complex. Consider: 'The animal didn't cross the street because it was too tired.' "
            "The word 'it' could relate to 'animal' — that's the meaning. But it also relates to 'street' — "
            "that's the position. And it relates to 'tired' — that's the state. "
            "Different heads learn to focus on different aspects: one head might track subject-verb relationships, "
            "another tracks pronoun references, another tracks positional patterns, and yet another "
            "tracks semantic categories. With eight, sixteen, or even thirty-two heads, the model can "
            "simultaneously capture many different types of relationships at once. "
            "Each head has its own Query, Key, and Value weight matrices — they learn different projections "
            "that emphasize different aspects of the input."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        hd = heading("Why Multiple Heads?", INDIGO)
        sketch(scene, hd, 0.0, 2.0)

        all_elements = [hd]

        # Token positions at y=190 (enough clearance from heading bottom ~y=102)
        token_data = [
            ("The", 150), ("animal", 300), ("didn't", 450), ("cross", 600),
            ("the", 720), ("street", 860), ("because", 1010),
            ("it", 1160), ("was", 1310), ("tired", 1460)
        ]
        tok_y = 190

        tokens = []
        t = 1.5
        for item in token_data:
            word, x = item[0], item[1]
            col = ORANGE if word == "it" else LIGHT_GRAY
            circle, txt = token_circle(x, tok_y, word, col, radius=35)
            sketch(scene, circle, t, 0.4)
            sketch(scene, txt, t + 0.15, 0.3)
            tokens.extend([circle, txt])
            t += 0.25
        all_elements.extend(tokens)

        t += 1.0
        heads_title = label("Different Heads Learn Different Relationships", CX, 290, INDIGO, 26, 2)
        sketch(scene, heads_title, t, 0.8)
        all_elements.append(heads_title)

        # Actual token x positions for reference:
        # "animal"=300, "because"=1010, "street"=860, "tired"=1460, "it"=1160
        it_x = 1160

        # FIX: target coordinates now match actual token positions in token_data
        head_configs = [
            ("Head 1: Meaning",   RED,    [(300,  tok_y)],                380),  # it→animal
            ("Head 2: Reference", ORANGE, [(300,  tok_y), (1010, tok_y)], 480),  # it→animal,because
            ("Head 3: Position",  GREEN,  [(860,  tok_y)],                580),  # it→street
            ("Head 4: State",     BLUE,   [(1460, tok_y)],                680),  # it→tired
        ]

        head_elements = []
        for i, (name, color, connections, y) in enumerate(head_configs):
            head_node, head_lbl = node_with_label(200, y, name, color, color, size=45)
            sketch(scene, head_node, t + 1.0 + i*0.5, 0.6)
            sketch(scene, head_lbl, t + 1.2 + i*0.5, 0.5)
            head_elements.extend([head_node, head_lbl])

            for target_x, target_y in connections:
                arc_height = 55 + i * 15   # vary height per head to prevent arc overlap
                conn = attention_arc(
                    it_x, tok_y - 35,
                    target_x, target_y - 35,
                    color, height=arc_height
                )
                sketch(scene, conn, t + 1.5 + i*0.5, 0.8)
                head_elements.append(conn)

        all_elements.extend(head_elements)

        # Parallel processing visualization (right side, y=380-700)
        t += 4.0
        parallel_lbl = label("Parallel Processing", 1420, 340, PURPLE, 24, 2)
        sketch(scene, parallel_lbl, t, 0.7)
        all_elements.append(parallel_lbl)

        t += 0.8
        head_nodes = []
        head_xs = [1270, 1380, 1490, 1600]
        for i, x in enumerate(head_xs):
            node, lbl = node_with_label(x, 440, f"H{i+1}", VIOLET, VIOLET, size=40)
            sketch(scene, node, t + i*0.2, 0.5)
            sketch(scene, lbl, t + i*0.2 + 0.1, 0.4)
            head_nodes.extend([node, lbl])

            mini_outline = matrix_outline(x-22, 510, 3, 3, VIOLET, 18, 3)
            mini_cells   = matrix_grid(x-22, 510, 3, 3, VIOLET, 18, 3)
            sketch(scene, mini_outline, t + i*0.2 + 0.3, 0.4)
            for j, cell in enumerate(mini_cells):
                sketch(scene, cell, t + i*0.2 + 0.4 + j*0.01, 0.1)
            head_nodes.extend([mini_outline] + mini_cells)
        all_elements.extend(head_nodes)

        # Concatenation + combined output
        t += 1.5
        concat_arrow = flow_arrow(1430, 580, 1430, 640, GREEN, 3)
        sketch(scene, concat_arrow, t, 0.5)
        all_elements.append(concat_arrow)

        concat_cloud = cloud_shape(1430, 720, 180, 100, GREEN)
        concat_lbl   = label("Combined Output", 1430, 720, GREEN, 22, 2)
        sketch_all(scene, concat_cloud, t + 0.5, 0.6, 0.1)
        sketch(scene, concat_lbl, t + 1.0, 0.5)
        all_elements.extend(concat_cloud + [concat_lbl])

        erase(scene, all_elements, track.end_time - scene.timeline_cursor - 1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE 6  ─  COMPLETE FLOW  (~70 s)
# FIX: completely redesigned layout — old version had elements at y=1140-1200
#      which are beyond the 1080px canvas height.
#      New layout uses a 5-step vertical pipeline fitting within y=160-960.
# ═══════════════════════════════════════════════════════════════════════════════
def scene_complete_flow(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Let's see the complete end-to-end multi-head attention flow. "
            "Step one: Input embeddings enter the module. Step two: Three linear projections "
            "create the Query, Key, and Value matrices. Step three: Each matrix is split "
            "logically across all attention heads. Step four: Each head computes attention independently — "
            "Q times K transpose, scaled, softmax, multiply by V. Step five: The outputs from all heads "
            "are concatenated back together. Step six: A final linear projection combines the head outputs "
            "into the final representation. This output has the same dimensions as the input, "
            "but now each token carries rich contextual information from the entire sequence. "
            "This is what enables transformers to understand long-range dependencies and complex relationships "
            "that previous architectures like RNNs and LSTMs could never capture effectively."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        hd = heading("Complete Multi-Head Attention Flow", BLUE)
        sketch(scene, hd, 0.0, 2.0)

        all_elements = [hd]
        t = 1.5

        # Step numbers as a left-column spine (x=110, font small so they don't crowd content)
        step_spine = [
            ("1. Input",               110, 185, CYAN),
            ("2. Q, K, V Projections", 110, 320, ORANGE),
            ("3. Parallel Heads",      110, 490, INDIGO),
            ("4. Concatenate",         110, 660, GREEN),
            ("5. Output",              110, 830, DARK_GREEN),
        ]
        for txt, x, y, col in step_spine:
            lbl = label(txt, x, y, col, 19, 1)
            sketch(scene, lbl, t, 0.5)
            all_elements.append(lbl)
            t += 0.25

        t += 0.5

        # ── Step 1: Input tokens (y=185) ─────────────────────────────────────
        for i, (word, col) in enumerate(zip(["The", "cat", "sat"], [BLUE, RED, BLUE])):
            c, tx = token_circle(440 + i*110, 185, word, col, radius=30)
            sketch(scene, c, t+i*0.2, 0.4)
            sketch(scene, tx, t+i*0.2+0.1, 0.3)
            all_elements.extend([c, tx])
        t += 1.2

        # Connector arrow step 1→2
        arr_12 = flow_arrow(CX, 228, CX, 285, DARK_GRAY, 2)
        sketch(scene, arr_12, t, 0.4)
        all_elements.append(arr_12)
        t += 0.5

        # ── Step 2: Linear projections (y=320) ───────────────────────────────
        proj_items = [("W_Q→Q", ORANGE), ("W_K→K", GREEN), ("W_V→V", BLUE)]
        for i, (name, col) in enumerate(proj_items):
            x = 380 + i * 240
            node, lbl = operation_node(x, 320, name, col)
            sketch(scene, node, t+i*0.25, 0.55)
            sketch(scene, lbl, t+i*0.25+0.15, 0.45)
            all_elements.extend([node, lbl])
        t += 1.3

        # Connector arrow step 2→3
        arr_23 = flow_arrow(CX, 375, CX, 440, DARK_GRAY, 2)
        sketch(scene, arr_23, t, 0.4)
        all_elements.append(arr_23)
        t += 0.5

        # ── Step 3: Attention heads (y=490) ─────────────────────────────────
        head_xs = [370, 570, 770, 970]
        for i, hx in enumerate(head_xs):
            hcirc = Circle(center=(hx, 490), radius=42,
                           stroke_style=StrokeStyle(color=VIOLET, width=2),
                           fill_style=FillStyle(color=WHITE, opacity=0.9),
                           sketch_style=SketchStyle(roughness=1.5))
            hlbl    = label(f"Head {i+1}", hx, 495, VIOLET, 18, 2)
            hform   = small_label("Attn(Q,K,V)", hx, 540, GRAY, 13)
            sketch(scene, hcirc, t+i*0.2, 0.5)
            sketch(scene, hlbl,  t+i*0.2+0.1, 0.4)
            sketch(scene, hform, t+i*0.2+0.2, 0.3)
            all_elements.extend([hcirc, hlbl, hform])

            # Dashed feed line from projection area to each head
            feed = connection_line(CX, 375, hx, 448, LIGHT_GRAY, 1, True)
            sketch(scene, feed, t+0.3, 0.4)
            all_elements.append(feed)
        t += 1.5

        # Connector arrow step 3→4
        arr_34 = flow_arrow(CX, 538, CX, 610, GREEN, 3)
        sketch(scene, arr_34, t, 0.4)
        all_elements.append(arr_34)
        t += 0.5

        # ── Step 4: Concatenate + W_O (y=660) ───────────────────────────────
        concat_cloud = cloud_shape(CX, 660, 200, 65, GREEN)
        concat_lbl   = label("Concat + W_O", CX, 660, GREEN, 24, 2)
        sketch_all(scene, concat_cloud, t, 0.5, 0.08)
        sketch(scene, concat_lbl, t+0.5, 0.5)
        all_elements.extend(concat_cloud + [concat_lbl])
        t += 1.3

        # Connector arrow step 4→5
        arr_45 = flow_arrow(CX, 710, CX, 775, DARK_GREEN, 3)
        sketch(scene, arr_45, t, 0.4)
        all_elements.append(arr_45)
        t += 0.5

        # ── Step 5: Output tokens (y=830) ────────────────────────────────────
        for i, word in enumerate(["The", "cat", "sat"]):
            c, tx = token_circle(440 + i*110, 830, word, DARK_GREEN, radius=30)
            sketch(scene, c, t+i*0.2, 0.4)
            sketch(scene, tx, t+i*0.2+0.1, 0.3)
            all_elements.extend([c, tx])

        out_note = label("Context-Aware Representations", CX, 900, DARK_GREEN, 22, 1)
        sketch(scene, out_note, t+0.8, 0.6)
        all_elements.append(out_note)
        t += 1.5

        # Closing note (y=975 — just within canvas)
        note = label("Global receptive field  ·  Parallelizable  ·  GPU-efficient", CX, 970, GRAY, 21, 1)
        sketch(scene, note, t, 0.7)
        all_elements.append(note)

        erase(scene, all_elements, track.end_time - scene.timeline_cursor - 1.5)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE 7  ─  KEY INSIGHTS  (~50 s)
# FIX: desc_cloud size reduced (180,60→150,40) and moved down (y+120→y+145)
#      to prevent overlap with title_lbl (y+70) above and row-2 icons below.
# FIX: row-2 insight y moved 450→480 to open up clearance with row-1 desc clouds.
# FIX: closing cloud size reduced (500,100→250,65), moved to y=760 to prevent
#      overlap with row-2 desc clouds that extended to y≈665.
# ═══════════════════════════════════════════════════════════════════════════════
def scene_key_insights(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Let's summarize the key insights. Multi-head attention enables parallel computation — "
            "all heads process simultaneously, making transformers highly parallelizable and perfect for GPU acceleration. "
            "It captures diverse relationships — different heads learn different linguistic and semantic patterns. "
            "The scaled dot-product prevents gradient vanishing, keeping training stable even in deep networks. "
            "Most importantly, attention creates global receptive fields — every token can directly attend "
            "to every other token, regardless of distance. This solves the long-range dependency problem "
            "that plagued RNNs and LSTMs. Understanding multi-head attention is essential for understanding "
            "modern AI — it is the foundation of GPT, BERT, T5, and every major language model in use today."
        ),
        voice=VOICE, rate=RATE,
    ) as track:
        hd = heading("Key Insights", GREEN)
        sketch(scene, hd, 0.0, 2.0)

        all_elements = [hd]

        # Row 1 (y=215): 3 insights;  Row 2 (y=480): 2 insights
        # FIX: row 2 y was 450 → 480 to create clearance below row-1 desc clouds
        insights = [
            ("Parallel", "All heads process simultaneously",           ORANGE, 250,  215, "||"),
            ("Diverse",  "Different heads, different patterns",         BLUE,   660,  215, "*"),
            ("Stable",   "Scaled dot-product prevents vanishing",       PURPLE, 1070, 215, "~"),
            ("Global",   "Every token sees all others",                 GREEN,  380,  480, "O"),  # FIX y 450→480
            ("GPU",      "Matrix ops highly optimized",                 TEAL,   870,  480, "#"),  # FIX y 450→480
        ]

        t = 1.5
        for title, desc, col, x, y, icon_txt in insights:
            # Icon circle
            icon, _ = icon_circle(x, y, icon_txt, col, 40)
            sketch(scene, icon, t, 0.5)
            all_elements.append(icon)

            # Title label  (FIX: offset +60→+75 for clearance from icon bottom)
            title_lbl = label(title, x, y + 75, col, 26, 2)
            sketch(scene, title_lbl, t + 0.2, 0.5)
            all_elements.append(title_lbl)

            # Description cloud  (FIX: size 180,60→150,40; center y+120→y+145)
            desc_cloud = cloud_shape(x, y + 145, 150, 40, col)
            desc_lbl   = label(desc, x, y + 145, DARK_GRAY, 17, 1)
            sketch_all(scene, desc_cloud, t + 0.4, 0.5, 0.05)
            sketch(scene, desc_lbl, t + 0.6, 0.5)
            all_elements.extend(desc_cloud + [desc_lbl])

            t += 0.6

        # Closing statement
        # FIX: cloud size 500,100→250,65; y 720→760 to stay below row-2 desc clouds (~y=665)
        t += 1.0
        closing_cloud = cloud_shape(CX, 760, 250, 65, INDIGO)
        closing       = label("Multi-Head Attention: The Foundation of Modern AI", CX, 760, INDIGO, 30, 2)
        sketch_all(scene, closing_cloud, t, 0.8, 0.1)
        sketch(scene, closing, t + 0.5, 0.8)
        all_elements.extend(closing_cloud + [closing])

        # Foundation models (y=890 — safely below closing cloud bottom ~y=830)
        t += 1.5
        models_lbl = label("GPT · BERT · T5 · Claude · Gemini · Llama", CX, 895, GRAY, 24, 1)
        sketch(scene, models_lbl, t, 0.7)
        all_elements.append(models_lbl)

        fadeout(scene, all_elements, track.end_time - scene.timeline_cursor - 1.5)


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    output_path = "output/multihead_attention.mp4"

    scene = Scene(
        width=1920,
        height=1080,
        fps=FPS,
        background_color=WHITE,
    )

    tts = EdgeTTSProvider()

    scene_title(scene, tts)
    scene_attention_intuition(scene, tts)
    scene_qkv_explained(scene, tts)
    scene_attention_scores(scene, tts)
    scene_multiple_heads(scene, tts)
    scene_complete_flow(scene, tts)
    scene_key_insights(scene, tts)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scene.render(output_path)
    print(f"Rendered: {output_path}")


if __name__ == "__main__":
    main()