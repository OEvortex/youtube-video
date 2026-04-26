"""
Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter
Animation based on arXiv paper: https://arxiv.org/html/2604.15039v1

This animation explains:
1. The problem with current Prefill-Decode (PD) disaggregation
2. How hybrid attention changes the game
3. The PrfaaS-PD architecture
4. The results and benefits
"""

import os
import edge_tts
from handanim.core import Scene, FillStyle, StrokeStyle, SketchStyle, DrawableGroup
from handanim.animations import (
    SketchAnimation, FadeInAnimation, FadeOutAnimation,
    TransformAnimation, ReplacementTransformAnimation,
    TranslateToAnimation, ZoomInAnimation, ZoomOutAnimation,
)
from handanim.primitives import (
    Text, Math, Rectangle, Circle, Arrow, Line,
    Polygon, RoundedRectangle, FlowchartProcess, FlowchartDecision,
    FlowchartTerminator, FlowchartConnector,
)
from handanim.stylings.color import (
    BLACK, WHITE, BLUE, RED, GREEN, ORANGE, PURPLE,
    PASTEL_BLUE, PASTEL_GREEN, PASTEL_ORANGE, PASTEL_RED,
    GRAY, DARK_GRAY, LIGHT_GRAY, YELLOW,
)


def main() -> None:
    scene = Scene(width=1920, height=1088, fps=24, background_color=WHITE)
    FONT_NAME = "feasibly"
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "prefill_as_a_service.mp4")

    # ========================================
    # SCENE 1: Title and Introduction
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Prefill as a Service: KVCache of Next-Generation Models Could Go Cross-Datacenter",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        # Title
        title = Text(
            text="Prefill-as-a-Service",
            position=(960, 300),
            font_size=96,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        
        subtitle = Text(
            text="KVCache of Next-Generation Models Could Go Cross-Datacenter",
            position=(960, 420),
            font_size=42,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            font_name=FONT_NAME,
        )
        
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1.5), drawable=subtitle)
        
        # Fade out title
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 4, duration=1), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 4, duration=1), drawable=subtitle)
    
    # ========================================
    # SCENE 2: The Problem with Current PD
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="The problem is the bandwidth wall. Current Prefill-Decode disaggregation requires high-bandwidth RDMA networks, confining it to a single datacenter. This limits heterogeneous serving because prefill and decode must be in the same tightly coupled network domain.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        # Problem statement
        problem_title = Text(
            text="The Problem: Bandwidth Wall",
            position=(960, 200),
            font_size=72,
            stroke_style=StrokeStyle(color=RED, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=problem_title)
        
        # Draw single datacenter diagram
        dc_box = RoundedRectangle(
            top_left=(260, 350),
            width=1400,
            height=400,
            border_radius=20,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        dc_label = Text(
            text="Single Datacenter (RDMA Network)",
            position=(960, 750),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1.5), drawable=dc_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=1), drawable=dc_label)
        
        # Prefill node
        prefill_box = Rectangle(
            top_left=(350, 420),
            width=300,
            height=200,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        prefill_text = Text(
            text="Prefill",
            position=(500, 520),
            font_size=48,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        prefill_subtext = Text(
            text="Compute-Intensive",
            position=(500, 560),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=1), drawable=prefill_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=0.5), drawable=prefill_text)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.7, duration=0.5), drawable=prefill_subtext)
        
        # Decode node
        decode_box = Rectangle(
            top_left=(1270, 420),
            width=300,
            height=200,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        decode_text = Text(
            text="Decode",
            position=(1420, 520),
            font_size=48,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        decode_subtext = Text(
            text="Memory-Bandwidth",
            position=(1420, 560),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=1), drawable=decode_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=0.5), drawable=decode_text)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.7, duration=0.5), drawable=decode_subtext)
        
        # KVCache transfer arrow
        kv_arrow = Arrow(
            start_point=(650, 520),
            end_point=(1270, 520),
            arrow_head_type="->",
            arrow_head_size=30,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=RED, width=4),
        )
        kv_label = Text(
            text="KVCache Transfer",
            position=(960, 480),
            font_size=32,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        kv_bandwidth = Text(
            text="60 Gbps (Too High!)",
            position=(960, 520),
            font_size=28,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=1), drawable=kv_arrow)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=0.5), drawable=kv_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.7, duration=0.5), drawable=kv_bandwidth)
        
        # Problem explanation
        problem_text = Text(
            text="• Requires high-bandwidth RDMA network\n• Confined to single datacenter\n• Limits heterogeneous serving",
            position=(960, 850),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 6.5, duration=1.5), drawable=problem_text)
        
        # Fade out scene 2
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=problem_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=dc_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=dc_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=prefill_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=prefill_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=prefill_subtext)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=decode_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=decode_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=decode_subtext)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=kv_arrow)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=kv_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=kv_bandwidth)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 9, duration=1.5), drawable=problem_text)
    
    # ========================================
    # SCENE 2.5: Hybrid Architecture Examples
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Flagship open-source models are adopting hybrid architectures. Qwen 3.5-397B uses a 3 to 1 linear-to-full ratio. MiMo V2-Flash uses a 5 to 1 sliding window to full ratio. Ring 2.5-1T uses a 7 to 1 linear-to-full ratio, achieving 36 times overall KV memory saving.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Hybrid Architecture Examples",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Qwen
        qwen_box = Rectangle(
            top_left=(160, 300),
            width=500,
            height=180,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        qwen_name = Text(
            text="Qwen 3.5-397B",
            position=(410, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        qwen_ratio = Text(
            text="3:1 linear-to-full",
            position=(410, 400),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=qwen_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=qwen_name)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.2, duration=0.5), drawable=qwen_ratio)
        
        # MiMo
        mimo_box = Rectangle(
            top_left=(710, 300),
            width=500,
            height=180,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        mimo_name = Text(
            text="MiMo V2-Flash",
            position=(960, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        mimo_ratio = Text(
            text="5:1 SWA-to-full",
            position=(960, 400),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=mimo_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=mimo_name)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=mimo_ratio)
        
        # Ring
        ring_box = Rectangle(
            top_left=(1260, 300),
            width=500,
            height=180,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        ring_name = Text(
            text="Ring 2.5-1T",
            position=(1510, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        ring_ratio = Text(
            text="7:1 linear-to-full",
            position=(1510, 400),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=ring_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=ring_name)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.2, duration=0.5), drawable=ring_ratio)
        
        # Key point
        key_point = Text(
            text="Key Point: Only full-attention layers produce\nKVCache that scales with sequence length",
            position=(960, 550),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1.5), drawable=key_point)
        
        # Ring savings
        ring_savings = Text(
            text="Ring 2.5-1T: 36× overall KV memory saving\n(4.5× from MLA + 8× from hybrid ratio)",
            position=(960, 650),
            font_size=32,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1.5), drawable=ring_savings)
        
        # Fade out scene 2.5
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=qwen_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=qwen_name)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=qwen_ratio)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=mimo_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=mimo_name)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=mimo_ratio)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=ring_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=ring_name)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=ring_ratio)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=key_point)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=ring_savings)
    
    # ========================================
    # SCENE 3: Hybrid Attention Changes the Game
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Hybrid attention changes everything. By interleaving linear-complexity layers with full-attention layers, hybrid models reduce KVCache by 13 times. This shifts the network boundary from RDMA to commodity Ethernet, making cross-datacenter transfer feasible.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        hybrid_title = Text(
            text="Hybrid Attention Changes Everything",
            position=(960, 200),
            font_size=72,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=hybrid_title)
        
        # Comparison
        dense_label = Text(
            text="Dense Attention (Conventional)",
            position=(480, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        hybrid_label = Text(
            text="Hybrid Attention (New)",
            position=(1440, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=dense_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=hybrid_label)
        
        # Dense model stats
        dense_box = Rectangle(
            top_left=(280, 400),
            width=400,
            height=250,
            stroke_style=StrokeStyle(color=RED, width=2),
            fill_style=FillStyle(color=PASTEL_RED, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        dense_kv = Text(
            text="KV Throughput: 60 Gbps",
            position=(480, 470),
            font_size=32,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        dense_growth = Text(
            text="KVCache: Grows linearly",
            position=(480, 520),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=dense_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=dense_kv)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=dense_growth)
        
        # Hybrid model stats
        hybrid_box = Rectangle(
            top_left=(1240, 400),
            width=400,
            height=250,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        hybrid_kv = Text(
            text="KV Throughput: 4.7 Gbps",
            position=(1440, 470),
            font_size=32,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        hybrid_growth = Text(
            text="KVCache: 13× smaller!",
            position=(1440, 520),
            font_size=28,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=hybrid_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=hybrid_kv)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.2, duration=0.5), drawable=hybrid_growth)
        
        # Arrow showing improvement
        improve_arrow = Arrow(
            start_point=(680, 525),
            end_point=(1240, 525),
            arrow_head_type="->",
            arrow_head_size=40,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=BLUE, width=4),
        )
        improve_text = Text(
            text="13× Reduction",
            position=(960, 500),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1), drawable=improve_arrow)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=0.5), drawable=improve_text)
        
        # Key insight
        insight_text = Text(
            text="Hybrid models reduce KVCache by interleaving\nlinear-complexity layers with full-attention layers",
            position=(960, 750),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1.5), drawable=insight_text)
        
        # Fade out scene 3
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=hybrid_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=dense_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=hybrid_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=dense_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=dense_kv)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=dense_growth)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=hybrid_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=hybrid_kv)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=hybrid_growth)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=improve_arrow)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=improve_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=insight_text)
    
    # ========================================
    # SCENE 4: PrfaaS-PD Architecture
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="The PrfaaS-PD architecture enables cross-datacenter KVCache transfer. PrfaaS clusters handle long-context prefills on high-throughput accelerators, while local clusters handle short requests and decode. A global scheduler routes requests based on characteristics, and a hybrid prefix cache manages different KVCache types.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        arch_title = Text(
            text="PrfaaS-PD Architecture",
            position=(960, 150),
            font_size=72,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=arch_title)
        
        # Local PD Cluster
        local_dc = RoundedRectangle(
            top_left=(100, 250),
            width=800,
            height=600,
            border_radius=20,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        local_label = Text(
            text="Local PD Cluster",
            position=(500, 820),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1.5), drawable=local_dc)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=1), drawable=local_label)
        
        # PrfaaS Cluster
        prfaas_dc = RoundedRectangle(
            top_left=(1020, 250),
            width=800,
            height=600,
            border_radius=20,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        prfaas_label = Text(
            text="PrfaaS Cluster (Remote)",
            position=(1420, 820),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1.5), drawable=prfaas_dc)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=1), drawable=prfaas_label)
        
        # Local prefill node
        local_prefill = Rectangle(
            top_left=(150, 350),
            width=250,
            height=150,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        local_prefill_text = Text(
            text="Local Prefill",
            position=(275, 425),
            font_size=28,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=local_prefill)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=local_prefill_text)
        
        # Local decode node
        local_decode = Rectangle(
            top_left=(150, 550),
            width=250,
            height=150,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        local_decode_text = Text(
            text="Local Decode",
            position=(275, 625),
            font_size=28,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=1), drawable=local_decode)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.2, duration=0.5), drawable=local_decode_text)
        
        # PrfaaS prefill node
        prfaas_prefill = Rectangle(
            top_left=(1070, 350),
            width=250,
            height=150,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        prfaas_prefill_text = Text(
            text="PrfaaS Prefill",
            position=(1195, 425),
            font_size=28,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        prfaas_prefill_sub = Text(
            text="High-Throughput",
            position=(1195, 455),
            font_size=20,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1), drawable=prfaas_prefill)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=0.5), drawable=prfaas_prefill_text)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.2, duration=0.5), drawable=prfaas_prefill_sub)
        
        # Cross-datacenter connection
        cross_arrow = Arrow(
            start_point=(900, 425),
            end_point=(1070, 425),
            arrow_head_type="->",
            arrow_head_size=30,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=PURPLE, width=4),
        )
        cross_label = Text(
            text="Ethernet",
            position=(985, 395),
            font_size=24,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )
        cross_bandwidth = Text(
            text="13 Gbps ✓",
            position=(985, 455),
            font_size=24,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1), drawable=cross_arrow)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 6, duration=0.5), drawable=cross_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 6.2, duration=0.5), drawable=cross_bandwidth)
        
        # Hybrid prefix cache pool
        cache_box = Rectangle(
            top_left=(1070, 550),
            width=700,
            height=200,
            stroke_style=StrokeStyle(color=YELLOW, width=2),
            fill_style=FillStyle(color=YELLOW, opacity=0.2),
            sketch_style=SketchStyle(roughness=2),
        )
        cache_text = Text(
            text="Hybrid Prefix Cache Pool",
            position=(1420, 620),
            font_size=32,
            stroke_style=StrokeStyle(color=YELLOW, width=2),
            font_name=FONT_NAME,
        )
        cache_sub = Text(
            text="Manages linear states & full-attention KVCache",
            position=(1420, 660),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=1),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 6.5, duration=1), drawable=cache_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 7, duration=0.5), drawable=cache_text)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 7.2, duration=0.5), drawable=cache_sub)
        
        # Global scheduler
        scheduler_box = Circle(
            center=(960, 300),
            radius=80,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        scheduler_text = Text(
            text="Global",
            position=(960, 290),
            font_size=24,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )
        scheduler_text2 = Text(
            text="Scheduler",
            position=(960, 320),
            font_size=24,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 7.5, duration=1), drawable=scheduler_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 8, duration=0.5), drawable=scheduler_text)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 8.2, duration=0.5), drawable=scheduler_text2)
        
        # Explanation
        arch_explain = Text(
            text="• PrfaaS clusters handle long-context prefills\n• Local clusters handle short requests & decode\n• Global scheduler routes based on request characteristics\n• Hybrid prefix cache manages different KVCache types",
            position=(960, 900),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 8.5, duration=1.5), drawable=arch_explain)
        
        # Fade out scene 4
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=arch_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=local_dc)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=local_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=prfaas_dc)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=prfaas_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=local_prefill)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=local_prefill_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=local_decode)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=local_decode_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=prfaas_prefill)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=prfaas_prefill_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=prfaas_prefill_sub)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=cross_arrow)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=cross_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=cross_bandwidth)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=cache_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=cache_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=cache_sub)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=scheduler_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=scheduler_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=scheduler_text2)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 11, duration=1.5), drawable=arch_explain)
    
    # ========================================
    # SCENE 4.5: Length-Based Routing Policy
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Not all requests benefit equally from PrfaaS. Short-context prefill is memory or communication bound rather than compute bound. We apply a length-based routing policy. When the incremental prefill length exceeds 19.4K tokens, the request is routed to PrfaaS. Otherwise, it's handled locally.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Length-Based Routing Policy",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Decision diagram
        request_box = Rectangle(
            top_left=(810, 240),
            width=300,
            height=80,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        request_text = Text(
            text="New Request",
            position=(960, 280),
            font_size=28,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=request_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=request_text)
        
        # Arrow down
        arrow1 = Arrow(
            start_point=(960, 320),
            end_point=(960, 380),
            arrow_head_type="->",
            arrow_head_size=20,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=0.5), drawable=arrow1)
        
        # Decision
        decision_box = Rectangle(
            top_left=(785, 380),
            width=350,
            height=100,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        decision_text = Text(
            text="Length > 19.4K?",
            position=(960, 430),
            font_size=32,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=1), drawable=decision_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=0.5), drawable=decision_text)
        
        # Yes path
        yes_arrow = Arrow(
            start_point=(1135, 430),
            end_point=(1300, 430),
            arrow_head_type="->",
            arrow_head_size=20,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=GREEN, width=2),
        )
        yes_text = Text(
            text="Yes",
            position=(1210, 410),
            font_size=24,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=yes_arrow)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=yes_text)
        
        # PrfaaS box
        prfaas_box = Rectangle(
            top_left=(1300, 390),
            width=250,
            height=80,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        prfaas_text = Text(
            text="Route to PrfaaS",
            position=(1425, 430),
            font_size=24,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1), drawable=prfaas_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=0.5), drawable=prfaas_text)
        
        # No path
        no_arrow = Arrow(
            start_point=(785, 430),
            end_point=(620, 430),
            arrow_head_type="->",
            arrow_head_size=20,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=RED, width=2),
        )
        no_text = Text(
            text="No",
            position=(700, 410),
            font_size=24,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=no_arrow)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=no_text)
        
        # Local box
        local_box = Rectangle(
            top_left=(370, 390),
            width=250,
            height=80,
            stroke_style=StrokeStyle(color=RED, width=2),
            fill_style=FillStyle(color=PASTEL_RED, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        local_text = Text(
            text="Route to Local",
            position=(495, 430),
            font_size=24,
            stroke_style=StrokeStyle(color=RED, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1), drawable=local_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=0.5), drawable=local_text)
        
        # Threshold info
        threshold_text = Text(
            text="Optimal threshold: 19.4K tokens\n~50% of requests offloaded to PrfaaS",
            position=(960, 600),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=1.5), drawable=threshold_text)
        
        # Rationale
        rationale = Text(
            text="Rationale: Short requests are memory/communication bound\nand cannot fully exploit compute-dense PrfaaS accelerators",
            position=(960, 700),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 6, duration=1.5), drawable=rationale)
        
        # Fade out scene 4.5
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=request_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=request_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=arrow1)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=decision_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=decision_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=yes_arrow)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=yes_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=prfaas_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=prfaas_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=no_arrow)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=no_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=local_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=local_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=threshold_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=rationale)
    
    # ========================================
    # SCENE 5: Results
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="The results are impressive. PrfaaS-PD achieves 54 percent higher throughput and 64 percent lower P90 time to first token compared to homogeneous PD-only baseline. The average PrfaaS cluster egress is only 13 gigabits per second, well within Ethernet capacity.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        results_title = Text(
            text="Results",
            position=(960, 200),
            font_size=96,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=results_title)
        
        # Result 1: Throughput
        throughput_box = Rectangle(
            top_left=(260, 350),
            width=600,
            height=200,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        throughput_label = Text(
            text="54% Higher Throughput",
            position=(560, 450),
            font_size=48,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            font_name=FONT_NAME,
        )
        throughput_sub = Text(
            text="vs homogeneous PD-only baseline",
            position=(560, 490),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=throughput_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=throughput_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.2, duration=0.5), drawable=throughput_sub)
        
        # Result 2: Latency
        latency_box = Rectangle(
            top_left=(1060, 350),
            width=600,
            height=200,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        latency_label = Text(
            text="64% Lower P90 TTFT",
            position=(1360, 450),
            font_size=48,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        latency_sub = Text(
            text="Time to First Token",
            position=(1360, 490),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=latency_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=latency_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=latency_sub)
        
        # Result 3: Bandwidth
        bandwidth_box = Rectangle(
            top_left=(460, 600),
            width=1000,
            height=150,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        bandwidth_label = Text(
            text="Average PrfaaS Egress: 13 Gbps (well within Ethernet capacity)",
            position=(960, 675),
            font_size=40,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=bandwidth_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=bandwidth_label)
        
        # Conclusion
        conclusion = Text(
            text="PrfaaS-PD enables cross-datacenter KVCache transfer,\nunlocking heterogeneous serving for next-generation LLMs",
            position=(960, 850),
            font_size=36,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1.5), drawable=conclusion)
    
    # ========================================
    # SCENE 5.5: Case Study Setup
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="To evaluate the architecture, we conducted a case study with two clusters connected by a 100 gigabit per second VPC network. The PrfaaS cluster uses 32 H200 GPUs for long-context prefill. The local PD cluster uses 64 H20 GPUs with 800 gigabit per second RDMA interconnect.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Case Study Setup",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Network
        network_box = Rectangle(
            top_left=(460, 250),
            width=1000,
            height=100,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        network_text = Text(
            text="100 Gbps VPC Network",
            position=(960, 300),
            font_size=36,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=network_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=network_text)
        
        # PrfaaS cluster
        prfaas_box = Rectangle(
            top_left=(160, 400),
            width=600,
            height=200,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        prfaas_title = Text(
            text="PrfaaS Cluster",
            position=(460, 450),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        prfaas_specs = Text(
            text="32 × H200 GPUs\nHigh compute throughput",
            position=(460, 510),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=prfaas_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=prfaas_title)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=prfaas_specs)
        
        # Local PD cluster
        local_box = Rectangle(
            top_left=(1160, 400),
            width=600,
            height=200,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        local_title = Text(
            text="Local PD Cluster",
            position=(1460, 450),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        local_specs = Text(
            text="64 × H20 GPUs\n800 Gbps RDMA interconnect",
            position=(1460, 510),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=local_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=local_title)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.2, duration=0.5), drawable=local_specs)
        
        # Model info
        model_text = Text(
            text="Model: 1T parameter hybrid model\nArchitecture: 3:1 KDA to MLA ratio\nWorkload: Log-normal distribution, mean 27K tokens",
            position=(960, 700),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1.5), drawable=model_text)
        
        # Baseline
        baseline_text = Text(
            text="Baseline: 96 × H20 GPUs (homogeneous PD)",
            position=(960, 800),
            font_size=28,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1), drawable=baseline_text)
        
        # Fade out scene 5.5
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=network_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=network_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_specs)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=local_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=local_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=local_specs)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=model_text)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=baseline_text)
    
    # ========================================
    # SCENE 6: Bandwidth Utilization Results
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="With the routing threshold set to 19.4K tokens, about 50 percent of requests are routed to PrfaaS. The aggregate PrfaaS egress load is approximately 13 gigabits per second, consuming only 13 percent of the Ethernet link. This confirms that hybrid model KVCache can be transported over commodity Ethernet.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Results: Bandwidth Utilization",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Bandwidth bar
        bar_bg = Rectangle(
            top_left=(260, 300),
            width=1400,
            height=80,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=bar_bg)
        
        # Used portion
        bar_used = Rectangle(
            top_left=(260, 300),
            width=182,
            height=80,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.8),
            sketch_style=SketchStyle(roughness=2),
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=1), drawable=bar_used)
        
        # Labels
        bar_label = Text(
            text="100 Gbps Ethernet Link",
            position=(960, 400),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        used_label = Text(
            text="13 Gbps used (13%)",
            position=(351, 275),
            font_size=28,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        available_label = Text(
            text="87 Gbps available",
            position=(1200, 275),
            font_size=28,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=0.5), drawable=bar_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=0.5), drawable=used_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=0.5), drawable=available_label)
        
        # Key metrics
        metrics = Text(
            text="Key Metrics:\n• Routing threshold: 19.4K tokens\n• Requests offloaded: 49.6%\n• Average offloaded length: 44K tokens\n• Egress bandwidth: 13 Gbps",
            position=(960, 550),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=1.5), drawable=metrics)
        
        # Conclusion
        conclusion = Text(
            text="Conclusion: Cross-datacenter KVCache is practical\nfor hybrid models with selective offloading",
            position=(960, 750),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1.5), drawable=conclusion)
        
        # Fade out scene 6
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=bar_bg)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=bar_used)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=bar_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=used_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=available_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=metrics)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=conclusion)
    
    # ========================================
    # SCENE 7: Throughput Comparison
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Compared to a homogeneous PD baseline of 96 H20 GPUs, the PrfaaS-PD configuration achieves 54 percent higher throughput. This is because the PrfaaS cluster's superior compute throughput allows the local PD cluster to free capacity for additional decode slots. The optimal local PD allocation is 3 prefill and 5 decode instances.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Results: Throughput Comparison",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=BLUE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Baseline bar
        baseline_box = Rectangle(
            top_left=(260, 300),
            width=500,
            height=200,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        baseline_label = Text(
            text="Homogeneous PD",
            position=(510, 360),
            font_size=36,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            font_name=FONT_NAME,
        )
        baseline_spec = Text(
            text="96 × H20 GPUs",
            position=(510, 410),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        baseline_value = Text(
            text="Baseline",
            position=(510, 460),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=baseline_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=baseline_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.2, duration=0.5), drawable=baseline_spec)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.4, duration=0.5), drawable=baseline_value)
        
        # PrfaaS-PD bar
        prfaas_box = Rectangle(
            top_left=(1160, 300),
            width=500,
            height=200,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.5),
            sketch_style=SketchStyle(roughness=2),
        )
        prfaas_label = Text(
            text="PrfaaS-PD",
            position=(1410, 360),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        prfaas_spec = Text(
            text="32 × H200 + 64 × H20",
            position=(1410, 410),
            font_size=28,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        prfaas_value = Text(
            text="+54% Throughput",
            position=(1410, 460),
            font_size=32,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=prfaas_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=prfaas_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=prfaas_spec)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.4, duration=0.5), drawable=prfaas_value)
        
        # Arrow
        improve_arrow = Arrow(
            start_point=(760, 400),
            end_point=(1160, 400),
            arrow_head_type="->",
            arrow_head_size=40,
            arrow_head_angle=45,
            stroke_style=StrokeStyle(color=BLUE, width=4),
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=improve_arrow)
        
        # Explanation
        explanation = Text(
            text="Why: PrfaaS cluster handles long-context prefill,\nfreeing local cluster capacity for more decode slots",
            position=(960, 600),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=1.5), drawable=explanation)
        
        # Optimal allocation
        allocation = Text(
            text="Optimal local PD allocation: 3 prefill + 5 decode instances",
            position=(960, 700),
            font_size=28,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5, duration=1), drawable=allocation)
        
        # Fade out scene 7
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=baseline_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=baseline_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=baseline_spec)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=baseline_value)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_spec)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=prfaas_value)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=improve_arrow)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=explanation)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=allocation)
    
    # ========================================
    # SCENE 8: Latency Improvement
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Another key benefit is the reduction in time to first token, especially for long-context requests. In the homogeneous baseline, long requests compete with short requests for prefill capacity, inflating queuing delays. With PrfaaS-PD, long requests are offloaded to the dedicated high-throughput cluster. Mean TTFT is reduced by 50 percent, and P90 TTFT by 64 percent.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Results: Latency Improvement",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=ORANGE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Mean TTFT
        mean_box = Rectangle(
            top_left=(260, 300),
            width=600,
            height=180,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        mean_label = Text(
            text="Mean TTFT",
            position=(560, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        mean_value = Text(
            text="-50%",
            position=(560, 410),
            font_size=48,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=mean_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=mean_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.2, duration=0.5), drawable=mean_value)
        
        # P90 TTFT
        p90_box = Rectangle(
            top_left=(1060, 300),
            width=600,
            height=180,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        p90_label = Text(
            text="P90 TTFT",
            position=(1360, 350),
            font_size=36,
            stroke_style=StrokeStyle(color=PURPLE, width=2),
            font_name=FONT_NAME,
        )
        p90_value = Text(
            text="-64%",
            position=(1360, 410),
            font_size=48,
            stroke_style=StrokeStyle(color=GREEN, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=p90_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=p90_label)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=p90_value)
        
        # Explanation
        explanation = Text(
            text="Why: Long requests no longer compete with short requests\nfor prefill capacity in the local cluster",
            position=(960, 550),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1.5), drawable=explanation)
        
        # TTFT definition
        ttft_def = Text(
            text="TTFT = Time to First Token\nMeasures how quickly users see the first response character",
            position=(960, 650),
            font_size=28,
            stroke_style=StrokeStyle(color=GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1), drawable=ttft_def)
        
        # Fade out scene 8
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=mean_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=mean_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=mean_value)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=p90_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=p90_label)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=p90_value)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=explanation)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 7, duration=1.5), drawable=ttft_def)
    
    # ========================================
    # SCENE 9: Discussion and Future Implications
    # ========================================
    
    with scene.group(
        tts_provider=edge_tts,
        speech="Cross-datacenter KVCache extends PD disaggregation from a single tightly coupled cluster to loosely connected heterogeneous clusters. This progress depends on coordinated advances in model architecture, system design, and hardware. KVCache-friendly architectures, compression techniques, and phase-specialized hardware all reinforce this trend.",
        voice="en-US-JennyNeural",
        rate="+8%",
    ):
        title = Text(
            text="Discussion & Future Implications",
            position=(960, 150),
            font_size=64,
            stroke_style=StrokeStyle(color=PURPLE, width=3),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor, duration=2), drawable=title)
        
        # Three trends
        trend1_box = Rectangle(
            top_left=(160, 300),
            width=500,
            height=200,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            fill_style=FillStyle(color=PASTEL_BLUE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        trend1_title = Text(
            text="KVCache-Friendly\nArchitecture",
            position=(410, 350),
            font_size=32,
            stroke_style=StrokeStyle(color=BLUE, width=2),
            font_name=FONT_NAME,
        )
        trend1_desc = Text(
            text="MLA, SWA, linear attention\nreduce KVCache size",
            position=(410, 420),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 1.5, duration=1), drawable=trend1_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2, duration=0.5), drawable=trend1_title)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.2, duration=0.5), drawable=trend1_desc)
        
        # Trend 2
        trend2_box = Rectangle(
            top_left=(710, 300),
            width=500,
            height=200,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            fill_style=FillStyle(color=PASTEL_GREEN, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        trend2_title = Text(
            text="KVCache Compression\n& Reuse",
            position=(960, 350),
            font_size=32,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        trend2_desc = Text(
            text="H2O, KIVI, CacheGen\nreduce memory pressure",
            position=(960, 420),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 2.5, duration=1), drawable=trend2_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3, duration=0.5), drawable=trend2_title)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.2, duration=0.5), drawable=trend2_desc)
        
        # Trend 3
        trend3_box = Rectangle(
            top_left=(1260, 300),
            width=500,
            height=200,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            fill_style=FillStyle(color=PASTEL_ORANGE, opacity=0.3),
            sketch_style=SketchStyle(roughness=2),
        )
        trend3_title = Text(
            text="Phase-Specialized\nHardware",
            position=(1510, 350),
            font_size=32,
            stroke_style=StrokeStyle(color=ORANGE, width=2),
            font_name=FONT_NAME,
        )
        trend3_desc = Text(
            text="Rubin CPX, LPU, Taalas\noptimize for prefill/decode",
            position=(1510, 420),
            font_size=24,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 3.5, duration=1), drawable=trend3_box)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4, duration=0.5), drawable=trend3_title)
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.2, duration=0.5), drawable=trend3_desc)
        
        # Key insight
        insight = Text(
            text="These trends reinforce each other, making\ncross-datacenter KVCache increasingly practical",
            position=(960, 600),
            font_size=32,
            stroke_style=StrokeStyle(color=DARK_GRAY, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 4.5, duration=1.5), drawable=insight)
        
        # Conclusion
        conclusion = Text(
            text="PrfaaS-PD enables the next generation of\nheterogeneous LLM serving at scale",
            position=(960, 750),
            font_size=36,
            stroke_style=StrokeStyle(color=GREEN, width=2),
            font_name=FONT_NAME,
        )
        scene.add(SketchAnimation(start_time=scene.timeline_cursor + 5.5, duration=1.5), drawable=conclusion)
        
        # Fade out scene 9
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend1_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend1_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend1_desc)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend2_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend2_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend2_desc)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend3_box)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend3_title)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=trend3_desc)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=insight)
        scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + 8, duration=1.5), drawable=conclusion)
    
    # Render
    scene.render(output_path)


if __name__ == "__main__":
    main()
