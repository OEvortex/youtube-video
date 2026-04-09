import os
import asyncio
import re
import math
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("Please install edge-tts: pip install edge-tts")
    exit()

from handanim.animations import (
    SketchAnimation,
    FadeInAnimation,
    FadeOutAnimation,
    TransformAnimation,
    TranslateToAnimation,
)
from handanim.core import (
    CompositeAnimationEvent,
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
)
from handanim.core.styles import StrokePressure
from handanim.primitives import (
    Arrow,
    Circle,
    Line,
    LinearPath,
    Math,
    Rectangle,
    Text,
    Eraser,
    Square,
)
from handanim.core import DrawableGroup
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
    PASTEL_RED,
    PASTEL_PURPLE,
)

# --- Configuration ---
WIDTH = 1920
HEIGHT = 1088
FONT_NAME = "cabin_sketch"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "classification_clustering.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "classification_clustering.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> In the world of Machine Learning, we often need to organize data. "
    "This is done through two main approaches: Classification, where we know the categories, "
    "and Clustering, where we let the machine find the groups itself. "
    "<bookmark mark='knn_start'/> Let's start with K-Nearest Neighbors, or KNN. "
    "It is one of the simplest classification algorithms. Imagine we have a new data point. "
    "To decide its category, we look at its 'K' closest neighbors. "
    "If most of those neighbors are 'Red', the new point becomes 'Red'. It is literally a majority vote based on distance. "
    "<bookmark mark='svm_start'/> Next, we have Support Vector Machines, or SVMs. "
    "Instead of looking at neighbors, an SVM tries to draw a boundary, called a hyperplane, "
    "that maximizes the distance between two classes. "
    "The points closest to this boundary are the 'Support Vectors'. "
    "By maximizing this margin, the model becomes more robust to new, unseen data. "
    "Even if data isn't linearly separable, SVMs can use the 'Kernel Trick' to project data into higher dimensions to find a split. "
    "<bookmark mark='kmeans_start'/> Now, let's move to Unsupervised Learning with K-Means Clustering. "
    "Here, we have no labels—just raw data. We want the computer to find 'K' distinct clusters. "
    "The algorithm starts by placing 'K' random center points, called centroids. "
    "It then assigns every data point to its nearest centroid. "
    "Next, it moves the centroids to the average center of their assigned points and repeats the process. "
    "Eventually, the centroids stop moving, and we have our clusters. "
    "<bookmark mark='outro'/> From the voting logic of KNN to the geometric boundaries of SVMs and the iterative grouping of K-Means, "
    "these tools allow us to make sense of complex datasets. Thanks for watching."
)

BOOKMARK_RE = re.compile(r"<bookmark\s+(?:mark|name)\s*=\s*['\"][^'\"]+['\"]\s*/>")

def strip_bookmarks(text: str) -> str:
    return BOOKMARK_RE.sub("", text)

async def synthesize_narration(audio_path: str, text: str) -> None:
    if os.path.exists(audio_path):
        return
    communicate = edge_tts.Communicate(strip_bookmarks(text), VOICE, rate=VOICE_RATE)
    await communicate.save(audio_path)

