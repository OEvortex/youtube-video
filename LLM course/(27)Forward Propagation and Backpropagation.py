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

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation, ReplacementTransform
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, Math, Table
from handanim.stylings.color import (
    BLACK, BLUE, ORANGE, RED, WHITE, GREEN, PURPLE, 
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_RED, PASTEL_ORANGE, PASTEL_PURPLE, GRAY, DARK_GRAY, LIGHT_GRAY
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "backprop"
AUDIO_PATH = OUTPUT_DIR / "backprop_deep_dive_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "backprop_deep_dive_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='intro'/> Welcome back! Today we are exploring the heartbeat of neural networks: Forward Propagation and Backpropagation. "
    "<bookmark mark='fwd_intro'/> Think of a neural network learning like a student taking a test. First, the student makes a guess. This is Forward Propagation. "
    "<bookmark mark='fwd_flow'/> Data flows forward from the input layer, through the hidden layers, to the output layer. Each neuron multiplies inputs by weights, adds a bias, and applies an activation function to generate a prediction. "
    "<bookmark mark='loss'/> But how do we know if the prediction is right? We use a Loss Function. It compares our network's guess to the actual true answer, calculating the total error. "
    "<bookmark mark='back_intro'/> If Forward Propagation is taking the test, Backpropagation is reviewing the graded test to see what went wrong. "
    "<bookmark mark='chain_rule'/> The network works backwards from the output to the input. Using calculus, specifically the Chain Rule, it calculates the 'gradient'. "
    "<bookmark mark='gradients'/> Gradients tell us exactly how much each individual weight and bias contributed to the overall error. "
    "<bookmark mark='update'/> Finally, an optimizer like Gradient Descent uses these gradients to update the weights. It nudges them down the slope, minimizing the loss for the next time. "
    "<bookmark mark='outro'/> Forward to predict, backward to learn. Iterating this cycle is how AI achieves mastery. Thanks for watching!"
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
        font_size=100,
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
        fwd_intro_start = tracker.bookmark_time("fwd_intro")
        fwd_flow_start = tracker.bookmark_time("fwd_flow")
        loss_start = tracker.bookmark_time("loss")
        back_intro_start = tracker.bookmark_time("back_intro")
        chain_rule_start = tracker.bookmark_time("chain_rule")
        gradients_start = tracker.bookmark_time("gradients")
        update_start = tracker.bookmark_time("update")
        outro_start = tracker.bookmark_time("outro")

        stroke = StrokeStyle(color=BLACK, width=3.0)
        net_stroke = StrokeStyle(color=LIGHT_GRAY, width=3.0)

        # ---------------------------------------------------------
        # SECTION 1: Intro
        # ---------------------------------------------------------
        intro_title = make_title("Forward & Backpropagation", y=400, color=BLUE)
        intro_sub = make_body("How Neural Networks Learn", y=550, color=ORANGE, font_size=64)
        
        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 2.5, duration=1.5), drawable=intro_sub)
        
        intro_drawables =[intro_title, intro_sub]

        # ---------------------------------------------------------
        # SECTION 2: Forward Propagation
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=fwd_intro_start - 1.0)
        
        # Neural Network Coordinates
        I1, I2 = (300, 400), (300, 700)
        H1, H2, H3 = (860, 300), (860, 550), (860, 800)
        O1 = (1420, 550)
        
        net_drawables =[]
        
        # Draw edges first
        for i_node in [I1, I2]:
            for h_node in[H1, H2, H3]:
                edge = Line(start=i_node, end=h_node, stroke_style=net_stroke, sketch_style=SKETCH)
                net_drawables.append(edge)
                scene.add(SketchAnimation(start_time=fwd_intro_start + 0.5, duration=0.8), drawable=edge)
                
        for h_node in [H1, H2, H3]:
            edge = Line(start=h_node, end=O1, stroke_style=net_stroke, sketch_style=SKETCH)
            net_drawables.append(edge)
            scene.add(SketchAnimation(start_time=fwd_intro_start + 1.0, duration=0.8), drawable=edge)

        # Draw nodes
        nodes =[I1, I2, H1, H2, H3, O1]
        for idx, pos in enumerate(nodes):
            color = PASTEL_BLUE if idx < 2 else (PASTEL_GREEN if idx < 5 else PASTEL_PURPLE)
            node = Circle(center=pos, radius=55, stroke_style=stroke, fill_style=FillStyle(color=color, opacity=0.8), sketch_style=SKETCH)
            net_drawables.append(node)
            scene.add(SketchAnimation(start_time=fwd_intro_start + 1.5 + (idx*0.1), duration=0.5), drawable=node)

        # Labels
        x_label = make_body("Inputs (x)", x=300, y=250, color=BLUE, font_size=48)
        h_label = make_body("Hidden Layer", x=860, y=150, color=GREEN, font_size=48)
        
        scene.add(SketchAnimation(start_time=fwd_intro_start + 2.5, duration=1.0), drawable=x_label)
        scene.add(SketchAnimation(start_time=fwd_intro_start + 3.0, duration=1.0), drawable=h_label)
        net_drawables.extend([x_label, h_label])

        # Forward Flow Arrow & Prediction
        fwd_arrow = Arrow(start_point=(400, 100), end_point=(1300, 100), stroke_style=StrokeStyle(color=BLUE, width=8), sketch_style=SKETCH)
        fwd_text = make_body("Forward Propagation", x=850, y=50, color=BLUE, font_size=56)
        
        y_hat_box = FlowchartProcess(r"Prediction ($\hat{y}$)", top_left=(1480, 500), width=350, height=100, font_size=48, fill_style=FillStyle(color=WHITE), stroke_style=stroke)

        scene.add(SketchAnimation(start_time=fwd_flow_start + 0.5, duration=1.0), drawable=fwd_arrow)
        scene.add(SketchAnimation(start_time=fwd_flow_start + 1.0, duration=1.0), drawable=fwd_text)
        scene.add(SketchAnimation(start_time=fwd_flow_start + 3.5, duration=1.0), drawable=y_hat_box)
        
        net_drawables.extend([fwd_arrow, fwd_text, y_hat_box])

        # ---------------------------------------------------------
        # SECTION 3: Loss Function
        # ---------------------------------------------------------
        y_true_box = FlowchartProcess(r"True Target ($y$)", top_left=(1480, 350), width=350, height=100, font_size=48, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=stroke)
        
        loss_bracket = Curve(points=[(1840, 550), (1880, 500), (1880, 450), (1840, 400)], stroke_style=StrokeStyle(color=RED, width=4), sketch_style=SKETCH)
        loss_math = Math(r"$Loss = \frac{1}{2}(\hat{y} - y)^2$", position=(1460, 750), font_size=64, stroke_style=StrokeStyle(color=RED, width=3))

        scene.add(SketchAnimation(start_time=loss_start + 1.0, duration=1.0), drawable=y_true_box)
        scene.add(SketchAnimation(start_time=loss_start + 2.5, duration=1.0), drawable=loss_bracket)
        scene.add(SketchAnimation(start_time=loss_start + 3.5, duration=1.5), drawable=loss_math)
        
        net_drawables.extend([y_true_box, loss_bracket, loss_math])

        # ---------------------------------------------------------
        # SECTION 4: Backpropagation & Chain Rule
        # ---------------------------------------------------------
        back_arrow = Arrow(start_point=(1300, 950), end_point=(400, 950), stroke_style=StrokeStyle(color=RED, width=8), sketch_style=SKETCH)
        back_text = make_body("Backpropagation", x=850, y=1000, color=RED, font_size=56)
        
        scene.add(SketchAnimation(start_time=back_intro_start + 1.0, duration=1.0), drawable=back_arrow)
        scene.add(SketchAnimation(start_time=back_intro_start + 1.5, duration=1.0), drawable=back_text)
        
        chain_rule_title = make_body("Calculus: Chain Rule", x=1250, y=250, color=ORANGE, font_size=56)
        chain_rule_math = Math(r"$\frac{\partial L}{\partial w_i} = \frac{\partial L}{\partial \hat{y}} \cdot \frac{\partial \hat{y}}{\partial z} \cdot \frac{\partial z}{\partial w_i}$", position=(1250, 850), font_size=56, stroke_style=StrokeStyle(color=ORANGE, width=3))
        
        scene.add(SketchAnimation(start_time=chain_rule_start + 1.5, duration=1.0), drawable=chain_rule_title)
        scene.add(SketchAnimation(start_time=chain_rule_start + 3.0, duration=2.5), drawable=chain_rule_math)
        
        # Highlight a specific weight gradient
        grad_highlight = Math(r"$\nabla w$", position=(550, 480), font_size=64, stroke_style=StrokeStyle(color=RED, width=3))
        scene.add(SketchAnimation(start_time=gradients_start + 0.5, duration=1.5), drawable=grad_highlight)

        net_drawables.extend([back_arrow, back_text, chain_rule_title, chain_rule_math, grad_highlight])

        # ---------------------------------------------------------
        # SECTION 5: Gradient Descent (Weight Update)
        # ---------------------------------------------------------
        make_eraser(net_drawables, scene, start_time=update_start - 1.2)
        
        gd_title = make_title("Gradient Descent Optimizer", y=150, color=BLUE)
        
        # U-shaped loss landscape (Valley)
        # We want y to be high (mathematically) at edges, low at center
        # y = -0.0015 * (x - 960)^2 + 800
        gd_pts =[(x, -0.0015 * (x - 960)**2 + 800) for x in range(460, 1461, 20)]
        gd_curve = Curve(points=gd_pts, stroke_style=StrokeStyle(color=BLACK, width=6), sketch_style=SKETCH)
        
        # Axes
        ax_x = Line(start=(400, 800), end=(1520, 800), stroke_style=stroke, sketch_style=SKETCH)
        ax_y = Line(start=(960, 900), end=(960, 350), stroke_style=stroke, sketch_style=SKETCH)
        ax_x_label = make_body("Weight (w)", x=1450, y=850, color=BLACK, font_size=48)
        ax_y_label = make_body("Loss (L)", x=880, y=380, color=BLACK, font_size=48)
        
        # The Ball (Current Weight)
        ball_x = 600
        ball_y = -0.0015 * (ball_x - 960)**2 + 800
        ball = Circle(center=(ball_x, ball_y), radius=25, stroke_style=stroke, fill_style=FillStyle(color=RED, opacity=1.0), sketch_style=SKETCH)
        
        # Arrow pointing down the gradient
        step_arrow = Arrow(start_point=(620, ball_y + 10), end_point=(780, 715), stroke_style=StrokeStyle(color=ORANGE, width=5), sketch_style=SKETCH)
        
        # Update Rule Math
        update_math = Math(r"$w_{new} = w_{old} - \alpha \frac{\partial L}{\partial w}$", position=(960, 950), font_size=80, stroke_style=StrokeStyle(color=GREEN, width=3))

        scene.add(SketchAnimation(start_time=update_start + 0.5, duration=1.0), drawable=gd_title)
        scene.add(SketchAnimation(start_time=update_start + 1.5, duration=1.0), drawable=ax_x)
        scene.add(SketchAnimation(start_time=update_start + 1.5, duration=1.0), drawable=ax_y)
        scene.add(SketchAnimation(start_time=update_start + 2.0, duration=0.5), drawable=ax_x_label)
        scene.add(SketchAnimation(start_time=update_start + 2.0, duration=0.5), drawable=ax_y_label)
        
        scene.add(SketchAnimation(start_time=update_start + 3.0, duration=1.5), drawable=gd_curve)
        scene.add(SketchAnimation(start_time=update_start + 4.5, duration=0.8), drawable=ball)
        scene.add(SketchAnimation(start_time=update_start + 5.5, duration=1.0), drawable=step_arrow)
        
        scene.add(SketchAnimation(start_time=update_start + 7.0, duration=2.0), drawable=update_math)

        gd_drawables =[gd_title, ax_x, ax_y, ax_x_label, ax_y_label, gd_curve, ball, step_arrow, update_math]

        # ---------------------------------------------------------
        # SECTION 6: Outro
        # ---------------------------------------------------------
        make_eraser(gd_drawables, scene, start_time=outro_start - 1.2)

        outro_title = make_title("Summary", y=200, color=BLACK)
        
        sum_box1 = FlowchartProcess("1. Forward Propagation\n➔ Make Predictions", top_left=(300, 450), width=600, height=200, font_size=56, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), stroke_style=stroke)
        sum_box2 = FlowchartProcess("2. Backpropagation\n➔ Learn from Mistakes", top_left=(1020, 450), width=600, height=200, font_size=56, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3), stroke_style=stroke)
        
        outro_text = make_body("Thanks for watching!", y=850, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=outro_start + 0.5, duration=1.0), drawable=outro_title)
        scene.add(SketchAnimation(start_time=outro_start + 1.5, duration=1.5), drawable=sum_box1)
        scene.add(SketchAnimation(start_time=outro_start + 3.0, duration=1.5), drawable=sum_box2)
        scene.add(SketchAnimation(start_time=tracker.end_time - 3.0, duration=1.5), drawable=outro_text)

        return tracker.end_time + 1.5

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")

if __name__ == "__main__":
    main()