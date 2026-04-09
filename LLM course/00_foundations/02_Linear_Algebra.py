import asyncio
import os
import re
import math
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("Please install edge-tts: pip install edge-tts")
    exit()

from handanim.animations import (
    FadeInAnimation,
    FadeOutAnimation,
    SketchAnimation,
    TransformAnimation,
    TranslateToAnimation,
    ZoomInAnimation,
)
from handanim.core import (
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
)
from handanim.primitives import (
    Arrow,
    Circle,
    Cube,
    Line,
    Math,
    MathTex,
    Rectangle,
    Square,
    Table,
    Text,
)
from handanim.stylings.color import (
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    WHITE,
    GRAY,
    DARK_GRAY,
    PASTEL_BLUE,
    PASTEL_GREEN,
    PASTEL_ORANGE,
    PASTEL_PURPLE,
    PASTEL_RED,
)

# --- Configuration ---
WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "linear_algebra_narration.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "linear_algebra_whiteboard.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
FONT_NAME = "cabin_sketch"
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> Welcome to the world of Linear Algebra. "
    "It is the mathematical language of shapes, rotations, and most importantly, artificial intelligence. "
    "<bookmark mark='vector_start'/> We begin with the most basic building block: The Vector. "
    "To a physicist, a vector is an arrow in space with a specific magnitude and direction. "
    "To a computer scientist, it is simply an ordered list of numbers. "
    "In a two-dimensional plane, a vector connects the origin to a point, like three, four. "
    "<bookmark mark='matrix_start'/> When we group these vectors together into a grid, we get a Matrix. "
    "A matrix isn't just a container for data; it is a dynamic operator. "
    "Multiplying a vector by a matrix transforms the space itself—scaling it, rotating it, or shearing it. "
    "<bookmark mark='tensor_start'/> But why stop at two dimensions? This brings us to Tensors. "
    "A scalar is a zero-rank tensor—just a single point. A vector is rank one—a line. "
    "A matrix is rank two—a surface. And a three-dimensional block of data is a rank-three tensor. "
    "Tensors are the multi-dimensional arrays that flow through neural networks, which is why we call it TensorFlow. "
    "<bookmark mark='eigen_start'/> Finally, we reach the crown jewel of linear algebra: Eigenvalues and Eigenvectors. "
    "When a matrix transforms space, most vectors get knocked off their original line. "
    "But a few special vectors, the Eigenvectors, stay exactly on their original span—they are only scaled. "
    "The amount they are scaled by is called the Eigenvalue. "
    "This concept allows us to simplify complex systems, from Google's PageRank algorithm to facial recognition. "
    "<bookmark mark='outro'/> From simple arrows to high-dimensional tensors, linear algebra is the engine of the modern world. "
    "Thanks for watching."
)

BOOKMARK_RE = re.compile(r"<bookmark\s+(?:mark|name)\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

async def synthesize_narration(audio_path: str, text: str) -> None:
    if os.path.exists(audio_path):
        return
    communicate = edge_tts.Communicate(strip_bookmarks(text), VOICE, rate=VOICE_RATE)
    await communicate.save(audio_path)

def make_eraser(scene, objects, start_time, duration=1.5):
    from handanim.primitives import Eraser
    eraser = Eraser(
        objects_to_erase=objects,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.6, 0.6, 0.6), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)

