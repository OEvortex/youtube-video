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
    CompositeAnimationEvent,
)
from handanim.core import (
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
    YELLOW,
    CYAN,
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

# --- Detailed Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> Welcome to this lesson on Classification and Clustering, two fundamental approaches in Machine Learning for organizing data. "
    "Classification is Supervised Learning where we know the categories upfront. Clustering is Unsupervised Learning where we let the machine discover the groups. "
    "<bookmark mark='knn_start'/> Let's start with K-Nearest Neighbors, or KNN. "
    "It is one of the simplest and most intuitive classification algorithms. "
    "Imagine you have a new data point here, and you need to classify it. "
    "What do you do? You look at its K nearest neighbors. "
    "Here, with K equals 3, we find the three closest points. "
    "Two are Red and one is Blue. By majority vote, our new point becomes Red. "
    "This is the core idea of KNN: similarity through proximity. "
    "The key parameter is K, the number of neighbors to consider. "
    "Notice how changing K can change the result. With K equals 5, we might get a different classification. "
    "KNN is simple but powerful, though it can be slow for large datasets since we distance compute every query point. "
    "<bookmark mark='svm_start'/> Next, we have Support Vector Machines, or SVMs. "
    "Instead of voting, SVMs find a geometric solution. "
    "An SVM tries to draw a boundary, called a hyperplane, that maximizes the margin between two classes. "
    "The closest training points to this boundary are called Support Vectors. "
    "They literally support or define the position of the hyperplane. "
    "By maximizing this margin, the model gains robustness to noise and performs better on unseen data. "
    "What if the data is not linearly separable? No problem! "
    "SVMs use the Kernel Trick to project data into higher dimensions where a separation becomes possible. "
    "Think of it as looking at data from a different angle to find a clear split. "
    "This is how SVMs handle complex, non-linear patterns. "
    "<bookmark mark='kmeans_start'/> Now, let's move to Unsupervised Learning with K-Means Clustering. "
    "Unlike classification, we have no labels—we must find the groups ourselves. "
    "The algorithm has four simple steps. One: choose K, the number of clusters. "
    "Two: initialize K random centroid positions. "
    "Three: assign each data point to its nearest centroid. "
    "Four: move each centroid to the average center of its assigned points. "
    "Then we repeat steps three and four until convergence. "
    "Watch as the centroids move and points reassign until we find stable clusters. "
    "K-Means is fast and scalable, but the result depends on initial centroid positions. "
    "Different initializations can produce different clusters. "
    "<bookmark mark='outro'/> From the voting logic of KNN to the geometric boundaries of SVMs and the iterative grouping of K-Means, "
    "these three algorithms give us powerful tools to make sense of complex data. "
    "Choose KNN for simplicity, SVMs for geometric precision, and K-Means when you don't know the groups. "
    "Thanks for watching!"
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
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_knn = tracker.bookmark_time("knn_start")
        t_svm = tracker.bookmark_time("svm_start")
        t_kmeans = tracker.bookmark_time("kmeans_start")
        t_outro = tracker.bookmark_time("outro")

        # ═══════════════════════════════════════════════════════════════
        # SECTION 1: INTRO - Title and Comparison
        # ═══════════════════════════════════════════════════════════════
        title = Text("Classification & Clustering", position=(960, 280), font_size=100, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Two columns comparison
        col1_label = Text("Classification", position=(500, 500), font_size=55, color=RED, font_name=FONT_NAME)
        col1_desc = Text("Supervised Learning", position=(500, 570), font_size=35, color=RED, font_name=FONT_NAME)
        col1_ex = Text("✓ Categories known", position=(500, 620), font_size=30, color=GRAY, font_name=FONT_NAME)
        
        col2_label = Text("Clustering", position=(1420, 500), font_size=55, color=PURPLE, font_name=FONT_NAME)
        col2_desc = Text("Unsupervised Learning", position=(1420, 570), font_size=35, color=PURPLE, font_name=FONT_NAME)
        col2_ex = Text("? Find the groups", position=(1420, 620), font_size=30, color=GRAY, font_name=FONT_NAME)
        
        # Arrow between them
        arrow = Arrow(start_point=(700, 550), end_point=(1220, 550), stroke_style=StrokeStyle(color=BLACK, width=3), sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 2.5, duration=1.5), drawable=col1_label)
        scene.add(FadeInAnimation(start_time=t_intro + 3.0, duration=1.0), drawable=col1_desc)
        scene.add(FadeInAnimation(start_time=t_intro + 3.5, duration=1.0), drawable=col1_ex)
        scene.add(SketchAnimation(start_time=t_intro + 4.0, duration=1.5), drawable=col2_label)
        scene.add(FadeInAnimation(start_time=t_intro + 4.5, duration=1.0), drawable=col2_desc)
        scene.add(FadeInAnimation(start_time=t_intro + 5.0, duration=1.0), drawable=col2_ex)
        scene.add(SketchAnimation(start_time=t_intro + 5.5, duration=1.0), drawable=arrow)
        
        # Erase intro
        eraser_intro = Eraser(objects_to_erase=[title, col1_label, col1_desc, col1_ex, col2_label, col2_desc, col2_ex, arrow], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_knn - 1.0, duration=1.0), drawable=eraser_intro)

        # ═══════════════════════════════════════════════════════════════
        # SECTION 2: KNN - Detailed Visualization
        # ═══════════════════════════════════════════════════════════════
        knn_title = Text("1. K-Nearest Neighbors (KNN)", position=(960, 100), font_size=65, color=RED, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Grid/Axes
        xaxis = Line(start=(200, 700), end=(900, 700), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        yaxis = Line(start=(300, 500), end=(300, 900), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        axis_label_x = Text("Feature 1", position=(550, 940), font_size=30, color=DARK_GRAY, font_name=FONT_NAME)
        axis_label_y = Text("Feature 2", position=(150, 700), font_size=30, color=DARK_GRAY, font_name=FONT_NAME)
        
        # Training Data - Red Class
        red_pts = [(350, 600), (400, 550), (380, 480), (450, 520), (500, 580)]
        red_dots = [Circle(center=p, radius=14, fill_style=FillStyle(color=PASTEL_RED), stroke_style=StrokeStyle(color=RED, width=2)) for p in red_pts]
        red_label = Text("Red Class", position=(400, 420), font_size=35, color=RED, font_name=FONT_NAME)
        
        # Training Data - Blue Class  
        blue_pts = [(700, 650), (750, 600), (680, 520), (800, 580), (720, 700)]
        blue_dots = [Circle(center=p, radius=14, fill_style=FillStyle(color=PASTEL_BLUE), stroke_style=StrokeStyle(color=BLUE, width=2)) for p in blue_pts]
        blue_label = Text("Blue Class", position=(750, 460), font_size=35, color=BLUE, font_name=FONT_NAME)
        
        # Query Point
        query_pt = (550, 620)
        query_dot = Circle(center=query_pt, radius=18, fill_style=FillStyle(color=WHITE), stroke_style=StrokeStyle(color=BLACK, width=4))
        query_label = Text("?", position=(550, 620), font_size=40, font_name=FONT_NAME)
        
        # K-NN Circle - shows neighborhood
        neighbor_circle = Circle(center=query_pt, radius=150, stroke_style=StrokeStyle(color=GREEN, width=3, opacity=0.6), sketch_style=SKETCH)
        
        # Distance lines to neighbors
        dist_lines = [
            Line(start=query_pt, end=red_pts[2], stroke_style=StrokeStyle(color=GREEN, width=2, opacity=0.5)),
            Line(start=query_pt, end=red_pts[3], stroke_style=StrokeStyle(color=GREEN, width=2, opacity=0.5)),
            Line(start=query_pt, end=blue_pts[0], stroke_style=StrokeStyle(color=ORANGE, width=2, opacity=0.5)),
        ]
        
        # Result
        query_result = Circle(center=query_pt, radius=18, fill_style=FillStyle(color=PASTEL_RED), stroke_style=StrokeStyle(color=RED, width=3))
        
        # Formula
        formula = Text("New Point = RED (2 Red, 1 Blue → Majority Vote)", position=(550, 850), font_size=30, color=RED, font_name=FONT_NAME)
        
        # K parameter explanation
        k_label = Text("K = 3 nearest neighbors", position=(960, 1000), font_size=35, color=GREEN, font_name=FONT_NAME)
        
        scene.add(SketchAnimation(start_time=t_knn, duration=2.0), drawable=knn_title)
        scene.add(SketchAnimation(start_time=t_knn + 1.5, duration=1.0), drawable=xaxis)
        scene.add(SketchAnimation(start_time=t_knn + 1.5, duration=1.0), drawable=yaxis)
        scene.add(FadeInAnimation(start_time=t_knn + 2.0, duration=0.5), drawable=axis_label_x)
        scene.add(FadeInAnimation(start_time=t_knn + 2.0, duration=0.5), drawable=axis_label_y)
        
        # Draw red points with stagger
        for i, dot in enumerate(red_dots):
            scene.add(SketchAnimation(start_time=t_knn + 3.0 + i*0.15, duration=0.4), drawable=dot)
        scene.add(FadeInAnimation(start_time=t_knn + 4.0, duration=0.5), drawable=red_label)
        
        # Draw blue points with stagger
        for i, dot in enumerate(blue_dots):
            scene.add(SketchAnimation(start_time=t_knn + 5.0 + i*0.15, duration=0.4), drawable=dot)
        scene.add(FadeInAnimation(start_time=t_knn + 6.0, duration=0.5), drawable=blue_label)
        
        # Query point
        scene.add(SketchAnimation(start_time=t_knn + 7.5, duration=1.0), drawable=query_dot)
        scene.add(FadeInAnimation(start_time=t_knn + 8.0, duration=0.5), drawable=query_label)
        
        # Show K circle
        scene.add(SketchAnimation(start_time=t_knn + 9.5, duration=1.5), drawable=neighbor_circle)
        scene.add(FadeInAnimation(start_time=t_knn + 10.0, duration=0.5), drawable=k_label)
        
        # Show distances
        for line in dist_lines:
            scene.add(FadeInAnimation(start_time=t_knn + 11.0, duration=0.8), drawable=line)
        
        # Result
        scene.add(FadeInAnimation(start_time=t_knn + 13.0, duration=0.8), drawable=query_result)
        scene.add(FadeInAnimation(start_time=t_knn + 14.0, duration=0.5), drawable=formula)
        
        # Erase KNN section
        eraser_knn = Eraser(
            objects_to_erase=[knn_title, xaxis, yaxis, axis_label_x, axis_label_y,
                           neighbor_circle, query_dot, query_label, query_result, formula, k_label,
                           *red_dots, *blue_dots, *dist_lines, red_label, blue_label],
            drawable_cache=scene.drawable_cache
        )
        scene.add(SketchAnimation(start_time=t_svm - 1.0, duration=1.0), drawable=eraser_knn)

        # ═══════════════════════════════════════════════════════════════
        # SECTION 3: SVM - Detailed Visualization  
        # ═══════════════════════════════════════════════════════════════
        svm_title = Text("2. Support Vector Machines (SVM)", position=(960, 100), font_size=65, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # SVM Grid
        s_xaxis = Line(start=(200, 700), end=(900, 700), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        s_yaxis = Line(start=(300, 500), end=(300, 900), stroke_style=StrokeStyle(color=BLACK, width=2), sketch_style=SKETCH)
        
        # Separable Data - Red
        s_red_pts = [(350, 620), (420, 580), (380, 520), (480, 550)]
        s_red_dots = [Circle(center=p, radius=14, fill_style=FillStyle(color=PASTEL_RED), stroke_style=StrokeStyle(color=RED, width=2)) for p in s_red_pts]
        
        # Separable Data - Blue
        s_blue_pts = [(650, 620), (720, 580), (680, 520), (800, 550)]
        s_blue_dots = [Circle(center=p, radius=14, fill_style=FillStyle(color=PASTEL_BLUE), stroke_style=StrokeStyle(color=BLUE, width=2)) for p in s_blue_pts]
        
        # The Hyperplane (decision boundary)
        hyperplane = Line(start=(300, 400), end=(800, 900), stroke_style=StrokeStyle(color=BLACK, width=5), sketch_style=SKETCH)
        hyperplane_label = Text("Hyperplane", position=(520, 630), font_size=35, color=BLACK, font_name=FONT_NAME)
        
        # Margin lines
        margin1 = Line(start=(400, 350), end=(900, 800), stroke_style=StrokeStyle(color=GREEN, width=3, opacity=0.7), sketch_style=SKETCH)
        margin2 = Line(start=(200, 450), end=(700, 900), stroke_style=StrokeStyle(color=GREEN, width=3, opacity=0.7), sketch_style=SKETCH)
        
        # Support Vectors highlighted
        sv1 = Circle(center=s_red_pts[2], radius=20, stroke_style=StrokeStyle(color=GREEN, width=4), fill_style=FillStyle(color=PASTEL_RED))
        sv2 = Circle(center=s_blue_pts[2], radius=20, stroke_style=StrokeStyle(color=GREEN, width=4), fill_style=FillStyle(color=PASTEL_BLUE))
        sv_label = Text("Support Vectors", position=(550, 450), font_size=30, color=GREEN, font_name=FONT_NAME)
        
        # Margin annotation
        margin_text = Text("Maximum Margin", position=(650, 850), font_size=35, color=GREEN, font_name=FONT_NAME)
        
        # Kernel trick visualization
        kernel_title = Text("The Kernel Trick: Higher Dimensions", position=(960, 350), font_size=50, color=PURPLE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Show non-linear separability
        nonlinear_pts = [
            ((400, 500), (400, 700)), ((450, 520), (450, 720)),
            ((700, 500), (700, 700)), ((750, 520), (750, 720)),
        ]
        nonlinear_circles = [
            Circle(center=p[0], radius=12, fill_style=FillStyle(color=PASTEL_RED)) for p in nonlinear_pts
        ] + [
            Circle(center=p[1], radius=12, fill_style=FillStyle(color=PASTEL_BLUE)) for p in nonlinear_pts
        ]
        
        # 3D projection arrow
        proj_arrow = Arrow(start_point=(960, 600), end_point=(960, 750), stroke_style=StrokeStyle(color=PURPLE, width=4), sketch_style=SKETCH)
        proj_text = Text("Project to 3D → Find Plane", position=(960, 800), font_size=35, color=PURPLE, font_name=FONT_NAME)
        
        scene.add(SketchAnimation(start_time=t_svm, duration=2.0), drawable=svm_title)
        scene.add(SketchAnimation(start_time=t_svm + 1.5, duration=1.0), drawable=s_xaxis)
        scene.add(SketchAnimation(start_time=t_svm + 1.5, duration=1.0), drawable=s_yaxis)
        
        # Draw data
        for dot in s_red_dots + s_blue_dots:
            scene.add(FadeInAnimation(start_time=t_svm + 2.5, duration=0.5), drawable=dot)
        
        # Hyperplane
        scene.add(SketchAnimation(start_time=t_svm + 4.5, duration=2.0), drawable=hyperplane)
        scene.add(FadeInAnimation(start_time=t_svm + 5.0, duration=0.5), drawable=hyperplane_label)
        
        # Margins
        scene.add(SketchAnimation(start_time=t_svm + 7.0, duration=1.5), drawable=margin1)
        scene.add(SketchAnimation(start_time=t_svm + 7.0, duration=1.5), drawable=margin2)
        scene.add(FadeInAnimation(start_time=t_svm + 8.0, duration=0.5), drawable=margin_text)
        
        # Support vectors
        scene.add(SketchAnimation(start_time=t_svm + 10.0, duration=1.0), drawable=sv1)
        scene.add(SketchAnimation(start_time=t_svm + 10.0, duration=1.0), drawable=sv2)
        scene.add(FadeInAnimation(start_time=t_svm + 10.5, duration=0.5), drawable=sv_label)
        
        # Kernel trick
        scene.add(SketchAnimation(start_time=t_svm + 13.0, duration=2.0), drawable=kernel_title)
        for i, circle in enumerate(nonlinear_circles):
            scene.add(FadeInAnimation(start_time=t_svm + 14.0 + i*0.2, duration=0.5), drawable=circle)
        scene.add(SketchAnimation(start_time=t_svm + 16.0, duration=1.5), drawable=proj_arrow)
        scene.add(FadeInAnimation(start_time=t_svm + 16.5, duration=0.5), drawable=proj_text)
        
        # Erase SVM
        eraser_svm = Eraser(
            objects_to_erase=[svm_title, s_xaxis, s_yaxis, hyperplane, hyperplane_label,
                           margin1, margin2, margin_text, sv1, sv2, sv_label,
                           kernel_title, proj_arrow, proj_text, *s_red_dots, *s_blue_dots, *nonlinear_circles],
            drawable_cache=scene.drawable_cache
        )
        scene.add(SketchAnimation(start_time=t_kmeans - 1.0, duration=1.0), drawable=eraser_svm)

        # ═══════════════════════════════════════════════════════════════
        # SECTION 4: K-Means - Detailed Visualization
        # ═══════════════════════════════════════════════════════════════
        km_title = Text("3. K-Means Clustering", position=(960, 100), font_size=65, color=PURPLE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Step indicators
        step1 = Text("Step 1: Initialize Centroids", position=(960, 180), font_size=30, color=DARK_GRAY, font_name=FONT_NAME)
        step2 = Text("Step 2: Assign to Nearest", position=(960, 180), font_size=30, color=DARK_GRAY, font_name=FONT_NAME)
        step3 = Text("Step 3: Update Centroids", position=(960, 180), font_size=30, color=DARK_GRAY, font_name=FONT_NAME)
        step4 = Text("Step 4: Repeat until Convergence", position=(960, 180), font_size=30, color=DARK_GRAY, font_name=FONT_NAME)
        
        # Raw unlabeled data - two clusters
        k1_pts = [(350, 500), (400, 520), (380, 580), (420, 550), (360, 620)]
        k2_pts = [(650, 700), (700, 720), (680, 780), (720, 750), (660, 820)]
        
        raw_dots = [Circle(center=p, radius=12, fill_style=FillStyle(color=GRAY), stroke_style=StrokeStyle(color=BLACK, width=2)) 
                   for p in k1_pts + k2_pts]
        
        # K=2 centroids (initial)
        c1_init = (400, 450)
        c2_init = (700, 850)
        
        c1 = Circle(center=c1_init, radius=25, fill_style=FillStyle(color=PASTEL_RED), stroke_style=StrokeStyle(color=RED, width=3))
        c2 = Circle(center=c2_init, radius=25, fill_style=FillStyle(color=PASTEL_BLUE), stroke_style=StrokeStyle(color=BLUE, width=3))
        
        # Assignment lines (after first assignment)
        assign_lines_c1 = [Line(start=c1_init, end=p, stroke_style=StrokeStyle(color=RED, width=2, opacity=0.4)) for p in k1_pts]
        assign_lines_c2 = [Line(start=c2_init, end=p, stroke_style=StrokeStyle(color=BLUE, width=2, opacity=0.4)) for p in k2_pts]
        
        # Updated centroids
        c1_new = (390, 555)
        c2_new = (682, 755)
        
        # Final clusters with colors
        final_c1 = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_RED), stroke_style=StrokeStyle(color=RED, width=2)) for p in k1_pts]
        final_c2 = [Circle(center=p, radius=12, fill_style=FillStyle(color=PASTEL_BLUE), stroke_style=StrokeStyle(color=BLUE, width=2)) for p in k2_pts]
        
        scene.add(SketchAnimation(start_time=t_kmeans, duration=2.0), drawable=km_title)
        
        # Step 1: Initialize
        scene.add(FadeInAnimation(start_time=t_kmeans + 2.0, duration=0.5), drawable=step1)
        
        # Raw data
        for i, dot in enumerate(raw_dots):
            scene.add(FadeInAnimation(start_time=t_kmeans + 3.0 + i*0.1, duration=0.3), drawable=dot)
        
        # Initial centroids
        scene.add(CompositeAnimationEvent(events=[
            SketchAnimation(start_time=t_kmeans + 5.0, duration=1.0),
        ]), drawable=c1)
        scene.add(CompositeAnimationEvent(events=[
            SketchAnimation(start_time=t_kmeans + 5.0, duration=1.0),
        ]), drawable=c2)
        
        # Step 2: Assign
        scene.add(FadeInAnimation(start_time=t_kmeans + 7.0, duration=0.5), drawable=step2)
        for line in assign_lines_c1 + assign_lines_c2:
            scene.add(FadeInAnimation(start_time=t_kmeans + 7.5, duration=0.5), drawable=line)
        
        # Step 3: Update
        scene.add(FadeInAnimation(start_time=t_kmeans + 10.0, duration=0.5), drawable=step3)
        scene.add(TranslateToAnimation(start_time=t_kmeans + 11.0, duration=2.0, data={"point": c1_new}), drawable=c1)
        scene.add(TranslateToAnimation(start_time=t_kmeans + 11.0, duration=2.0, data={"point": c2_new}), drawable=c2)
        
        # Show final cluster assignments
        scene.add(FadeInAnimation(start_time=t_kmeans + 14.0, duration=0.5), drawable=step4)
        for i, dot in enumerate(final_c1):
            scene.add(FadeInAnimation(start_time=t_kmeans + 15.0 + i*0.1, duration=0.3), drawable=dot)
        for i, dot in enumerate(final_c2):
            scene.add(FadeInAnimation(start_time=t_kmeans + 15.5 + i*0.1, duration=0.3), drawable=dot)
        
        # Erase K-Means
        eraser_km = Eraser(
            objects_to_erase=[km_title, step1, step2, step3, step4, c1, c2,
                           *raw_dots, *assign_lines_c1, *assign_lines_c2, *final_c1, *final_c2],
            drawable_cache=scene.drawable_cache
        )
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=eraser_km)

        # ═══════════════════════════════════════════════════════════════
        # SECTION 5: OUTRO
        # ═══════════════════════════════════════════════════════════════
        outro_title = Text("Choosing Your Algorithm", position=(960, 350), font_size=70, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Decision guide
        guide1 = Text("KNN: When you need simplicity", position=(500, 500), font_size=35, color=RED, font_name=FONT_NAME)
        guide1_desc = Text("Works well with small data", position=(500, 560), font_size=28, color=GRAY, font_name=FONT_NAME)
        
        guide2 = Text("SVM: When precision matters", position=(750, 650), font_size=35, color=BLUE, font_name=FONT_NAME)
        guide2_desc = Text("Handles complex boundaries", position=(750, 710), font_size=28, color=GRAY, font_name=FONT_NAME)
        
        guide3 = Text("K-Means: When groups are unknown", position=(1200, 500), font_size=35, color=PURPLE, font_name=FONT_NAME)
        guide3_desc = Text("Scalable & fast", position=(1200, 560), font_size=28, color=GRAY, font_name=FONT_NAME)
        
        thanks = Text("Thanks for watching!", position=(960, 900), font_size=80, color=GREEN, font_name=FONT_NAME, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_outro, duration=2.5), drawable=outro_title)
        scene.add(FadeInAnimation(start_time=t_outro + 2.5, duration=1.0), drawable=guide1)
        scene.add(FadeInAnimation(start_time=t_outro + 3.0, duration=0.5), drawable=guide1_desc)
        scene.add(FadeInAnimation(start_time=t_outro + 4.0, duration=1.0), drawable=guide2)
        scene.add(FadeInAnimation(start_time=t_outro + 4.5, duration=0.5), drawable=guide2_desc)
        scene.add(FadeInAnimation(start_time=t_outro + 5.5, duration=1.0), drawable=guide3)
        scene.add(FadeInAnimation(start_time=t_outro + 6.0, duration=0.5), drawable=guide3_desc)
        scene.add(SketchAnimation(start_time=t_outro + 8.0, duration=2.0), drawable=thanks)

    # 3. Render
    scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()