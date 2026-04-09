import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts or uv add --dev edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation, ReplacementTransform
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, Math, Rectangle, Table
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, ORANGE, PURPLE, RED, WHITE,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_ORANGE, PASTEL_PURPLE, PASTEL_RED, PASTEL_YELLOW
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "cnn_rnn_masterclass"
AUDIO_PATH = OUTPUT_DIR / "cnn_rnn_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "cnn_rnn_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "-10%" # Slower pace for a long, masterclass feel
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome to a comprehensive masterclass on deep learning architectures. "
    "Today, we are undertaking a massive deep dive into the two most important specialized neural networks ever created. "
    "First, Convolutional Neural Networks, or CNNs, which gave AI the ability to see and understand the visual world. "
    "And second, Recurrent Neural Networks, or RNNs, including LSTMs and GRUs, which gave AI the ability to process time, sequence, and language. "
    
    "<bookmark mark='cnn_prob'/> Let us begin with vision. Why do we need a special architecture for images? "
    "Imagine feeding a high-definition image into a standard, fully connected neural network. "
    "A 1080p color image has over 6 million individual data points. If your first hidden layer has just one thousand neurons, "
    "you are forcing the network to calculate 6 billion weights instantly. The memory requirement is astronomically prohibitive. "
    "Furthermore, a standard network flattens the image into a 1D line. This destroys all 2D spatial relationships. "
    "A cat's ear is made of pixels that are spatially next to each other. If we flatten the image, we lose that vital geometric structure. "
    
    "<bookmark mark='cnn_conv'/> To solve this, researchers introduced the Convolution Operation. "
    "Instead of connecting every pixel to every neuron, a CNN uses a tiny matrix called a Filter, or a Kernel. "
    "Typically, this is a 3 by 3 grid of weights. The network slides, or 'convolves', this tiny filter across the entire image, pixel by pixel. "
    "At every single stop, it performs a dot product. It multiplies the filter's weights by the pixels directly underneath it, and sums them into a single number. "
    "<bookmark mark='cnn_features'/> What is the magical result of this? Feature extraction. "
    "By learning the exact right weights, a filter becomes an edge detector. It might light up when it sees a vertical line, or a horizontal curve. "
    "As we stack layer upon layer of these convolutions, the network combines simple edges into textures, textures into shapes, and shapes into complex objects like faces and cars. "
    "Because the filter slides across the whole image, a cat recognized in the top left corner will still be recognized if it moves to the bottom right. This is called Translation Invariance. "
    
    "<bookmark mark='cnn_pool'/> However, as we extract thousands of feature maps, our data size explodes. We need to aggressively downsample the spatial dimensions. "
    "Enter the Pooling layer. The most dominant technique is Max Pooling. "
    "Imagine a 2 by 2 window sliding over our feature map. Instead of doing complex math, Max Pooling simply looks at the four numbers in the window, keeps the highest value, and throws the rest in the trash. "
    "This halves the height and halves the width of the data, dramatically reducing the computational load, while preserving the most highly activated, dominant features in that region. "
    "A CNN is simply a repeating sandwich of Convolutions to extract features, and Pooling to compress them, ending with a standard classification layer. "
    
    "<bookmark mark='rnn_intro'/> But what if our data is not a static grid of pixels? What if it unfolds over time? "
    "Think of a sentence, a spoken audio wavelength, or the daily fluctuations of the stock market. "
    "Standard feed-forward networks have severe amnesia. They process each input in total isolation. They have zero concept of time or memory. "
    
    "<bookmark mark='rnn_loop'/> Recurrent Neural Networks, or RNNs, solve this by introducing a temporal loop. "
    "When an RNN processes time step 1, it generates a prediction, but crucially, it also generates a 'Hidden State'. "
    "This hidden state acts as the network's short-term memory. When time step 2 arrives, the RNN takes the new input AND the hidden state from step 1. "
    "<bookmark mark='rnn_unroll'/> We can visualize this by 'unrolling' the network across time. "
    "Input 1 goes into Cell 1, which passes its hidden state to Cell 2. Input 2 goes into Cell 2, which passes its state to Cell 3, forming an unbroken chain of temporal context. "
    
    "<bookmark mark='rnn_vanish'/> In theory, this is perfect. In reality, standard RNNs suffer from a catastrophic mathematical flaw known as the Vanishing Gradient Problem. "
    "During training, the network uses Backpropagation Through Time to update its weights. The error gradient must flow backwards through every single time step. "
    "Because the gradient is repeatedly multiplied by weight matrices, if those numbers are less than 1, the gradient shrinks exponentially. "
    "Within 10 or 20 steps, the gradient vanishes to zero. The network completely forgets early context. "
    "If a paragraph begins with 'I was born in France', and ends 100 words later with 'I speak fluent...', a standard RNN cannot remember 'France' to predict 'French'. "
    
    "<bookmark mark='lstm_intro'/> To cure this catastrophic amnesia, Sepp Hochreiter and Jürgen Schmidhuber created a masterpiece in 1997: The Long Short-Term Memory network, or LSTM. "
    "LSTMs fundamentally redesign the internal structure of the RNN cell. They introduce an entirely new pathway called the 'Cell State'. "
    "Think of the Cell State as an express highway, or a conveyor belt, running straight down the entire length of the sequence. "
    "It carries long-term memory with minimal interference, completely bypassing the vanishing gradient problem. "
    
    "<bookmark mark='lstm_gates'/> How does the LSTM protect this conveyor belt? It uses three mathematical valves called Gates, built using sigmoid neural layers. "
    "First is the Forget Gate. It looks at the new input and the old hidden state, and decides what outdated information on the conveyor belt should be erased. "
    "Second is the Input Gate. It decides what brand-new, relevant information from the current step should be written onto the conveyor belt. "
    "Third is the Output Gate. It filters the conveyor belt to decide exactly what the cell should output as a prediction, and what it should pass as the hidden state to the next cell. "
    "By explicitly learning what to keep, what to throw away, and what to read, LSTMs can remember context across thousands of time steps. "
    
    "<bookmark mark='gru'/> Years later, researchers created a streamlined variant called the Gated Recurrent Unit, or GRU. "
    "The GRU simplifies the architecture by merging the Cell State and Hidden State into one pathway. "
    "It also merges the forget and input gates into a single 'Update Gate'. "
    "Because it has fewer tensor operations, a GRU trains significantly faster and uses less memory, while often matching the LSTM's performance on a vast majority of sequential tasks. "
    
    "<bookmark mark='summary'/> Let us summarize this expansive masterclass. "
    "When your data contains 2D spatial relationships, like pixels in photography or medical imaging, rely on Convolutional Neural Networks. They use filters to find patterns, and pooling to compress them. "
    "When your data flows sequentially through time, like written text, spoken audio, or financial charts, rely on Recurrent Neural Networks. "
    "Specifically, use LSTMs or GRUs to defeat the vanishing gradient problem and allow your AI to master long-term memory. "
    "Thank you for joining this deep dive into the architecture of modern AI."
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


