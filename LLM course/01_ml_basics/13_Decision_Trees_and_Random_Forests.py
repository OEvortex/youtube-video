import os
import asyncio
import re
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("Please install edge-tts: pip install edge-tts")
    exit()

from handanim.animations import (
    SketchAnimation,
    FadeInAnimation,
    TranslateToAnimation,
)
from handanim.core import (
    FillStyle,
    Scene,
    SketchStyle,
    StrokeStyle,
    DrawableGroup,
)
from handanim.primitives import (
    Arrow,
    Circle,
    Line,
    Rectangle,
    Text,
    Eraser,
    FlowchartProcess,
    FlowchartDecision,
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
    PASTEL_RED,
    PASTEL_PURPLE,
)

# --- Configuration ---
WIDTH = 1920
HEIGHT = 1088
FONT_NAME = "cabin_sketch"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_PATH = os.path.join(OUTPUT_DIR, "trees_forests_narration.mp3")
VIDEO_PATH = os.path.join(OUTPUT_DIR, "trees_forests_whiteboard.mp4")

VOICE = "en-US-GuyNeural"
VOICE_RATE = "+5%"
SKETCH = SketchStyle(roughness=1.2, bowing=1.0, disable_font_mixture=True)

# --- Narration Script ---
NARRATION = (
    "<bookmark mark='intro'/> Decision Trees and Random Forests are among the most intuitive and powerful tools in machine learning. "
    "They mimic the way humans make decisions—by asking a series of questions. "
    "<bookmark mark='tree_start'/> A Decision Tree starts with a single node, called the Root. "
    "From there, it splits into branches based on specific features of the data. "
    "Each internal node represents a question, like 'Is the temperature above 30 degrees?' "
    "The final nodes are called Leaves, which provide the prediction, such as 'Yes, it will rain' or 'No, it won't'. "
    "<bookmark mark='overfit_start'/> However, a single Decision Tree has a major weakness: Overfitting. "
    "It can become so complex and specific to the training data that it fails to generalize to new information. "
    "<bookmark mark='forest_start'/> To solve this, we use a Random Forest. "
    "Instead of relying on one tree, we build an ensemble of many trees. "
    "Each tree is trained on a random subset of the data and a random subset of features. "
    "This diversity ensures that the trees don't all make the same mistakes. "
    "<bookmark mark='voting_start'/> When it's time to make a prediction, every tree in the forest gets a vote. "
    "The Random Forest takes the majority vote for classification, or the average for regression. "
    "This 'Wisdom of the Crowd' makes the model incredibly robust and accurate. "
    "<bookmark mark='outro'/> From simple flowcharts to massive ensembles, these algorithms are the workhorses of modern data science. "
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

def main():
    # 1. Synthesize Audio
    asyncio.run(synthesize_narration(AUDIO_PATH, NARRATION))

    # 2. Setup Scene
    scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=WHITE)
    scene.set_viewport_to_identity()

    with scene.voiceover(AUDIO_PATH, text=NARRATION) as tracker:
        t_intro = tracker.bookmark_time("intro")
        t_tree = tracker.bookmark_time("tree_start")
        t_overfit = tracker.bookmark_time("overfit_start")
        t_forest = tracker.bookmark_time("forest_start")
        t_voting = tracker.bookmark_time("voting_start")
        t_outro = tracker.bookmark_time("outro")

        # --- SECTION 1: INTRO ---
        title = Text("Decision Trees & Random Forests", position=(960, 400), font_size=100, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        subtitle = Text("The Logic of Branching Choices", position=(960, 550), font_size=60, color=DARK_GRAY, font_name=FONT_NAME, sketch_style=SKETCH)
        
        scene.add(SketchAnimation(start_time=t_intro, duration=2.5), drawable=title)
        scene.add(SketchAnimation(start_time=t_intro + 3.0, duration=2.0), drawable=subtitle)

        eraser_intro = Eraser(objects_to_erase=[title, subtitle], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_tree - 1.0, duration=1.0), drawable=eraser_intro)

        # --- SECTION 2: DECISION TREE ---
        tree_title = Text("1. The Decision Tree", position=(400, 100), font_size=80, color=GREEN, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Root Node
        root = FlowchartDecision("Is it Sunny?", top_left=(810, 200), width=300, height=150, font_size=40, font_name=FONT_NAME, fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3))
        
        # Branches
        branch_l = Arrow(start_point=(810, 275), end_point=(600, 450), stroke_style=StrokeStyle(color=BLACK, width=3))
        branch_r = Arrow(start_point=(1110, 275), end_point=(1320, 450), stroke_style=StrokeStyle(color=BLACK, width=3))
        txt_yes = Text("Yes", position=(650, 330), font_size=30, font_name=FONT_NAME)
        txt_no = Text("No", position=(1250, 330), font_size=30, font_name=FONT_NAME)

        # Internal Node
        node_l = FlowchartDecision("Humidity > 70%?", top_left=(450, 450), width=300, height=150, font_size=35, font_name=FONT_NAME, fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3))
        
        # Leaves
        leaf_no = FlowchartProcess("Don't Play", top_left=(1170, 450), width=300, height=100, font_size=40, font_name=FONT_NAME, fill_style=FillStyle(color=PASTEL_RED, opacity=0.3))
        leaf_yes = FlowchartProcess("Go Play!", top_left=(450, 700), width=300, height=100, font_size=40, font_name=FONT_NAME, fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3))
        branch_ll = Arrow(start_point=(600, 600), end_point=(600, 700), stroke_style=StrokeStyle(color=BLACK, width=3))

        scene.add(SketchAnimation(start_time=t_tree, duration=1.5), drawable=tree_title)
        scene.add(SketchAnimation(start_time=t_tree + 2.0, duration=1.5), drawable=root)
        scene.add(SketchAnimation(start_time=t_tree + 4.0, duration=0.8), drawable=branch_l)
        scene.add(SketchAnimation(start_time=t_tree + 4.0, duration=0.8), drawable=branch_r)
        scene.add(SketchAnimation(start_time=t_tree + 4.5, duration=0.5), drawable=txt_yes)
        scene.add(SketchAnimation(start_time=t_tree + 4.5, duration=0.5), drawable=txt_no)
        scene.add(SketchAnimation(start_time=t_tree + 6.0, duration=1.5), drawable=node_l)
        scene.add(SketchAnimation(start_time=t_tree + 6.0, duration=1.5), drawable=leaf_no)
        scene.add(SketchAnimation(start_time=t_tree + 8.0, duration=0.8), drawable=branch_ll)
        scene.add(SketchAnimation(start_time=t_tree + 9.0, duration=1.5), drawable=leaf_yes)

        # --- SECTION 3: OVERFITTING ---
        overfit_msg = Text("Problem: Overfitting (Too Complex)", position=(960, 950), font_size=50, color=RED, font_name=FONT_NAME, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_overfit, duration=2.0), drawable=overfit_msg)

        eraser_tree = Eraser(objects_to_erase=[tree_title, root, branch_l, branch_r, txt_yes, txt_no, node_l, leaf_no, branch_ll, leaf_yes, overfit_msg], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_forest - 1.0, duration=1.0), drawable=eraser_tree)

        # --- SECTION 4: RANDOM FOREST ---
        forest_title = Text("2. The Random Forest", position=(450, 100), font_size=80, color=ORANGE, font_name=FONT_NAME, sketch_style=SKETCH)
        
        # Draw multiple mini trees
        def make_mini_tree(pos, color):
            x, y = pos
            r = Circle(center=(x, y), radius=30, fill_style=FillStyle(color=color, opacity=0.4))
            l1 = Line(start=(x, y+30), end=(x-40, y+80), stroke_style=StrokeStyle(color=BLACK, width=2))
            l2 = Line(start=(x, y+30), end=(x+40, y+80), stroke_style=StrokeStyle(color=BLACK, width=2))
            c1 = Circle(center=(x-40, y+80), radius=20, fill_style=FillStyle(color=color, opacity=0.2))
            c2 = Circle(center=(x+40, y+80), radius=20, fill_style=FillStyle(color=color, opacity=0.2))
            return DrawableGroup(elements=[r, l1, l2, c1, c2])

        tree1 = make_mini_tree((400, 350), GREEN)
        tree2 = make_mini_tree((700, 350), BLUE)
        tree3 = make_mini_tree((1000, 350), PURPLE)
        tree4 = make_mini_tree((1300, 350), RED)
        tree5 = make_mini_tree((1600, 350), ORANGE)

        bagging_txt = Text("Bagging: Random Data + Random Features", position=(960, 550), font_size=45, color=DARK_GRAY, font_name=FONT_NAME)

        scene.add(SketchAnimation(start_time=t_forest, duration=1.5), drawable=forest_title)
        scene.add(SketchAnimation(start_time=t_forest + 2.0, duration=1.0), drawable=tree1)
        scene.add(SketchAnimation(start_time=t_forest + 2.5, duration=1.0), drawable=tree2)
        scene.add(SketchAnimation(start_time=t_forest + 3.0, duration=1.0), drawable=tree3)
        scene.add(SketchAnimation(start_time=t_forest + 3.5, duration=1.0), drawable=tree4)
        scene.add(SketchAnimation(start_time=t_forest + 4.0, duration=1.0), drawable=tree5)
        scene.add(SketchAnimation(start_time=t_forest + 6.0, duration=2.0), drawable=bagging_txt)

        # --- SECTION 5: VOTING ---
        vote_box = Rectangle(top_left=(400, 650), width=1120, height=250, stroke_style=StrokeStyle(color=BLACK, width=3), fill_style=FillStyle(color=PASTEL_PURPLE, opacity=0.1), sketch_style=SKETCH)
        v1 = Text("Class A", position=(400, 750), font_size=40, color=GREEN, font_name=FONT_NAME)
        v2 = Text("Class A", position=(700, 750), font_size=40, color=GREEN, font_name=FONT_NAME)
        v3 = Text("Class B", position=(1000, 750), font_size=40, color=RED, font_name=FONT_NAME)
        v4 = Text("Class A", position=(1300, 750), font_size=40, color=GREEN, font_name=FONT_NAME)
        v5 = Text("Class A", position=(1600, 750), font_size=40, color=GREEN, font_name=FONT_NAME)
        
        final_vote = Text("Majority Vote: Class A", position=(960, 850), font_size=60, color=GREEN, font_name=FONT_NAME, sketch_style=SKETCH)

        scene.add(SketchAnimation(start_time=t_voting, duration=1.5), drawable=vote_box)
        scene.add(FadeInAnimation(start_time=t_voting + 2.0, duration=0.5), drawable=v1)
        scene.add(FadeInAnimation(start_time=t_voting + 2.5, duration=0.5), drawable=v2)
        scene.add(FadeInAnimation(start_time=t_voting + 3.0, duration=0.5), drawable=v3)
        scene.add(FadeInAnimation(start_time=t_voting + 3.5, duration=0.5), drawable=v4)
        scene.add(FadeInAnimation(start_time=t_voting + 4.0, duration=0.5), drawable=v5)
        scene.add(SketchAnimation(start_time=t_voting + 6.0, duration=2.0), drawable=final_vote)

        eraser_forest = Eraser(objects_to_erase=[forest_title, tree1, tree2, tree3, tree4, tree5, bagging_txt, vote_box, v1, v2, v3, v4, v5, final_vote], drawable_cache=scene.drawable_cache)
        scene.add(SketchAnimation(start_time=t_outro - 1.0, duration=1.0), drawable=eraser_forest)

        # --- SECTION 6: OUTRO ---
        outro_msg = Text("Robust, Scalable, and Accurate", position=(960, 540), font_size=90, color=BLUE, font_name=FONT_NAME, sketch_style=SKETCH)
        scene.add(SketchAnimation(start_time=t_outro, duration=3.0), drawable=outro_msg)

    # 3. Render
    scene.render(VIDEO_PATH, max_length=tracker.end_time + 2)

if __name__ == "__main__":
    main()