def main():
    # 1. Synthesize Audio
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Setup Scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=12, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_knn = tracker.bookmark_time("knn_start")
        t_svm = tracker.bookmark_time("svm_start")
        t_kmeans = tracker.bookmark_time("kmeans_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRO ---
        title = Text("Classification & Clustering", position=(960, 400), font_size=100, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        sub1 = Text("Supervised: Classification", position=(600, 600), font_size=50, color=RED, font_name=FONT_NAME)
        sub2 = Text("Unsupervised: Clustering", position=(1300, 600), font_size=50, color=PURPLE, font_name=FONT_NAME)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 3.0, duration=1.5), drawable=sub1)
        scene.add(SketchAnimation(start_time=t_intro + 4.5, duration=1.5), drawable=sub2)

        eraser_intro = Eraser(objects_to_erase=[title, sub1, sub2], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_knn - 1.0, duration=1.0), drawable=eraser_intro)

        # --- SECTION 2: KNN ---
        knn_title = Text("1. K-Nearest Neighbors (KNN)", position=(500, 150), font_size=70, color=RED, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Grid/Axes
        xaxis = Line(start=(300, 850), end=(1000, 850), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        yaxis = Line(start=(400, 450), end=(400, 950), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        
        # Data Points
        red_pts = [(450, 800), (500, 750), (480, 680), (550, 720)]
        blue_pts = [(850, 550), (900, 600), (880, 680), (950, 620)]
        red_dots = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_RED)) for p in red_pts]
        blue_dots = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_BLUE)) for p in blue_pts]
        
        # Query Point
        query_pt = (700, 700)
        query_dot = Circle(center=query_pt, radius=15, stroke_style=StrokeStyle(color=BLACK, width=3), fill_style=FillStyle(color=WHITE))
        query_lbl = Text("?", position=(700, 700), font_size=30, font_name=FONT_NAME)
        
        # Neighbor Circle
        neighbor_circle = Circle(center=query_pt, radius=180, stroke_style=StrokeStyle(color=GREEN, width=2, opacity=0.5), sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_knn, duration=1.5), drawable=knn_title)
        scene.add(SketchAnimation(start_time=t_knn + 1.0, duration=1.0), drawable=xaxis)
        scene.add(SketchAnimation(start_time=t_knn + 1.0, duration=1.0), drawable=yaxis)
        
        for i, dot in enumerate(red_dots + blue_dots):
            scene.add(SketchAnimation(start_time=t_knn + 2.0 + i*0.2, duration=0.4), drawable=dot)
            
        scene.add(SketchAnimation(start_time=t_knn + 5.0, duration=1.0), drawable=query_dot)
        scene.add(SketchAnimation(start_time=t_knn + 5.0, duration=1.0), drawable=query_lbl)
        scene.add(SketchAnimation(start_time=t_knn + 8.0, duration=2.0), drawable=neighbor_circle)
        
        # Result: Query turns Blue (assuming K=3, neighbors are mostly blue)
        query_result = Circle(center=query_pt, radius=15, fill_style=FillStyle(color=PASTEL_BLUE))
        scene.add(FadeInAnimation(start_time=t_knn + 12.0, duration=0.5), drawable=query_result)

        eraser_knn = Eraser(objects_to_erase=[knn_title, xaxis, yaxis, neighbor_circle, query_dot, query_lbl, query_result, *red_dots, *blue_dots], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_svm - 1.0, duration=1.0), drawable=eraser_knn)

        # --- SECTION 3: SVM ---
        svm_title = Text("2. Support Vector Machines (SVM)", position=(550, 150), font_size=70, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Separable Data
        s_red_pts = [(400, 800), (500, 850), (450, 700), (600, 820)]
        s_blue_pts = [(1200, 400), (1300, 450), (1250, 550), (1100, 420)]
        s_red_dots = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_RED)) for p in s_red_pts]
        s_blue_dots = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_BLUE)) for p in s_blue_pts]
        
        # Hyperplane and Margins
        hyperplane = Line(start=(400, 400), end=(1400, 900), stroke_style=StrokeStyle(color=BLACK, width=5), sketch_style=SKETCH)
        margin1 = Line(start=(500, 350), end=(1500, 850), stroke_style=StrokeStyle(color=GRAY, width=2, opacity=0.5), sketch_style=SKETCH)
        margin2 = Line(start=(300, 450), end=(1300, 950), stroke_style=StrokeStyle(color=GRAY, width=2, opacity=0.5), sketch_style=SKETCH)
        
        margin_lbl = Text("Maximum Margin", position=(1100, 750), font_size=40, color=DARK_GRAY, font_name=FONT_NAME)
        
        scene.add(SketchAnimation(start_time=t_svm, duration=1.5), drawable=svm_title)
        for dot in s_red_dots + s_blue_dots:
            scene.add(FadeInAnimation(start_time=t_svm + 2.0, duration=0.5), drawable=dot)
            
        scene.add(SketchAnimation(start_time=t_svm + 4.0, duration=2.0), drawable=hyperplane)
        scene.add(SketchAnimation(start_time=t_svm + 7.0, duration=1.5), drawable=margin1)
        scene.add(SketchAnimation(start_time=t_svm + 7.0, duration=1.5), drawable=margin2)
        scene.add(SketchAnimation(start_time=t_svm + 9.0, duration=1.5), drawable=margin_lbl)
        
        # Kernel Trick Note
        kernel_note = Text("The Kernel Trick: Projecting to 3D", position=(960, 950), font_size=45, color=PURPLE, font_name=FONT_NAME, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_svm + 13.0, duration=2.0), drawable=kernel_note)

        eraser_svm = Eraser(objects_to_erase=[svm_title, hyperplane, margin1, margin2, margin_lbl, kernel_note, *s_red_dots, *s_blue_dots], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_kmeans - 1.0, duration=1.0), drawable=eraser_svm)

        # --- SECTION 4: K-MEANS ---
        km_title = Text("3. K-Means Clustering", position=(450, 150), font_size=70, color=PURPLE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Unlabeled Data
        raw_pts = [(500, 500), (550, 550), (480, 600), (600, 520), (1300, 700), (1350, 750), (1280, 800), (1400, 720)]
        raw_dots = [Circle(center=p, radius=12, fill_style=FillStyle(color=GRAY)) for p in raw_pts]
        
        # Centroids
        c1_pos = (700, 400)
        c2_pos = (1100, 900)
        centroid1 = Text("X", position=c1_pos, font_size=50, color=RED, font_name=FONT_NAME)
        centroid2 = Text("X", position=c2_pos, font_size=50, color=BLUE, font_name=FONT_NAME)
        
        scene.add(SketchAnimation(start_time=t_kmeans, duration=1.5), drawable=km_title)
        for dot in raw_dots:
            scene.add(FadeInAnimation(start_time=t_kmeans + 2.0, duration=0.5), drawable=dot)
            
        scene.add(SketchAnimation(start_time=t_kmeans + 5.0, duration=1.0), drawable=centroid1)
        scene.add(SketchAnimation(start_time=t_kmeans + 5.0, duration=1.0), drawable=centroid2)
        
        # Iteration 1: Points change color
        red_cluster = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_RED)) for p in raw_pts[:4]]
        blue_cluster = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_BLUE)) for p in raw_pts[4:]]
        
        scene.add(FadeInAnimation(start_time=t_kmeans + 8.0, duration=1.0), drawable=DrawableGroup(elements=red_cluster + blue_cluster))
        
        # Iteration 2: Centroids move
        c1_new = (530, 540)
        c2_new = (1330, 740)
        scene.add(TranslateToAnimation(start_time=t_kmeans + 12.0, duration=2.0, data={"point": c1_new}), drawable=centroid1)
        scene.add(TranslateToAnimation(start_time=t_kmeans + 12.0, duration=2.0, data={"point": c2_new}), drawable=centroid2)

        eraser_km = Eraser(objects_to_erase=[km_title, centroid1, centroid2, *raw_dots, *red_cluster, *blue_cluster], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=eraser_km)

        # --- SECTION 5: OUTRO ---
        outro_msg = Text("Organizing the World's Data", position=(960, 540), font_size=90, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=outro_msg)

    # 3. Render
    scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()