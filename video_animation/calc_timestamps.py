import os
import sys

# Add the directory containing deepseek_v4_architecture to sys.path
script_dir = r"c:\Users\koula\Desktop\CODEBASE\Projects\OEvortex\handanim-2\youtube-video\video_animation"
sys.path.append(script_dir)

import asyncio
from handanim.core import Scene
from multihead_attention import (
    scene_title,
    scene_attention_intuition,
    scene_qkv_explained,
    scene_attention_scores,
    scene_multiple_heads,
    scene_complete_flow,
    scene_key_insights,
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
        ("Cinematic Title", scene_title),
        ("The Attention Intuition", scene_attention_intuition),
        ("Query, Key, and Value Explained", scene_qkv_explained),
        ("Attention Score Calculation", scene_attention_scores),
        ("Why Multiple Heads?", scene_multiple_heads),
        ("Complete Flow", scene_complete_flow),
        ("Key Insights", scene_key_insights),
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