# ----- Drawing Helpers -----

def make_title(text: str, *, y: float, color: tuple[float, float, float] = BLACK) -> Text:
    return Text(text, position=(960, y), font_size=80, font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=color, width=4.0), sketch_style=SKETCH)

def make_body(text: str, *, x: float = 960, y: float, color: tuple[float, float, float] = BLACK, align: str = "center", font_size: int = 48) -> Text:
    return Text(text, position=(x, y), font_size=font_size, font_name=FONT_NAME,
                stroke_style=StrokeStyle(color=color, width=3.5), sketch_style=SKETCH, align=align)

def make_eraser(objects_to_erase: list, scene: Scene, *, start_time: float, duration: float = 1.2) -> None:
    eraser = Eraser(objects_to_erase=objects_to_erase, drawable_cache=scene.drawable_cache,
                    glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15})
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)

def create_grid(x_start: float, y_start: float, rows: int, cols: int, cell_size: float, 
                fill_color: FillStyle, stroke: StrokeStyle, highlight_cells: list[tuple[int, int]] | None = None, highlight_fill: FillStyle | None = None) -> list:
    drawables =[]
    for r in range(rows):
        for c in range(cols):
            x = x_start + c * cell_size
            y = y_start + r * cell_size
            f_style = highlight_fill if (highlight_cells and (r, c) in highlight_cells) else fill_color
            rect = Rectangle(top_left=(x, y), width=cell_size, height=cell_size, stroke_style=stroke, fill_style=f_style, sketch_style=SKETCH)
            drawables.append(rect)
    return drawables


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()

