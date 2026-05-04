import os
import sys

# Add the directory containing deepseek_v4_architecture to sys.path
script_dir = r"c:\Users\koula\Desktop\CODEBASE\Projects\OEvortex\handanim-2\youtube-video\video_animation"
sys.path.append(script_dir)

import asyncio
from handanim.core import Scene
from deepseek_v4_architecture import (
    scene_title, scene_context_problem, scene_architecture_overview,
    scene_mhc, scene_csa, scene_hca, scene_muon, scene_stability,
    scene_post_training, scene_benchmarks, scene_conclusion,
    EdgeTTSProvider, WHITE, W, H, FPS
)

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def main():
    scene = Scene(width=W, height=H, fps=FPS, background_color=WHITE)
    tts = EdgeTTSProvider()

    scenes = [
        ("Intro: DeepSeek-V4 Overview", scene_title),
        ("The Long-Context Bottleneck", scene_context_problem),
        ("Architecture Overview", scene_architecture_overview),
        ("Manifold-Constrained Hyper-Connections (mHC)", scene_mhc),
        ("Compressed Sparse Attention (CSA)", scene_csa),
        ("Heavily Compressed Attention (HCA)", scene_hca),
        ("The Muon Optimizer", scene_muon),
        ("Mitigating Training Instability", scene_stability),
        ("Post-Training: OPD Pipeline", scene_post_training),
        ("Benchmark Results", scene_benchmarks),
        ("Conclusion & Summary", scene_conclusion),
    ]

    print("# YouTube Chapters & Scene Timestamps")
    print("-" * 40)
    
    current_time = 0.0
    for name, fn in scenes:
        timestamp = format_timestamp(current_time)
        print(f"{timestamp} - {name}")
        
        # Build the scene to calculate its duration
        fn(scene, tts)
        new_total_time = scene.get_total_duration()
        scene_duration = new_total_time - current_time
        current_time = new_total_time

    print("-" * 40)
    print(f"Total Video Duration: {format_timestamp(current_time)}")

if __name__ == "__main__":
    main()