def main():
    # 1. Synthesize audio
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Setup Scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_vector = tracker.bookmark_time("vector_start")
        t_matrix = tracker.bookmark_time("matrix_start")
        t_tensor = tracker.bookmark_time("tensor_start")
        t_eigen = tracker.bookmark_time("eigen_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRO ---
        title = Text("Linear Algebra", position=(960, 400), font_size=120, color=BLUE, sketch_style=SKETCH)
        subtitle = Text("The Engine of AI & Physics", position=(960, 550), font_size=60, color=DARK_GRAY, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 2.0, duration=2.0), drawable=subtitle)
        
        make_eraser(scene, [title, subtitle], t_vector - 1.0)

        # --- SECTION 2: VECTORS ---
        v_title = Text("1. The Vector", position=(300, 150), font_size=80, color=RED, sketch_style=SKETCH)
        
        # Coordinate Plane
        origin = (500, 700)
        xaxis = Line(start=(300, 700), end=(1100, 700), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        yaxis = Line(start=(500, 400), end=(500, 900), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        
        vec_arrow = Arrow(start_point=origin, end_point=(900, 500), arrow_head_type="-|>", stroke_style=StrokeStyle(color=RED, width=8), sketch_style=SKETCH)
        vec_math = MathTex(tex_expression=r"$\vec{v} = \begin{bmatrix} 3 \\ 4 \end{bmatrix}$", position=(1300, 550), font_size=100, stroke_style=StrokeStyle(color=RED), usetex=True)
        
        scene.add(SketchAnimation(start_time=t_vector, duration=1.5), drawable=v_title)
        scene.add(SketchAnimation(start_time=t_vector + 1.0, duration=1.5), drawable=xaxis)
        scene.add(SketchAnimation(start_time=t_vector + 1.0, duration=1.5), drawable=yaxis)
        scene.add(SketchAnimation(start_time=t_vector + 3.0, duration=2.0), drawable=vec_arrow)
        scene.add(SketchAnimation(start_time=t_vector + 5.0, duration=2.0), drawable=vec_math)

        make_eraser(scene, [v_title, xaxis, yaxis, vec_arrow, vec_math], t_matrix - 1.0)

        # --- SECTION 3: MATRICES ---
        m_title = Text("2. The Matrix", position=(300, 150), font_size=80, color=GREEN, sketch_style=SKETCH)
        
        matrix_table = Table(
            data=[["a", "b"], ["c", "d"]],
            top_left=(400, 350),
            col_widths=[150, 150],
            row_heights=[120, 120],
            font_size=80,
            fill_style=FillStyle(color=WHITE),
            stroke_style=StrokeStyle(color=GREEN, width=5)
        )
        
        transform_label = Text("Linear Transformation", position=(1300, 400), font_size=60, color=GREEN, sketch_style=SKETCH)
        rotate_math = MathTex(tex_expression=r"$\begin{bmatrix} \cos \theta & -\sin \theta \\ \sin \theta & \cos \theta \end{bmatrix}$", position=(1300, 600), font_size=80, usetex=True)

        scene.add(SketchAnimation(start_time=t_matrix, duration=1.5), drawable=m_title)
        scene.add(SketchAnimation(start_time=t_matrix + 2.0, duration=2.5), drawable=matrix_table)
        scene.add(SketchAnimation(start_time=t_matrix + 5.0, duration=2.0), drawable=transform_label)
        scene.add(SketchAnimation(start_time=t_matrix + 7.0, duration=2.5), drawable=rotate_math)

        make_eraser(scene, [m_title, matrix_table, transform_label, rotate_math], t_tensor - 1.0)

        # --- SECTION 4: TENSORS ---
        t_title = Text("3. Tensors (Generalization)", position=(400, 150), font_size=80, color=PURPLE, sketch_style=SKETCH)
        
        scalar = Circle(center=(300, 500), radius=20, fill_style=FillStyle(color=PASTEL_RED), sketch_style=SKETCH)
        s_lbl = Text("Scalar (Rank 0)", position=(300, 650), font_size=40)
        
        vector = Line(start=(550, 400), end=(550, 600), stroke_style=StrokeStyle(color=PASTEL_GREEN, width=10), sketch_style=SKETCH)
        v_lbl = Text("Vector (Rank 1)", position=(550, 650), font_size=40)
        
        matrix = Square(top_left=(750, 425), side_length=150, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3), sketch_style=SKETCH)
        m_lbl = Text("Matrix (Rank 2)", position=(825, 650), font_size=40)
        
        tensor_cube = Rectangle(top_left=(1100, 400), width=200, height=200, fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.3), sketch_style=SKETCH)
        t_lbl = Text("Tensor (Rank 3+)", position=(1200, 650), font_size=40)
        
        tf_note = Text("Deep Learning = Tensor Flow", position=(960, 850), font_size=54, color=PURPLE, sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=t_tensor, duration=1.5), drawable=t_title)
        scene.add(SketchAnimation(start_time=t_tensor + 2.0, duration=1.0), drawable=scalar)
        scene.add(SketchAnimation(start_time=t_tensor + 2.5, duration=1.0), drawable=s_lbl)
        scene.add(SketchAnimation(start_time=t_tensor + 4.0, duration=1.0), drawable=vector)
        scene.add(SketchAnimation(start_time=t_tensor + 4.5, duration=1.0), drawable=v_lbl)
        scene.add(SketchAnimation(start_time=t_tensor + 6.0, duration=1.0), drawable=matrix)
        scene.add(SketchAnimation(start_time=t_tensor + 6.5, duration=1.0), drawable=m_lbl)
        scene.add(SketchAnimation(start_time=t_tensor + 8.0, duration=1.0), drawable=tensor_cube)
        scene.add(SketchAnimation(start_time=t_tensor + 8.5, duration=1.0), drawable=t_lbl)
        scene.add(SketchAnimation(start_time=t_tensor + 11.0, duration=2.0), drawable=tf_note)

        make_eraser(scene, [t_title, scalar, s_lbl, vector, v_lbl, matrix, m_lbl, tensor_cube, t_lbl, tf_note], t_eigen - 1.0)

        # --- SECTION 5: EIGENVALUES & EIGENVECTORS ---
        e_title = Text("4. Eigenvalues & Eigenvectors", position=(500, 150), font_size=80, color=ORANGE, sketch_style=SKETCH)
        
        eigen_math = MathTex(tex_expression=r"$\mathbf{A}\mathbf{v} = \lambda \mathbf{v}$", position=(960, 450), font_size=150, stroke_style=StrokeStyle(color=ORANGE), usetex=True)
        
        v_expl = Text("Vector v: Does not change direction", position=(960, 650), font_size=50, color=DARK_GRAY)
        l_expl = Text("Lambda: Only scales the length", position=(960, 750), font_size=50, color=DARK_GRAY)

        scene.add(SketchAnimation(start_time=t_eigen, duration=1.5), drawable=e_title)
        scene.add(SketchAnimation(start_time=t_eigen + 3.0, duration=3.0), drawable=eigen_math)
        scene.add(SketchAnimation(start_time=t_eigen + 7.0, duration=2.0), drawable=v_expl)
        scene.add(SketchAnimation(start_time=t_eigen + 9.0, duration=2.0), drawable=l_expl)

        make_eraser(scene, [e_title, eigen_math, v_expl, l_expl], t_outro - 1.0)

        # --- SECTION 6: OUTRO ---
        final_msg = Text("The Engine of Modern Progress", position=(960, 540), font_size=90, color=BLUE, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=final_msg)

        # 3. Render
        scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()