def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        # Bookmarks
        intro_start = tracker.bookmark_time("intro")
        cnn_prob_start = tracker.bookmark_time("cnn_prob")
        cnn_conv_start = tracker.bookmark_time("cnn_conv")
        cnn_features_start = tracker.bookmark_time("cnn_features")
        cnn_pool_start = tracker.bookmark_time("cnn_pool")
        
        rnn_intro_start = tracker.bookmark_time("rnn_intro")
        rnn_loop_start = tracker.bookmark_time("rnn_loop")
        rnn_unroll_start = tracker.bookmark_time("rnn_unroll")
        rnn_vanish_start = tracker.bookmark_time("rnn_vanish")
        
        lstm_intro_start = tracker.bookmark_time("lstm_intro")
        lstm_gates_start = tracker.bookmark_time("lstm_gates")
        gru_start = tracker.bookmark_time("gru")
        summary_start = tracker.bookmark_time("summary")

        stroke_thick = StrokeStyle(color=BLACK, width=4.0)
        stroke_thin = StrokeStyle(color=BLACK, width=2.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Deep Learning Masterclass", y=300, color=BLUE)
        intro_sub1 = make_body("Convolutional Neural Networks (CNNs) - Space / Images", y=500, color=ORANGE, font_size=56)
        intro_sub2 = make_body("Recurrent Neural Networks (RNNs) - Time / Sequences", y=650, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=2.0), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 5.0, duration=2.0), drawable=intro_sub1)
        scene.add(SketchAnimation(start_time=intro_start + 10.0, duration=2.0), drawable=intro_sub2)

        intro_drawables = [intro_title, intro_sub1, intro_sub2]

        # ---------------------------------------------------------
        # SECTION 2: CNN Problem
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=cnn_prob_start - 1.2)
        
        prob_title = make_title("The Problem with Images", y=120, color=RED)
        
        img_box = Rectangle(top_left=(300, 300), width=400, height=400, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        img_label = make_body("1920 x 1080 Image\n(6.2 Million Pixels)", x=500, y=500, color=BLACK)
        
        arr_flat = Arrow(start_point=(750, 500), end_point=(950, 500), stroke_style=stroke_thick, sketch_style=SKETCH)
        
        flat_box = Rectangle(top_left=(1000, 200), width=100, height=700, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), sketch_style=SKETCH)
        flat_label = make_body("Flattened 1D Line", x=1250, y=500, color=RED)
        
        destroy_label = make_body("Destroys 2D Spatial Structure & Requires Billions of Weights", x=960, y=950, color=RED, font_size=56)

        scene.add(SketchAnimation(start_time=cnn_prob_start + 0.5, duration=1.5), drawable=prob_title)
        scene.add(SketchAnimation(start_time=cnn_prob_start + 3.0, duration=1.5), drawable=img_box)
        scene.add(SketchAnimation(start_time=cnn_prob_start + 4.5, duration=1.0), drawable=img_label)
        
        scene.add(SketchAnimation(start_time=cnn_prob_start + 18.0, duration=1.0), drawable=arr_flat)
        scene.add(SketchAnimation(start_time=cnn_prob_start + 19.0, duration=1.5), drawable=flat_box)
        scene.add(SketchAnimation(start_time=cnn_prob_start + 20.5, duration=1.0), drawable=flat_label)
        scene.add(SketchAnimation(start_time=cnn_prob_start + 22.0, duration=2.0), drawable=destroy_label)

        prob_drawables =[prob_title, img_box, img_label, arr_flat, flat_box, flat_label, destroy_label]

        # ---------------------------------------------------------
        # SECTION 3: CNN Convolutions
        # ---------------------------------------------------------
        make_eraser(prob_drawables, scene, start_time=cnn_conv_start - 1.2)
        
        conv_title = make_title("The Convolution Operation", y=100, color=GREEN)
        
        # 5x5 Image grid
        img_grid = create_grid(200, 300, 5, 5, 80, FillStyle(color=WHITE), stroke_thin, highlight_cells=[(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)], highlight_fill=FillStyle(color=PASTEL_BLUE, opacity=0.5))
        img_grid_label = make_body("Image Pixels", x=400, y=750, color=BLACK)
        
        # 3x3 Filter
        filter_grid = create_grid(800, 400, 3, 3, 60, FillStyle(color=PASTEL_ORANGE, opacity=0.8), stroke_thin)
        filter_label = make_body("3x3 Filter (Weights)", x=890, y=650, color=ORANGE)
        dot_math = Math(r"Dot Product ($\sum$)", position=(890, 300), font_size=56, stroke_style=StrokeStyle(color=BLACK, width=2))
        
        # Result grid
        res_grid = create_grid(1300, 400, 3, 3, 80, FillStyle(color=WHITE), stroke_thin, highlight_cells=[(1,1)], highlight_fill=FillStyle(color=PASTEL_GREEN, opacity=0.8))
        res_label = make_body("Feature Map", x=1420, y=700, color=GREEN)
        
        arr_c1 = Arrow(start_point=(600, 450), end_point=(750, 450), stroke_style=stroke_thick, sketch_style=SKETCH)
        arr_c2 = Arrow(start_point=(1050, 450), end_point=(1250, 450), stroke_style=stroke_thick, sketch_style=SKETCH)
        
        feat_text1 = make_body("Filters act as Edge Detectors", x=960, y=850, color=BLUE, font_size=56)
        feat_text2 = make_body("Translation Invariance: It finds patterns anywhere!", x=960, y=950, color=PURPLE, font_size=56)

        scene.add(SketchAnimation(start_time=cnn_conv_start + 0.5, duration=1.0), drawable=conv_title)
        
        delay = cnn_conv_start + 3.0
        for rect in img_grid:
            scene.add(SketchAnimation(start_time=delay, duration=0.1), drawable=rect)
            delay += 0.05
        scene.add(SketchAnimation(start_time=delay, duration=0.5), drawable=img_grid_label)
        
        delay += 3.0
        for rect in filter_grid:
            scene.add(SketchAnimation(start_time=delay, duration=0.1), drawable=rect)
            delay += 0.1
        scene.add(SketchAnimation(start_time=delay, duration=0.5), drawable=filter_label)
        
        scene.add(SketchAnimation(start_time=delay + 2.0, duration=1.0), drawable=arr_c1)
        scene.add(SketchAnimation(start_time=delay + 3.0, duration=1.5), drawable=dot_math)
        scene.add(SketchAnimation(start_time=delay + 4.0, duration=1.0), drawable=arr_c2)
        
        delay += 5.0
        for rect in res_grid:
            scene.add(SketchAnimation(start_time=delay, duration=0.1), drawable=rect)
            delay += 0.1
        scene.add(SketchAnimation(start_time=delay, duration=0.5), drawable=res_label)
        
        scene.add(SketchAnimation(start_time=cnn_features_start + 1.0, duration=1.5), drawable=feat_text1)
        scene.add(SketchAnimation(start_time=cnn_features_start + 14.0, duration=1.5), drawable=feat_text2)

        conv_drawables =[conv_title, img_grid_label, filter_label, dot_math, res_label, arr_c1, arr_c2, feat_text1, feat_text2] + img_grid + filter_grid + res_grid

        # ---------------------------------------------------------
        # SECTION 4: CNN Pooling
        # ---------------------------------------------------------
        make_eraser(conv_drawables, scene, start_time=cnn_pool_start - 1.2)
        
        pool_title = make_title("Max Pooling", y=120, color=ORANGE)
        
        # 4x4 Grid
        p_img_grid = create_grid(300, 300, 4, 4, 100, FillStyle(color=WHITE), stroke_thin, highlight_cells=[(0,0),(0,1),(1,0),(1,1)], highlight_fill=FillStyle(color=PASTEL_RED, opacity=0.5))
        p_math = Math(r"$\max(3, 1, 8, 2) = 8$", position=(500, 800), font_size=56, stroke_style=StrokeStyle(color=RED, width=2))
        
        arr_p1 = Arrow(start_point=(800, 500), end_point=(1100, 500), stroke_style=StrokeStyle(color=ORANGE, width=8), sketch_style=SKETCH)
        
        # 2x2 Grid (Result)
        p_res_grid = create_grid(1200, 400, 2, 2, 100, FillStyle(color=WHITE), stroke_thin, highlight_cells=[(0,0)], highlight_fill=FillStyle(color=PASTEL_RED, opacity=0.8))
        res_math = Math(r"$8$", position=(1250, 450), font_size=56, stroke_style=StrokeStyle(color=WHITE, width=2))
        
        pool_text = make_body("Halves the dimensions, saves computation, keeps dominant features.", x=960, y=950, color=BLACK, font_size=56)

        scene.add(SketchAnimation(start_time=cnn_pool_start + 0.5, duration=1.0), drawable=pool_title)
        
        delay = cnn_pool_start + 6.0
        for rect in p_img_grid:
            scene.add(SketchAnimation(start_time=delay, duration=0.1), drawable=rect)
            delay += 0.05
            
        scene.add(SketchAnimation(start_time=cnn_pool_start + 11.0, duration=1.5), drawable=p_math)
        scene.add(SketchAnimation(start_time=cnn_pool_start + 13.0, duration=1.0), drawable=arr_p1)
        
        delay = cnn_pool_start + 15.0
        for rect in p_res_grid:
            scene.add(SketchAnimation(start_time=delay, duration=0.1), drawable=rect)
            delay += 0.1
        scene.add(SketchAnimation(start_time=delay, duration=0.5), drawable=res_math)
        
        scene.add(SketchAnimation(start_time=cnn_pool_start + 18.0, duration=2.0), drawable=pool_text)

        pool_drawables =[pool_title, p_math, arr_p1, res_math, pool_text] + p_img_grid + p_res_grid

        # ---------------------------------------------------------
        # SECTION 5: RNN Intro & Unrolling
        # ---------------------------------------------------------
        make_eraser(pool_drawables, scene, start_time=rnn_intro_start - 1.2)
        
        rnn_title = make_title("Recurrent Neural Networks (RNNs)", y=120, color=PURPLE)
        
        seq_text = make_body("Data over time: 'The', 'weather', 'is', 'beautiful'", x=960, y=250, color=BLACK, font_size=56)
        
        # RNN Loop representation
        loop_circle = Circle(center=(300, 600), radius=100, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), sketch_style=SKETCH)
        loop_text = make_body("RNN", x=300, y=600, color=BLACK, font_size=56)
        loop_arrow = Curve(points=[(300, 480), (350, 430), (400, 480), (400, 550), (380, 600)], stroke_style=StrokeStyle(color=RED, width=5), sketch_style=SKETCH)
        
        arr_unroll = Arrow(start_point=(500, 600), end_point=(700, 600), stroke_style=StrokeStyle(color=BLACK, width=6), sketch_style=SKETCH)
        unroll_text = make_body("Unrolled across time", x=600, y=550, color=DARK_GRAY, font_size=40)
        
        # Unrolled Cells
        c1 = Rectangle(top_left=(800, 500), width=150, height=150, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.5), sketch_style=SKETCH)
        c2 = Rectangle(top_left=(1200, 500), width=150, height=150, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.5), sketch_style=SKETCH)
        c3 = Rectangle(top_left=(1600, 500), width=150, height=150, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.5), sketch_style=SKETCH)
        
        # Inputs & Hidden States
        t_arr1 = Arrow(start_point=(875, 800), end_point=(875, 660), stroke_style=stroke_thick)
        t_arr2 = Arrow(start_point=(1275, 800), end_point=(1275, 660), stroke_style=stroke_thick)
        t_arr3 = Arrow(start_point=(1675, 800), end_point=(1675, 660), stroke_style=stroke_thick)
        
        t1 = make_body("x_1 ('The')", x=875, y=850, font_size=40)
        t2 = make_body("x_2 ('weather')", x=1275, y=850, font_size=40)
        t3 = make_body("x_3 ('is')", x=1675, y=850, font_size=40)
        
        h_arr1 = Arrow(start_point=(960, 575), end_point=(1190, 575), stroke_style=StrokeStyle(color=BLUE, width=6))
        h_arr2 = Arrow(start_point=(1360, 575), end_point=(1590, 575), stroke_style=StrokeStyle(color=BLUE, width=6))
        
        h1 = make_body("Hidden State (h_1)", x=1075, y=520, color=BLUE, font_size=36)
        h2 = make_body("Hidden State (h_2)", x=1475, y=520, color=BLUE, font_size=36)

        scene.add(SketchAnimation(start_time=rnn_intro_start + 0.5, duration=1.0), drawable=rnn_title)
        scene.add(SketchAnimation(start_time=rnn_intro_start + 4.0, duration=1.5), drawable=seq_text)
        
        scene.add(SketchAnimation(start_time=rnn_loop_start + 0.5, duration=1.0), drawable=loop_circle)
        scene.add(SketchAnimation(start_time=rnn_loop_start + 1.0, duration=0.5), drawable=loop_text)
        scene.add(SketchAnimation(start_time=rnn_loop_start + 4.0, duration=1.0), drawable=loop_arrow)
        
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 0.5, duration=1.0), drawable=arr_unroll)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 0.5, duration=1.0), drawable=unroll_text)
        
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 3.0, duration=1.0), drawable=c1)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 3.5, duration=0.5), drawable=t_arr1)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 3.5, duration=0.5), drawable=t1)
        
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 6.0, duration=1.0), drawable=h_arr1)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 6.0, duration=0.5), drawable=h1)
        
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 7.5, duration=1.0), drawable=c2)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 8.0, duration=0.5), drawable=t_arr2)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 8.0, duration=0.5), drawable=t2)
        
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 10.0, duration=1.0), drawable=h_arr2)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 10.0, duration=0.5), drawable=h2)
        
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 11.5, duration=1.0), drawable=c3)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 12.0, duration=0.5), drawable=t_arr3)
        scene.add(SketchAnimation(start_time=rnn_unroll_start + 12.0, duration=0.5), drawable=t3)

        rnn_drawables =[rnn_title, seq_text, loop_circle, loop_text, loop_arrow, arr_unroll, unroll_text,
                         c1, c2, c3, t_arr1, t_arr2, t_arr3, t1, t2, t3, h_arr1, h_arr2, h1, h2]

        # ---------------------------------------------------------
        # SECTION 6: Vanishing Gradient
        # ---------------------------------------------------------
        # Just add a massive red arrow shrinking backwards over the unrolled network
        v_arr1 = Arrow(start_point=(1475, 400), end_point=(1300, 400), stroke_style=StrokeStyle(color=RED, width=12))
        v_arr2 = Arrow(start_point=(1075, 420), end_point=(900, 420), stroke_style=StrokeStyle(color=RED, width=4))
        v_arr3 = Arrow(start_point=(675, 440), end_point=(500, 440), stroke_style=StrokeStyle(color=RED, width=1))
        
        v_text = make_body("VANISHING GRADIENT: Memory Shrinks Exponentially to Zero!", x=960, y=200, color=RED, font_size=64)

        scene.add(SketchAnimation(start_time=rnn_vanish_start + 4.0, duration=1.0), drawable=v_text)
        scene.add(SketchAnimation(start_time=rnn_vanish_start + 12.0, duration=1.0), drawable=v_arr1)
        scene.add(SketchAnimation(start_time=rnn_vanish_start + 14.0, duration=1.0), drawable=v_arr2)
        scene.add(SketchAnimation(start_time=rnn_vanish_start + 16.0, duration=1.0), drawable=v_arr3)

        rnn_drawables.extend([v_arr1, v_arr2, v_arr3, v_text])

        # ---------------------------------------------------------
        # SECTION 7: LSTM Cell
        # ---------------------------------------------------------
        make_eraser(rnn_drawables, scene, start_time=lstm_intro_start - 1.2)
        
        lstm_title = make_title("Long Short-Term Memory (LSTM)", y=100, color=GREEN)
        
        # Giant LSTM Box
        lstm_box = Rectangle(top_left=(500, 250), width=900, height=600, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.1), sketch_style=SKETCH)
        
        # Conveyor Belt (Cell State)
        c_line = Line(start=(300, 350), end=(1600, 350), stroke_style=StrokeStyle(color=BLUE, width=12), sketch_style=SKETCH)
        c_label = make_body("Cell State (The Conveyor Belt)", x=960, y=280, color=BLUE, font_size=48)
        
        # Hidden State line (bottom)
        h_line_in = Line(start=(300, 750), end=(600, 750), stroke_style=stroke_thin, sketch_style=SKETCH)
        h_line_out = Line(start=(1300, 750), end=(1600, 750), stroke_style=stroke_thin, sketch_style=SKETCH)
        
        # Gates
        g_forget = FlowchartProcess("Forget\nGate", top_left=(600, 500), width=150, height=100, font_size=32, fill_style=FillStyle(color=PASTEL_RED, opacity=0.6), stroke_style=stroke_thin)
        g_input = FlowchartProcess("Input\nGate", top_left=(850, 500), width=150, height=100, font_size=32, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.6), stroke_style=stroke_thin)
        g_output = FlowchartProcess("Output\nGate", top_left=(1150, 500), width=150, height=100, font_size=32, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.6), stroke_style=stroke_thin)
        
        arr_f = Arrow(start_point=(675, 500), end_point=(675, 360), stroke_style=StrokeStyle(color=RED, width=5))
        arr_i = Arrow(start_point=(925, 500), end_point=(925, 360), stroke_style=StrokeStyle(color=BLUE, width=5))
        arr_o = Arrow(start_point=(1225, 500), end_point=(1225, 360), stroke_style=StrokeStyle(color=ORANGE, width=5))

        # Operators on conveyor belt
        op_mult = Circle(center=(675, 350), radius=25, stroke_style=stroke_thick, fill_style=FillStyle(color=WHITE), sketch_style=SKETCH)
        op_add = Circle(center=(925, 350), radius=25, stroke_style=stroke_thick, fill_style=FillStyle(color=WHITE), sketch_style=SKETCH)
        
        mult_text = make_body("X", x=675, y=350, font_size=36)
        add_text = make_body("+", x=925, y=350, font_size=36)

        scene.add(SketchAnimation(start_time=lstm_intro_start + 0.5, duration=1.0), drawable=lstm_title)
        scene.add(SketchAnimation(start_time=lstm_intro_start + 5.0, duration=1.5), drawable=lstm_box)
        
        scene.add(SketchAnimation(start_time=lstm_intro_start + 12.0, duration=2.0), drawable=c_line)
        scene.add(SketchAnimation(start_time=lstm_intro_start + 14.0, duration=1.0), drawable=c_label)
        
        scene.add(SketchAnimation(start_time=lstm_intro_start + 15.0, duration=0.5), drawable=h_line_in)
        scene.add(SketchAnimation(start_time=lstm_intro_start + 15.0, duration=0.5), drawable=h_line_out)

        scene.add(SketchAnimation(start_time=lstm_gates_start + 3.0, duration=1.0), drawable=g_forget)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 5.0, duration=1.0), drawable=arr_f)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 5.5, duration=0.5), drawable=op_mult)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 5.5, duration=0.5), drawable=mult_text)
        
        scene.add(SketchAnimation(start_time=lstm_gates_start + 11.0, duration=1.0), drawable=g_input)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 13.0, duration=1.0), drawable=arr_i)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 13.5, duration=0.5), drawable=op_add)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 13.5, duration=0.5), drawable=add_text)
        
        scene.add(SketchAnimation(start_time=lstm_gates_start + 19.0, duration=1.0), drawable=g_output)
        scene.add(SketchAnimation(start_time=lstm_gates_start + 22.0, duration=1.0), drawable=arr_o)

        lstm_drawables =[lstm_title, lstm_box, c_line, c_label, h_line_in, h_line_out, 
                          g_forget, g_input, g_output, arr_f, arr_i, arr_o, op_mult, op_add, mult_text, add_text]

        # ---------------------------------------------------------
        # SECTION 8: GRU
        # ---------------------------------------------------------
        make_eraser(lstm_drawables, scene, start_time=gru_start - 1.2)
        
        gru_title = make_title("Gated Recurrent Unit (GRU)", y=200, color=ORANGE)
        gru_text1 = make_body("Merged Cell State + Hidden State", x=960, y=400, color=BLACK, font_size=64)
        gru_text2 = make_body("Forget + Input Gate = 'Update Gate'", x=960, y=550, color=BLUE, font_size=64)
        gru_text3 = make_body("Faster Training • Less Memory • Near LSTM Performance", x=960, y=800, color=GREEN, font_size=64)

        scene.add(SketchAnimation(start_time=gru_start + 0.5, duration=1.0), drawable=gru_title)
        scene.add(SketchAnimation(start_time=gru_start + 5.0, duration=1.5), drawable=gru_text1)
        scene.add(SketchAnimation(start_time=gru_start + 10.0, duration=1.5), drawable=gru_text2)
        scene.add(SketchAnimation(start_time=gru_start + 18.0, duration=2.0), drawable=gru_text3)

        gru_drawables = [gru_title, gru_text1, gru_text2, gru_text3]

        # ---------------------------------------------------------
        # SECTION 9: Summary
        # ---------------------------------------------------------
        make_eraser(gru_drawables, scene, start_time=summary_start - 1.2)
        
        sum_title = make_title("Architecture Masterclass Summary", y=150, color=BLACK)
        
        sum_table = Table(
            data=[
                ["Architecture", "Best Used For", "Key Mechanisms"],["CNN", "2D Space / Images / Vision", "Convolutions & Max Pooling"],["RNN", "1D Time / Sequences / Text", "Hidden States (Short-Term Memory)"],["LSTM / GRU", "Long-Term Temporal Data", "Cell States & Gating Mechanisms"]
            ],
            top_left=(150, 350),
            col_widths=[300, 600, 700],
            row_heights=[100, 150, 150, 150],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=stroke_thick,
            sketch_style=SKETCH
        )
        
        outro_text = make_body("Thank you for joining this deep dive!", y=950, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 3.0, duration=4.0), drawable=sum_table)
        scene.add(SketchAnimation(start_time=tracker.end_time - 3.0, duration=1.5), drawable=outro_text)

        return tracker.end_time + 1.5

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering masterclass whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")

if __name__ == "__main__":
    main()