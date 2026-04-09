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
from handanim.primitives import Arrow, Circle, Curve, FlowchartProcess, Line, Math, Polygon, Rectangle, Table
from handanim.stylings.color import (
    BLACK, BLUE, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, ORANGE, PURPLE, RED, WHITE,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_ORANGE, PASTEL_PURPLE, PASTEL_RED
)

WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).parent / "output" / "loss_functions"
AUDIO_PATH = OUTPUT_DIR / "loss_functions_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "loss_functions_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "-2%"  # Slightly slower for a 5-minute deep dive feel
VOICE_VOLUME = 1.25
FONT_NAME = "feasibly"

BG = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

# ~650 words. At -2% rate, this should run roughly 4 to 4.5 minutes, providing a highly detailed 5-minute style video.
NARRATION = (
    "<bookmark mark='intro'/> Welcome to a comprehensive deep dive into the compass that guides all machine learning models: Loss Functions. "
    "Today, we are exploring the three mathematical engines of AI learning: Mean Squared Error, Cross-Entropy, and KL Divergence. "
    "<bookmark mark='compass'/> Without a loss function, a neural network is effectively blind. It's just a random number generator. "
    "The loss function calculates exactly how wrong the model is, providing the critical mathematical feedback, or gradients, needed to improve and learn. "
    
    "<bookmark mark='mse_intro'/> Let's begin with the absolute gold standard for continuous regression tasks: Mean Squared Error, commonly known as MSE. "
    "<bookmark mark='mse_house'/> Imagine you are building an AI model to predict real estate prices. The true value of a house is three hundred thousand dollars. "
    "Your model makes a prediction, let's call it y-hat, of two hundred thousand dollars. The error is the difference between these two numbers. "
    "<bookmark mark='mse_math'/> But why do we calculate the 'Squared' error? MSE takes the difference, and squares it. "
    "This accomplishes two brilliant things. First, squaring the number ensures the result is always positive, meaning overestimating and underestimating don't cancel each other out. "
    "<bookmark mark='mse_parabola'/> Second, and most importantly, it heavily punishes large errors. An error of 2 becomes a penalty of 4, but an error of 10 becomes a massive penalty of 100! "
    "Graphically, this creates a beautiful, smooth, U-shaped parabola. This smooth curve acts like a bowl, gently guiding the model's optimizer safely down to the minimum possible loss. "
    
    "<bookmark mark='ce_intro'/> However, MSE has a fatal weakness. It is completely terrible for classification tasks. "
    "If you want to classify whether an image is a dog or a cat, MSE struggles because classes don't have mathematical distances. For classification, we use Cross-Entropy. "
    "<bookmark mark='ce_prob'/> In classification, neural networks don't output hard labels; they output probability distributions. "
    "For example, the model says there is a 90 percent chance the image is a cat, and a 10 percent chance it is a dog. "
    "<bookmark mark='ce_math'/> Cross-Entropy, which has deep roots in Information Theory, measures the difference between the model's predicted probabilities and the actual true labels. "
    "The true label is typically a one-hot encoded vector: 100 percent for the correct answer, and 0 percent for everything else. "
    "<bookmark mark='ce_log'/> The core of Cross-Entropy is the natural logarithm. It calculates the 'surprise' of the prediction. "
    "If the model is 99 percent confident it's a dog, and it IS a dog, the loss is near zero. The model is barely penalized. "
    "But, if the model is 99 percent confident it's a cat, and it's actually a dog, Cross-Entropy applies a devastating, exponentially massive penalty. "
    "It screams at the model: 'You weren't just wrong, you were confidently wrong!' This forces the model to rapidly correct bad assumptions. "
    
    "<bookmark mark='kl_intro'/> This brings us to a very close mathematical cousin of Cross-Entropy: Kullback-Leibler Divergence, or KL Divergence for short. "
    "<bookmark mark='kl_concept'/> While Cross-Entropy calculates the total surprise, KL Divergence measures the *extra* surprise. "
    "It strictly answers the question: How much information is lost when we use our model's probability distribution, Q, to approximate the true probability distribution, P? "
    "<bookmark mark='kl_visual'/> Visually, imagine two bell curves. KL Divergence calculates how far apart these two distributions are, and specifically measures how to reshape the predicted curve to perfectly match the target curve. "
    "But remember, it is asymmetric. Walking from distribution P to Q yields a different divergence than walking from Q to P. "
    "<bookmark mark='kl_vae'/> KL Divergence is heavily used in Generative AI, specifically in Variational Autoencoders. "
    "It forces the AI's internal latent space to match a clean, standard normal distribution, preventing the model from just memorizing data, and forcing it to learn meaningful, continuous representations of the world. "
    
    "<bookmark mark='summary'/> To summarize this deep dive: Use Mean Squared Error when your AI is predicting continuous numbers, like prices or temperatures. "
    "Use Cross-Entropy when you are classifying discrete categories, like words or images. "
    "And use KL Divergence when you need to match and mold complex probability distributions, especially in generative AI. "
    "Thank you for watching!"
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
        compass_start = tracker.bookmark_time("compass")
        
        mse_intro_start = tracker.bookmark_time("mse_intro")
        mse_house_start = tracker.bookmark_time("mse_house")
        mse_math_start = tracker.bookmark_time("mse_math")
        mse_parabola_start = tracker.bookmark_time("mse_parabola")
        
        ce_intro_start = tracker.bookmark_time("ce_intro")
        ce_prob_start = tracker.bookmark_time("ce_prob")
        ce_math_start = tracker.bookmark_time("ce_math")
        ce_log_start = tracker.bookmark_time("ce_log")
        
        kl_intro_start = tracker.bookmark_time("kl_intro")
        kl_concept_start = tracker.bookmark_time("kl_concept")
        kl_visual_start = tracker.bookmark_time("kl_visual")
        kl_vae_start = tracker.bookmark_time("kl_vae")
        
        summary_start = tracker.bookmark_time("summary")

        stroke_thick = StrokeStyle(color=BLACK, width=4.0)
        
        # ---------------------------------------------------------
        # SECTION 1: Intro & Compass
        # ---------------------------------------------------------
        intro_title = make_title("Loss Functions in AI", y=200, color=BLUE)
        intro_sub = make_body("MSE • Cross-Entropy • KL Divergence", y=350, color=DARK_GRAY, font_size=64)
        
        compass_circle = Circle(center=(960, 650), radius=200, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.2), sketch_style=SKETCH)
        compass_needle = Arrow(start_point=(960, 800), end_point=(960, 500), stroke_style=StrokeStyle(color=RED, width=8), sketch_style=SKETCH)
        compass_text = make_body("Minimum Loss", x=960, y=920, color=RED, font_size=56)

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=2.0), drawable=intro_title)
        scene.add(SketchAnimation(start_time=intro_start + 3.0, duration=1.5), drawable=intro_sub)
        
        scene.add(SketchAnimation(start_time=compass_start + 0.5, duration=1.5), drawable=compass_circle)
        scene.add(SketchAnimation(start_time=compass_start + 2.0, duration=1.0), drawable=compass_needle)
        scene.add(SketchAnimation(start_time=compass_start + 3.5, duration=1.5), drawable=compass_text)

        intro_drawables =[intro_title, intro_sub, compass_circle, compass_needle, compass_text]

        # ---------------------------------------------------------
        # SECTION 2: Mean Squared Error (MSE)
        # ---------------------------------------------------------
        make_eraser(intro_drawables, scene, start_time=mse_intro_start - 1.2)
        
        mse_title = make_title("1. Mean Squared Error (MSE)", y=120, color=ORANGE)
        
        house_base = Rectangle(top_left=(300, 450), width=200, height=200, stroke_style=stroke_thick, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3), sketch_style=SKETCH)
        house_roof = Polygon(points=[(250, 450), (400, 300), (550, 450)], stroke_style=stroke_thick, fill_style=FillStyle(color=RED, opacity=0.5), sketch_style=SKETCH)
        
        true_price = make_body(r"True ($y$): $300k", x=400, y=720, color=GREEN, font_size=48)
        pred_price = make_body(r"Pred ($\hat{y}$): $200k", x=400, y=800, color=RED, font_size=48)
        
        mse_formula = Math(r"$\text{MSE} = \frac{1}{N} \sum (y - \hat{y})^2$", position=(1300, 350), font_size=80, stroke_style=StrokeStyle(color=BLACK, width=3))
        mse_calc = Math(r"$(300 - 200)^2 = 10,000$", position=(1300, 500), font_size=64, stroke_style=StrokeStyle(color=RED, width=3))

        # Parabola
        pts =[]
        for x in range(900, 1700, 20):
            # U-shape centered at 1300
            y = 0.002 * (x - 1300)**2 + 700
            pts.append((x, y))
        parabola = Curve(points=pts, stroke_style=StrokeStyle(color=BLUE, width=6), sketch_style=SKETCH)
        ball = Circle(center=(1000, 0.002*(1000-1300)**2+680), radius=20, fill_style=FillStyle(color=RED), stroke_style=stroke_thick, sketch_style=SKETCH)
        parabola_text = make_body("Heavily punishes large errors", x=1300, y=950, color=BLUE, font_size=48)

        scene.add(SketchAnimation(start_time=mse_intro_start + 0.5, duration=1.5), drawable=mse_title)
        
        scene.add(SketchAnimation(start_time=mse_house_start + 0.5, duration=1.0), drawable=house_base)
        scene.add(SketchAnimation(start_time=mse_house_start + 1.0, duration=1.0), drawable=house_roof)
        scene.add(SketchAnimation(start_time=mse_house_start + 3.0, duration=1.0), drawable=true_price)
        scene.add(SketchAnimation(start_time=mse_house_start + 6.0, duration=1.0), drawable=pred_price)

        scene.add(SketchAnimation(start_time=mse_math_start + 1.0, duration=2.5), drawable=mse_formula)
        scene.add(SketchAnimation(start_time=mse_math_start + 6.0, duration=1.5), drawable=mse_calc)

        scene.add(SketchAnimation(start_time=mse_parabola_start + 3.5, duration=2.0), drawable=parabola)
        scene.add(SketchAnimation(start_time=mse_parabola_start + 5.5, duration=0.8), drawable=ball)
        scene.add(SketchAnimation(start_time=mse_parabola_start + 7.0, duration=1.5), drawable=parabola_text)

        mse_drawables =[mse_title, house_base, house_roof, true_price, pred_price, mse_formula, mse_calc, parabola, ball, parabola_text]

        # ---------------------------------------------------------
        # SECTION 3: Cross-Entropy
        # ---------------------------------------------------------
        make_eraser(mse_drawables, scene, start_time=ce_intro_start - 1.2)
        
        ce_title = make_title("2. Cross-Entropy Loss", y=120, color=PURPLE)
        
        ce_vs_label = make_body("Classification: Dog vs Cat", x=960, y=250, color=BLACK, font_size=64)
        
        prob_box = FlowchartProcess("True: [Dog: 1.0, Cat: 0.0]\nPred:[Dog: 0.1, Cat: 0.9]", top_left=(200, 350), width=650, height=200, font_size=48, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.2), stroke_style=stroke_thick, sketch_style=SKETCH)
        
        ce_formula = Math(r"$CE = -\sum y \cdot \log(\hat{y})$", position=(1400, 450), font_size=80, stroke_style=StrokeStyle(color=BLACK, width=3))

        # Log curve visualization
        log_pts =[]
        for x in range(300, 1600, 20):
            # x maps probability from 0.01 to 1.0. 
            # 300 = p:0.01, 1600 = p:1.0
            p = (x - 200) / 1400.0
            if p <= 0: p = 0.01
            # y maps to penalty. higher penalty = higher up (lower y)
            # base y = 900 (0 penalty)
            penalty = -math.log(p)
            y = 900 - 80 * penalty
            log_pts.append((x, y))
            
        log_curve = Curve(points=log_pts, stroke_style=StrokeStyle(color=RED, width=6), sketch_style=SKETCH)
        
        ax_p = Line(start=(250, 900), end=(1650, 900), stroke_style=stroke_thick, sketch_style=SKETCH)
        ax_l = Line(start=(300, 950), end=(300, 500), stroke_style=stroke_thick, sketch_style=SKETCH)
        
        log_text_x = make_body("Confidence (Prob)", x=1400, y=950, color=BLACK, font_size=40)
        log_text_y = make_body("Massive Penalty\n(Log Loss)", x=200, y=550, color=RED, font_size=40)

        scene.add(SketchAnimation(start_time=ce_intro_start + 0.5, duration=1.5), drawable=ce_title)
        scene.add(SketchAnimation(start_time=ce_intro_start + 5.0, duration=1.5), drawable=ce_vs_label)
        
        scene.add(SketchAnimation(start_time=ce_prob_start + 0.5, duration=2.0), drawable=prob_box)
        scene.add(SketchAnimation(start_time=ce_math_start + 1.0, duration=2.0), drawable=ce_formula)
        
        scene.add(SketchAnimation(start_time=ce_log_start + 1.0, duration=1.0), drawable=ax_p)
        scene.add(SketchAnimation(start_time=ce_log_start + 1.0, duration=1.0), drawable=ax_l)
        scene.add(SketchAnimation(start_time=ce_log_start + 1.5, duration=0.5), drawable=log_text_x)
        scene.add(SketchAnimation(start_time=ce_log_start + 1.5, duration=0.5), drawable=log_text_y)
        
        scene.add(SketchAnimation(start_time=ce_log_start + 8.5, duration=3.0), drawable=log_curve)

        ce_drawables =[ce_title, ce_vs_label, prob_box, ce_formula, log_curve, ax_p, ax_l, log_text_x, log_text_y]

        # ---------------------------------------------------------
        # SECTION 4: KL Divergence
        # ---------------------------------------------------------
        make_eraser(ce_drawables, scene, start_time=kl_intro_start - 1.2)
        
        kl_title = make_title("3. KL Divergence", y=120, color=GREEN)
        
        kl_formula = Math(r"$D_{KL}(P \parallel Q) = \sum P(x) \log\left(\frac{P(x)}{Q(x)}\right)$", position=(960, 280), font_size=80, stroke_style=StrokeStyle(color=BLACK, width=3))

        # Bell curves
        def get_bell_curve(mu, sigma, height, center_y, color):
            pts =[]
            for x in range(300, 1600, 10):
                # Standard Gaussian equation
                val = height * math.exp(-0.5 * ((x - mu)/sigma)**2)
                pts.append((x, center_y - val))
            return Curve(points=pts, stroke_style=StrokeStyle(color=color, width=6), sketch_style=SKETCH)

        curve_p = get_bell_curve(mu=800, sigma=180, height=350, center_y=800, color=GREEN)
        curve_q = get_bell_curve(mu=1200, sigma=200, height=280, center_y=800, color=BLUE)
        
        p_label = make_body("Target $P(x)$", x=800, y=380, color=GREEN, font_size=48)
        q_label = make_body("Predicted $Q(x)$", x=1300, y=450, color=BLUE, font_size=48)
        
        ax_base = Line(start=(200, 800), end=(1700, 800), stroke_style=stroke_thick, sketch_style=SKETCH)
        
        # Arrows pulling Q to P
        arrow1 = Arrow(start_point=(1200, 600), end_point=(950, 600), stroke_style=StrokeStyle(color=RED, width=5), sketch_style=SKETCH)
        arrow2 = Arrow(start_point=(1100, 700), end_point=(850, 700), stroke_style=StrokeStyle(color=RED, width=5), sketch_style=SKETCH)
        
        vae_text = make_body("Core component of Variational Autoencoders (VAEs)", x=960, y=950, color=DARK_GRAY, font_size=56)

        scene.add(SketchAnimation(start_time=kl_intro_start + 0.5, duration=1.5), drawable=kl_title)
        scene.add(SketchAnimation(start_time=kl_concept_start + 3.0, duration=2.5), drawable=kl_formula)
        
        scene.add(SketchAnimation(start_time=kl_visual_start + 1.0, duration=1.0), drawable=ax_base)
        scene.add(SketchAnimation(start_time=kl_visual_start + 1.5, duration=2.0), drawable=curve_p)
        scene.add(SketchAnimation(start_time=kl_visual_start + 1.5, duration=0.8), drawable=p_label)
        scene.add(SketchAnimation(start_time=kl_visual_start + 2.5, duration=2.0), drawable=curve_q)
        scene.add(SketchAnimation(start_time=kl_visual_start + 2.5, duration=0.8), drawable=q_label)
        
        scene.add(SketchAnimation(start_time=kl_visual_start + 7.0, duration=1.0), drawable=arrow1)
        scene.add(SketchAnimation(start_time=kl_visual_start + 7.5, duration=1.0), drawable=arrow2)
        
        scene.add(SketchAnimation(start_time=kl_vae_start + 1.0, duration=2.0), drawable=vae_text)

        kl_drawables =[kl_title, kl_formula, curve_p, curve_q, p_label, q_label, ax_base, arrow1, arrow2, vae_text]

        # ---------------------------------------------------------
        # SECTION 5: Summary Table
        # ---------------------------------------------------------
        make_eraser(kl_drawables, scene, start_time=summary_start - 1.2)
        
        sum_title = make_title("Summary of Loss Functions", y=150, color=BLACK)
        
        sum_table = Table(
            data=[
                ["Loss Function", "Best Used For", "Key Characteristic"],["MSE", "Continuous Regression", "Punishes massive outliers quadratically"],
                ["Cross-Entropy", "Classification", "Logarithmic penalty for confident errors"],["KL Divergence", "Generative AI", "Matches entire probability distributions"]
            ],
            top_left=(150, 350),
            col_widths=[400, 500, 700],
            row_heights=[100, 150, 150, 150],
            font_size=42,
            header_fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.4),
            fill_style=FillStyle(color=WHITE),
            stroke_style=stroke_thick,
            sketch_style=SKETCH
        )
        
        outro_text = make_body("Thanks for watching!", y=950, color=BLUE, font_size=72)

        scene.add(SketchAnimation(start_time=summary_start + 0.5, duration=1.0), drawable=sum_title)
        scene.add(SketchAnimation(start_time=summary_start + 3.0, duration=4.0), drawable=sum_table)
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