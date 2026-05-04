"""
Voice Cloning: Complete Technical Deep Dive
===========================================
Comprehensive whiteboard animation explaining voice cloning technology
from traditional methods to state-of-the-art zero-shot systems.
RESTYLED: To match deepseek_v4_architecture.py animation style
"""

import os
import asyncio
import edge_tts
from handanim.core import Scene, FillStyle, StrokeStyle, SketchStyle, DrawableGroup
from handanim.primitives.eraser import Eraser
from handanim.core.scene import tts_speech
from handanim.animations import SketchAnimation, FadeInAnimation, FadeOutAnimation
from handanim.primitives import (
    Text, Rectangle, Circle, Arrow, Polygon
)

# ─────────────────────────────────────────────
# CANVAS & LAYOUT CONSTANTS  (1920 × 1080)
# ─────────────────────────────────────────────
W, H = 1920, 1080
SAFE_L, SAFE_R = 60, 1860        # horizontal safe zone
SAFE_T, SAFE_B = 60, 970         # vertical safe zone

# Two-column panel geometry
LP_X, LP_W = 60, 840             # left panel  : x=60..900
RP_X, RP_W = 1020, 840          # right panel : x=1020..1860
LP_CX = LP_X + LP_W // 2        # 480
RP_CX = RP_X + RP_W // 2        # 1440
CX = W // 2                     # 960  (full-width centre)

PANEL_TOP = 150                  # panels start below heading
PANEL_H   = 790                  # panels end at y=940 (< SAFE_B)

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
BLACK      = (0.05, 0.05, 0.05)
WHITE      = (0.98, 0.98, 0.98)
GRAY       = (0.55, 0.55, 0.55)
DARK_GRAY  = (0.22, 0.22, 0.22)
LIGHT_GRAY = (0.82, 0.82, 0.82)

BLUE       = (0.10, 0.35, 0.85)
DARK_BLUE  = (0.05, 0.20, 0.60)
SKY_BLUE   = (0.40, 0.70, 1.00)
CYAN       = (0.00, 0.75, 0.90)

GREEN      = (0.10, 0.72, 0.40)
DARK_GREEN = (0.05, 0.50, 0.25)

RED        = (0.88, 0.15, 0.20)
CORAL      = (1.00, 0.45, 0.40)

ORANGE     = (0.95, 0.55, 0.10)
AMBER      = (1.00, 0.75, 0.20)

PURPLE     = (0.55, 0.20, 0.80)
VIOLET     = (0.70, 0.45, 1.00)

PINK       = (0.92, 0.30, 0.65)
TEAL       = (0.10, 0.65, 0.65)
INDIGO     = (0.30, 0.25, 0.78)

PASTEL_BLUE   = (0.80, 0.88, 1.00)
PASTEL_GREEN  = (0.78, 0.96, 0.85)
PASTEL_RED    = (1.00, 0.82, 0.82)
PASTEL_ORANGE = (1.00, 0.91, 0.76)
PASTEL_PURPLE = (0.91, 0.82, 1.00)
PASTEL_CYAN   = (0.80, 0.96, 1.00)
PASTEL_MINT   = (0.85, 1.00, 0.90)
PASTEL_AMBER  = (1.00, 0.97, 0.82)

# Use better font and primary color
FONT  = "fredericka_the_great"
COLOR_PRIMARY = BLUE
FPS   = 24
VOICE = "en-US-JennyNeural"
RATE  = "+4%"
BG    = WHITE
SKETCH = SketchStyle(roughness=1.2, bowing=0.8, disable_font_mixture=True)

# ─────────────────────────────────────────────
# TTS PROVIDER
# ─────────────────────────────────────────────
class EdgeTTSProvider:
    @tts_speech
    def synthesize(self, speech: str, output_path: str, **kwargs) -> str:
        communicate = edge_tts.Communicate(speech, **kwargs)
        asyncio.run(communicate.save(output_path))
        return output_path


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def heading(text, color=BLUE, size=52):
    """Full-width scene heading at y=78."""
    return Text(text=text, position=(CX, 78), font_size=size,
                stroke_style=StrokeStyle(color=color, width=3), font_name=FONT)

def label(text, x, y, color=DARK_GRAY, size=30, width=2):
    return Text(text=text, position=(x, y), font_size=size,
                stroke_style=StrokeStyle(color=color, width=width), font_name=FONT)

def panel(x, y, w, h, stroke_col, fill_col, roughness=2):
    return Rectangle(
        top_left=(x, y), width=w, height=h,
        stroke_style=StrokeStyle(color=stroke_col, width=2),
        fill_style=FillStyle(color=fill_col, opacity=0.15),
        sketch_style=SketchStyle(roughness=roughness),
    )

def solid_rect(x, y, w, h, stroke_col, fill_col, opacity=0.55, roughness=1):
    return Rectangle(
        top_left=(x, y), width=w, height=h,
        stroke_style=StrokeStyle(color=stroke_col, width=2),
        fill_style=FillStyle(color=fill_col, opacity=opacity),
        sketch_style=SketchStyle(roughness=roughness),
    )

def arrow_down(x, y1, y2, color=ORANGE, width=3):
    return Arrow(
        start_point=(x, y1), end_point=(x, y2),
        arrow_head_type="->", arrow_head_size=22, arrow_head_angle=38,
        stroke_style=StrokeStyle(color=color, width=width),
    )

def arrow_right(x1, x2, y, color=ORANGE, width=3):
    return Arrow(
        start_point=(x1, y), end_point=(x2, y),
        arrow_head_type="->", arrow_head_size=22, arrow_head_angle=38,
        stroke_style=StrokeStyle(color=color, width=width),
    )

def sketch(scene, drawable, t, dur=1.0):
    scene.add(SketchAnimation(start_time=scene.timeline_cursor + t, duration=dur),
              drawable=drawable)

def erase(scene, objects_to_erase, at, duration=1.5):
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.7, 0.7, 0.7), "radius": 15},
    )
    scene.add(SketchAnimation(start_time=scene.timeline_cursor + at, duration=duration), 
              drawable=eraser)

def fadeout(scene, elements, at):
    scene.add(FadeOutAnimation(start_time=scene.timeline_cursor + at, duration=1.5),
              drawable=DrawableGroup(elements=elements))


# ══════════════════════════════════════════════
# SCENE 1  ─  COLD OPEN
# ══════════════════════════════════════════════
def scene_cold_open(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "What if you could clone any voice from just three seconds of audio? "
            "That's not science fiction - that's zero-shot voice cloning, "
            "and it's revolutionizing everything from accessibility tools to content creation. "
            "In this video, we'll go deep — the science, the math, the architectures, "
            "from traditional methods to state-of-the-art models like VALL-E, F5-TTS, and NaturalSpeech 3. "
            "Let's dive in."
        ),
        voice=VOICE, rate=RATE,
    ):
        # Hook question
        hook = Text("What if you could clone any voice\nfrom just 3 seconds of audio?", 
                    position=(CX, 340), font_size=72,
                    stroke_style=StrokeStyle(color=BLUE, width=4), font_name=FONT)
        hook_sub = label("That's zero-shot voice cloning", CX, 560, DARK_GRAY, 52, 2)
        hook_ans = label("→  From Science to State-of-the-Art  ←", CX, 680, ORANGE, 56, 2)
        
        sketch(scene, hook, 0.3, 1.8)
        sketch(scene, hook_sub, 2.2, 1.2)
        sketch(scene, hook_ans, 4.5, 1.5)
        
        cold_open_items = [hook, hook_sub, hook_ans]
        erase(scene, cold_open_items, 7.5)


# ══════════════════════════════════════════════
# SCENE 2  ─  TITLE CARD
# ══════════════════════════════════════════════
def scene_title(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech="Welcome. Today we are going to master Voice Cloning.",
        voice=VOICE, rate=RATE,
    ):
        ttl = Text("Voice Cloning", position=(CX, 280), font_size=88,
                   stroke_style=StrokeStyle(color=BLUE, width=4), font_name=FONT)
        ttl2 = Text("The Complete Technical Deep Dive", position=(CX, 420), font_size=62,
                    stroke_style=StrokeStyle(color=BLUE, width=3), font_name=FONT)
        by_lbl = label("Speaker Embeddings · Neural Vocoders · Zero-Shot TTS", CX, 540, ORANGE, 46, 2)
        tag_lbl = label("Codec Models · Diffusion · Disentanglement", CX, 610, PURPLE, 42, 1)
        
        sketch(scene, ttl, 0.4, 1.8)
        sketch(scene, ttl2, 2.0, 1.2)
        sketch(scene, by_lbl, 3.2, 1.2)
        sketch(scene, tag_lbl, 4.5, 1.0)
        
        title_items = [ttl, ttl2, by_lbl, tag_lbl]
        erase(scene, title_items, 6.5)


# ══════════════════════════════════════════════
# SCENE 3  ─  INTRO
# ══════════════════════════════════════════════
def scene_intro(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Let me start with the basics. Voice cloning is the process of reproducing "
            "a person's vocal characteristics from audio samples. "
            "Modern systems capture four key attributes: pitch and tone — the natural highs and lows; "
            "speech rhythm — the timing and pauses; emotional nuances — how voice changes with context; "
            "and pronunciation or accent — the unique way someone articulates words. "
            "The evolution has been dramatic. Traditional methods required hours of recorded speech "
            "and days of training. Today's zero-shot systems can clone a voice in real time "
            "using just a few seconds of audio. This has enabled applications everywhere: "
            "accessibility tools for those who've lost their voice, automated dubbing for global content, "
            "virtual assistants that sound like you, and content creation at unprecedented scale."
        ),
        voice=VOICE, rate=RATE,
    ):
        intro_title = heading("What is Voice Cloning?", BLACK)
        sketch(scene, intro_title, 0.5, 1.0)
        
        # Four attributes in left panel
        lp = panel(LP_X, PANEL_TOP, LP_W, PANEL_H, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 1.0, 1.0)
        
        attrs = [
            ("Pitch & Tone", "Natural highs and lows", BLUE),
            ("Speech Rhythm", "Timing, pauses, speed", GREEN),
            ("Emotional Nuances", "Context-dependent changes", ORANGE),
            ("Pronunciation & Accent", "Unique articulation", PURPLE),
        ]
        t = 2.0
        attr_items = []
        ty = 220
        for name, desc, col in attrs:
            box = solid_rect(LP_X+60, ty-25, LP_W-120, 70, col, PASTEL_BLUE, 0.25)
            name_lbl = label(name, LP_X+120, ty-10, col, 38, 2)
            desc_lbl = label(desc, LP_X+400, ty-10, DARK_GRAY, 30, 1)
            attr_items.extend([box, name_lbl, desc_lbl])
            for item in [box, name_lbl, desc_lbl]:
                sketch(scene, item, t, 0.5)
                t += 0.1
            ty += 110
            t += 0.3
        
        # Evolution in right panel
        rp = panel(RP_X, PANEL_TOP, RP_W, PANEL_H, RED, PASTEL_RED)
        sketch(scene, rp, t, 1.0)
        t += 0.5
        
        evo_title = label("Evolution: Hours → Seconds", RP_CX, 200, RED, 42, 2)
        sketch(scene, evo_title, t, 0.8)
        t += 0.6
        
        # Traditional box
        trad_box = solid_rect(LP_X+100, 320, 300, 100, RED, PASTEL_RED, 0.30)
        trad_lbl = label("Traditional", LP_X+250, 300, RED, 32, 2)
        trad_sub = label("Hours of audio\nDays of training", LP_X+250, 350, DARK_GRAY, 24, 1)
        sketch(scene, trad_box, t, 0.6)
        sketch(scene, trad_lbl, t+0.2, 0.4)
        sketch(scene, trad_sub, t+0.3, 0.4)
        t += 0.8
        
        # Arrow
        arr = arrow_right(LP_X+400, RP_X+100, 360, BLACK, 4)
        sketch(scene, arr, t, 0.5)
        t += 0.5
        
        # Zero-shot box
        zero_box = solid_rect(RP_X+100, 320, 300, 100, GREEN, PASTEL_GREEN, 0.30)
        zero_lbl = label("Zero-Shot", RP_X+250, 300, GREEN, 32, 2)
        zero_sub = label("Seconds of audio\nReal-time", RP_X+250, 350, DARK_GRAY, 24, 1)
        sketch(scene, zero_box, t, 0.6)
        sketch(scene, zero_lbl, t+0.2, 0.4)
        sketch(scene, zero_sub, t+0.3, 0.4)
        t += 0.8
        
        # Applications
        apps_title = label("Applications:", CX, 680, BLACK, 44, 2)
        sketch(scene, apps_title, t, 0.6)
        t += 0.5
        
        apps = [
            "Accessibility tools",
            "Automated dubbing",
            "Virtual assistants",
            "Content creation"
        ]
        for i, app in enumerate(apps):
            lbl = label(f"• {app}", CX, 740+i*55, DARK_GRAY, 36, 1)
            sketch(scene, lbl, t, 0.4)
            t += 0.3
        
        intro_items = [intro_title, lp, rp, evo_title, trad_box, trad_lbl, trad_sub, arr, zero_box, zero_lbl, zero_sub, apps_title] + attr_items
        erase(scene, intro_items, 18.0)


# ══════════════════════════════════════════════
# SCENE 4  ─  SPEAKER EMBEDDINGS
# ══════════════════════════════════════════════
def scene_speaker_embeddings(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Speaker embeddings are the foundation of voice cloning. "
            "They're fixed-dimensional vectors that represent a speaker's unique identity. "
            "The evolution has been remarkable: from i-vectors using factor analysis on Gaussian Mixture Models, "
            "to x-vectors with Time-Delay Neural Networks and statistical pooling, "
            "to ECAPA-TDNN with channel attention and multi-layer aggregation. "
            "The x-vector architecture processes audio through TDNN layers, "
            "applies statistical pooling, passes through fully connected layers, "
            "and outputs the final embedding vector. "
            "ECAPA-TDNN improves this with channel attention and better multi-layer aggregation."
        ),
        voice=VOICE, rate=RATE,
    ):
        emb_title = heading("Speaker Embeddings", TEAL)
        sketch(scene, emb_title, 0.5, 1.0)
        
        # Concept box
        concept_box = solid_rect(CX-400, 180, 800, 80, CYAN, PASTEL_CYAN, 0.20)
        concept_lbl = label("Fixed-dimensional vector representing speaker identity", CX, 180, CYAN, 36, 1)
        sketch(scene, concept_box, 1.2, 0.8)
        sketch(scene, concept_lbl, 1.5, 0.6)
        
        # Evolution in two panels
        lp = panel(LP_X, PANEL_TOP+180, LP_W, 350, GRAY, LIGHT_GRAY)
        rp = panel(RP_X, PANEL_TOP+180, RP_W, 350, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 2.5, 1.0)
        sketch(scene, rp, 2.7, 1.0)
        
        # Left: i-vector
        ivec_box = solid_rect(LP_CX-120, 320, 240, 100, GRAY, LIGHT_GRAY, 0.30)
        ivec_lbl = label("i-vector", LP_CX, 300, GRAY, 34, 2)
        ivec_sub = label("Factor analysis on GMM", LP_CX, 350, DARK_GRAY, 26, 1)
        sketch(scene, ivec_box, 3.5, 0.6)
        sketch(scene, ivec_lbl, 3.7, 0.4)
        sketch(scene, ivec_sub, 3.8, 0.4)
        
        # Middle: x-vector
        xvec_box = solid_rect(CX-120, 320, 240, 100, BLUE, PASTEL_BLUE, 0.30)
        xvec_lbl = label("x-vector", CX, 300, BLUE, 34, 2)
        xvec_sub = label("TDNN + Stats Pooling", CX, 350, DARK_GRAY, 26, 1)
        sketch(scene, xvec_box, 4.2, 0.6)
        sketch(scene, xvec_lbl, 4.4, 0.4)
        sketch(scene, xvec_sub, 4.5, 0.4)
        
        # Right: ECAPA-TDNN
        ecapa_box = solid_rect(RP_CX+120, 320, 240, 100, PURPLE, PASTEL_PURPLE, 0.30)
        ecapa_lbl = label("ECAPA-TDNN", RP_CX, 300, PURPLE, 34, 2)
        ecapa_sub = label("Channel attention", RP_CX, 350, DARK_GRAY, 26, 1)
        sketch(scene, ecapa_box, 4.9, 0.6)
        sketch(scene, ecapa_lbl, 5.1, 0.4)
        sketch(scene, ecapa_sub, 5.2, 0.4)
        
        # Arrows between
        arr1 = arrow_right(LP_X+420, CX-140, 360, BLACK, 3)
        arr2 = arrow_right(CX+140, RP_X+100, 360, BLACK, 3)
        sketch(scene, arr1, 5.5, 0.4)
        sketch(scene, arr2, 5.6, 0.4)
        
        # x-vector architecture at bottom
        arch_title = label("x-vector Architecture:", CX-280, 500, BLACK, 38, 2)
        sketch(scene, arch_title, 6.0, 0.6)
        
        # Architecture diagram: TDNN -> Stats Pool -> FC -> Embedding
        tdnn = solid_rect(LP_X+150, 580, 150, 70, BLUE, PASTEL_BLUE, 0.30)
        tdnn_lbl = label("TDNN", LP_X+150, 580, BLUE, 28, 2)
        stat = solid_rect(LP_X+350, 580, 150, 70, ORANGE, PASTEL_ORANGE, 0.30)
        stat_lbl = label("Stats Pool", LP_X+350, 580, ORANGE, 28, 2)
        fc = solid_rect(LP_X+550, 580, 150, 70, GREEN, PASTEL_GREEN, 0.30)
        fc_lbl = label("FC", LP_X+550, 580, GREEN, 28, 2)
        emb = solid_rect(LP_X+750, 580, 150, 70, RED, PASTEL_RED, 0.30)
        emb_lbl = label("Embedding", LP_X+750, 580, RED, 28, 2)
        
        a1 = arrow_right(LP_X+220, LP_X+270, 580, BLACK, 3)
        a2 = arrow_right(LP_X+420, LP_X+470, 580, BLACK, 3)
        a3 = arrow_right(LP_X+620, LP_X+670, 580, BLACK, 3)
        
        sketch(scene, tdnn, 6.5, 0.5)
        sketch(scene, tdnn_lbl, 6.6, 0.3)
        sketch(scene, a1, 6.7, 0.2)
        sketch(scene, stat, 6.8, 0.5)
        sketch(scene, stat_lbl, 6.9, 0.3)
        sketch(scene, a2, 7.0, 0.2)
        sketch(scene, fc, 7.1, 0.5)
        sketch(scene, fc_lbl, 7.2, 0.3)
        sketch(scene, a3, 7.3, 0.2)
        sketch(scene, emb, 7.4, 0.5)
        sketch(scene, emb_lbl, 7.5, 0.3)
        
        ecapa_note = label("ECAPA-TDNN: Channel attention + Multi-layer aggregation", CX, 700, PURPLE, 34, 1)
        sketch(scene, ecapa_note, 8.0, 0.8)
        
        emb_items = [emb_title, concept_box, concept_lbl, lp, rp, ivec_box, ivec_lbl, ivec_sub, 
                     xvec_box, xvec_lbl, xvec_sub, ecapa_box, ecapa_lbl, ecapa_sub, 
                     arr1, arr2, arch_title, tdnn, tdnn_lbl, stat, stat_lbl, fc, fc_lbl, emb, emb_lbl,
                     a1, a2, a3, ecapa_note]
        erase(scene, emb_items, 14.5)


# ══════════════════════════════════════════════
# SCENE 5  ─  NEURAL VOCODERS
# ══════════════════════════════════════════════
def scene_neural_vocoders(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Neural vocoders convert mel-spectrograms back to audio waveforms. "
            "The evolution has been dramatic: from Griffin-Lim, which was iterative and slow, "
            "to WaveNet with autoregressive generation and high quality, "
            "to HiFiGAN, which is GAN-based and runs in real-time. "
            "HiFiGAN uses a generator with transposed convolutions "
            "and a multi-period, multi-scale discriminator in a GAN training setup. "
            "The benefits are near-human quality at real-time speeds."
        ),
        voice=VOICE, rate=RATE,
    ):
        voc_title = heading("Neural Vocoders", RED)
        sketch(scene, voc_title, 0.5, 1.0)
        
        # Problem statement
        prob_box = solid_rect(CX-400, 200, 800, 80, RED, PASTEL_RED, 0.20)
        prob_lbl = label("Convert mel-spectrogram back to waveform", CX, 200, RED, 36, 1)
        sketch(scene, prob_box, 1.2, 0.8)
        sketch(scene, prob_lbl, 1.5, 0.6)
        
        # Evolution panels
        lp = panel(LP_X, PANEL_TOP+150, LP_W, 250, GRAY, LIGHT_GRAY)
        rp = panel(RP_X, PANEL_TOP+150, RP_W, 250, ORANGE, PASTEL_ORANGE)
        sketch(scene, lp, 2.2, 1.0)
        sketch(scene, rp, 2.4, 1.0)
        
        # Griffin-Lim
        gl_box = solid_rect(LP_X+180, 340, 280, 100, GRAY, LIGHT_GRAY, 0.30)
        gl_lbl = label("Griffin-Lim", LP_X+320, 320, GRAY, 32, 2)
        gl_sub = label("Iterative, slow", LP_X+320, 370, DARK_GRAY, 26, 1)
        sketch(scene, gl_box, 3.0, 0.6)
        sketch(scene, gl_lbl, 3.2, 0.4)
        sketch(scene, gl_sub, 3.3, 0.4)
        
        # WaveNet
        wn_box = solid_rect(CX-140, 340, 280, 100, BLUE, PASTEL_BLUE, 0.30)
        wn_lbl = label("WaveNet", CX, 320, BLUE, 32, 2)
        wn_sub = label("Autoregressive, high quality", CX, 370, DARK_GRAY, 26, 1)
        sketch(scene, wn_box, 3.6, 0.6)
        sketch(scene, wn_lbl, 3.8, 0.4)
        sketch(scene, wn_sub, 3.9, 0.4)
        
        # HiFiGAN
        hfg_box = solid_rect(RP_X+100, 340, 280, 100, ORANGE, PASTEL_ORANGE, 0.30)
        hfg_lbl = label("HiFiGAN", RP_X+240, 320, ORANGE, 32, 2)
        hfg_sub = label("GAN-based, real-time", RP_X+240, 370, DARK_GRAY, 26, 1)
        sketch(scene, hfg_box, 4.2, 0.6)
        sketch(scene, hfg_lbl, 4.4, 0.4)
        sketch(scene, hfg_sub, 4.5, 0.4)
        
        # Arrows
        arr1 = arrow_right(LP_X+460, CX-140, 390, BLACK, 3)
        arr2 = arrow_right(CX+140, RP_X+100, 390, BLACK, 3)
        sketch(scene, arr1, 4.8, 0.4)
        sketch(scene, arr2, 4.9, 0.4)
        
        # HiFiGAN architecture at bottom
        hifi_title = label("HiFiGAN: Multi-period discriminator", CX-200, 520, ORANGE, 38, 2)
        sketch(scene, hifi_title, 5.2, 0.6)
        
        # Generator and Discriminator
        gen_box = solid_rect(LP_X+180, 620, 280, 100, GREEN, PASTEL_GREEN, 0.30)
        gen_lbl = label("Generator", LP_X+180, 590, GREEN, 32, 2)
        gen_sub = label("Transposed convolutions", LP_X+180, 650, DARK_GRAY, 24, 1)
        
        disc_box = solid_rect(RP_X+180, 620, 280, 100, PURPLE, PASTEL_PURPLE, 0.30)
        disc_lbl = label("Discriminator", RP_X+180, 590, PURPLE, 32, 2)
        disc_sub = label("Multi-period & multi-scale", RP_X+180, 650, DARK_GRAY, 24, 1)
        
        gan_arr = arrow_right(LP_X+460, RP_X+60, 620, BLACK, 4)
        gan_lbl = label("GAN Training", CX, 590, BLACK, 28, 1)
        
        sketch(scene, gen_box, 5.8, 0.6)
        sketch(scene, gen_lbl, 5.9, 0.4)
        sketch(scene, gen_sub, 6.0, 0.4)
        sketch(scene, gan_arr, 6.2, 0.5)
        sketch(scene, gan_lbl, 6.3, 0.4)
        sketch(scene, disc_box, 6.5, 0.6)
        sketch(scene, disc_lbl, 6.6, 0.4)
        sketch(scene, disc_sub, 6.7, 0.4)
        
        ben_title = label("Benefits: Near-human quality, Real-time", CX, 780, BLACK, 40, 2)
        sketch(scene, ben_title, 7.2, 0.8)
        
        voc_items = [voc_title, prob_box, prob_lbl, lp, rp, gl_box, gl_lbl, gl_sub, 
                     wn_box, wn_lbl, wn_sub, hfg_box, hfg_lbl, hfg_sub, arr1, arr2,
                     hifi_title, gen_box, gen_lbl, gen_sub, disc_box, disc_lbl, disc_sub, gan_arr, gan_lbl, ben_title]
        erase(scene, voc_items, 13.5)


# ══════════════════════════════════════════════
# SCENE 6  ─  TRADITIONAL TTS
# ══════════════════════════════════════════════
def scene_traditional_tts(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Traditional TTS pipelines follow a multi-stage process. "
            "Text is converted to phonemes, then duration is predicted, "
            "then acoustic features are generated, and finally a vocoder produces audio. "
            "Tacotron was a breakthrough end-to-end system with attention mechanisms. "
            "However, the limitation is that these systems are speaker-specific "
            "and require retraining for each new speaker."
        ),
        voice=VOICE, rate=RATE,
    ):
        trad_title = heading("Traditional TTS Pipeline", DARK_GRAY)
        sketch(scene, trad_title, 0.5, 1.0)
        
        # Pipeline boxes across the screen
        boxes = [
            ("Text", 220, BLUE), ("Phonemes", 480, GREEN), ("Duration", 740, ORANGE),
            ("Acoustic", 1000, PURPLE), ("Vocoder", 1260, RED)
        ]
        pipeline_boxes = []
        for name, cx, col in boxes:
            box = solid_rect(cx-80, 280, 160, 80, col, PASTEL_BLUE, 0.30)
            lbl = label(name, cx, 280, col, 32, 2)
            pipeline_boxes.extend([box, lbl])
        
        # Arrows between boxes
        arrs = [
            arrow_right(300, 380, 320, BLACK, 4),
            arrow_right(560, 640, 320, BLACK, 4),
            arrow_right(800, 880, 320, BLACK, 4),
            arrow_right(1060, 1140, 320, BLACK, 4),
        ]
        
        # Audio output
        audio_box = solid_rect(1260-80, 450, 160, 80, CYAN, PASTEL_CYAN, 0.30)
        audio_lbl = label("Audio", 1260, 450, CYAN, 32, 2)
        
        # Down arrow from vocoder to audio
        down_arr = arrow_down(1260, 340, 410, BLACK, 4)
        
        t = 1.5
        for item in pipeline_boxes + arrs + [audio_box, audio_lbl, down_arr]:
            sketch(scene, item, t, 0.5)
            t += 0.2
        
        # Tacotron title
        taco_title = label("Tacotron: End-to-End with Attention", CX, 600, BLUE, 42, 2)
        sketch(scene, taco_title, t, 0.8)
        t += 0.6
        
        # Limitation
        lim_title = label("Limitation: Speaker-specific, requires retraining", CX, 700, RED, 40, 2)
        sketch(scene, lim_title, t, 0.8)
        
        trad_items = [trad_title, taco_title, lim_title] + pipeline_boxes + arrs + [audio_box, audio_lbl, down_arr]
        erase(scene, trad_items, 10.5)


# ══════════════════════════════════════════════
# SCENE 7  ─  FEW-SHOT
# ══════════════════════════════════════════════
def scene_few_shot(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Few-shot voice cloning fine-tunes a base model on minutes of reference audio. "
            "Approaches include speaker adaptation, meta-learning like MAML and Reptile, "
            "and FastSpeech2 with speaker embeddings. "
            "The process involves taking a base model, adding reference audio, and fine-tuning. "
            "The trade-offs are better quality but more computation required."
        ),
        voice=VOICE, rate=RATE,
    ):
        few_title = heading("Few-Shot Voice Cloning", GREEN)
        sketch(scene, few_title, 0.5, 1.0)
        
        # Concept box
        concept_box = solid_rect(CX-400, 200, 800, 80, GREEN, PASTEL_GREEN, 0.20)
        concept_lbl = label("Fine-tune base model on minutes of reference audio", CX, 200, GREEN, 36, 1)
        sketch(scene, concept_box, 1.2, 0.8)
        sketch(scene, concept_lbl, 1.5, 0.6)
        
        # Approaches in left panel
        lp = panel(LP_X, PANEL_TOP+150, LP_W, 350, BLUE, PASTEL_BLUE)
        sketch(scene, lp, 2.2, 1.0)
        
        app_title = label("Approaches:", LP_CX, 250, BLACK, 40, 2)
        sketch(scene, app_title, 2.5, 0.6)
        
        approaches = [
            ("Speaker Adaptation", "Fine-tune on reference", 340, BLUE),
            ("Meta-Learning", "MAML, Reptile", 470, ORANGE),
            ("FastSpeech2", "Speaker embedding", 600, PURPLE),
        ]
        
        t = 3.0
        for name, desc, cy, col in approaches:
            box = solid_rect(LP_X+80, cy-40, LP_W-160, 80, col, PASTEL_BLUE, 0.25)
            name_lbl = label(name, LP_CX, cy-15, col, 34, 2)
            desc_lbl = label(desc, LP_CX, cy+25, DARK_GRAY, 28, 1)
            sketch(scene, box, t, 0.5)
            sketch(scene, name_lbl, t+0.2, 0.4)
            sketch(scene, desc_lbl, t+0.3, 0.4)
            t += 0.6
        
        # Right panel: Process diagram
        rp = panel(RP_X, PANEL_TOP+150, RP_W, 350, DARK_GRAY, LIGHT_GRAY)
        sketch(scene, rp, t, 1.0)
        t += 0.5
        
        # Process: Base + Reference -> Fine-tune
        base_box = solid_rect(RP_X+120, 340, 180, 70, BLUE, PASTEL_BLUE, 0.30)
        base_lbl = label("Base Model", RP_X+210, 340, BLUE, 28, 2)
        
        ref_box = solid_rect(RP_X+380, 340, 180, 70, GREEN, PASTEL_GREEN, 0.30)
        ref_lbl = label("Reference", RP_X+470, 340, GREEN, 28, 2)
        
        arr = arrow_right(RP_X+300, RP_X+380, 375, BLACK, 4)
        
        ft_box = solid_rect(RP_X+600, 340, 180, 70, ORANGE, PASTEL_ORANGE, 0.30)
        ft_lbl = label("Fine-tune", RP_X+690, 340, ORANGE, 28, 2)
        
        sketch(scene, base_box, t, 0.5)
        sketch(scene, base_lbl, t+0.2, 0.3)
        sketch(scene, ref_box, t+0.3, 0.5)
        sketch(scene, ref_lbl, t+0.4, 0.3)
        sketch(scene, arr, t+0.5, 0.3)
        sketch(scene, ft_box, t+0.6, 0.5)
        sketch(scene, ft_lbl, t+0.7, 0.3)
        
        # Trade-offs
        trade_title = label("Trade-offs: Better quality, but needs computation", CX, 600, BLACK, 40, 2)
        sketch(scene, trade_title, t+1.0, 0.8)
        
        few_items = [few_title, concept_box, concept_lbl, lp, rp, app_title, approaches,
                     base_box, base_lbl, ref_box, ref_lbl, arr, ft_box, ft_lbl, trade_title]
        erase(scene, few_items, 10.5)


# ══════════════════════════════════════════════
# SCENE 8  ─  ZERO-SHOT
# ══════════════════════════════════════════════
def scene_zero_shot(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Zero-shot voice cloning is a paradigm shift. Unlike few-shot methods that require fine-tuning, "
            "zero-shot systems utilize 'In-Context Learning'. By treating a three-second audio prompt "
            "as a prefix or a conditioning vector, the model generalizes to unseen speakers instantly. "
            "The science relies on high-dimensional latent spaces where the speaker's identity is "
            "mapped to a fixed point, allowing the model to 'project' new text into that specific vocal style."
        ),
        voice=VOICE, rate=RATE,
    ):
        zero_title = heading("The Zero-Shot Paradigm", ORANGE)
        sketch(scene, zero_title, 0.5, 1.0)
        
        # ICL box
        icl_box = solid_rect(CX-400, 200, 800, 90, ORANGE, PASTEL_ORANGE, 0.15)
        icl_lbl = label("In-Context Learning: No Training, Just Inference", CX, 200, ORANGE, 40, 1)
        sketch(scene, icl_box, 1.2, 0.8)
        sketch(scene, icl_lbl, 1.5, 0.6)
        
        # Three-step diagram: Prompt -> Latent -> Target
        # Step 1: Prompt
        prompt_box = solid_rect(300, 400, 200, 80, BLUE, PASTEL_BLUE, 0.30)
        prompt_lbl = label("3s Prompt", 400, 400, BLUE, 32, 2)
        sketch(scene, prompt_box, 2.5, 0.8)
        sketch(scene, prompt_lbl, 2.7, 0.5)
        
        # Arrow to latent space
        a1 = arrow_right(500, 760, 440, BLACK, 5)
        sketch(scene, a1, 3.5, 0.6)
        
        # Step 2: Latent space circle
        latent_circle = Circle(center=(960, 440), radius=80,
                               stroke_style=StrokeStyle(color=PURPLE, width=4),
                               sketch_style=SKETCH)
        latent_lbl = label("Latent\nSpace", 960, 440, PURPLE, 28, 1)
        sketch(scene, latent_circle, 4.2, 1.0)
        sketch(scene, latent_lbl, 4.5, 0.5)
        
        # Arrow to target
        a2 = arrow_right(1040, 1420, 440, BLACK, 5)
        sketch(scene, a2, 5.2, 0.6)
        
        # Step 3: Cloned speech
        target_box = solid_rect(1520-100, 400, 200, 80, GREEN, PASTEL_GREEN, 0.30)
        target_lbl = label("Cloned Speech", 1520, 400, GREEN, 32, 2)
        sketch(scene, target_box, 5.8, 0.8)
        sketch(scene, target_lbl, 6.0, 0.5)
        
        # Math formula
        math_lbl = label("f(Text, Prompt) = Cloned Audio", CX, 580, DARK_GRAY, 44, 2)
        sketch(scene, math_lbl, 7.0, 1.0)
        
        # Generation note
        gen_lbl = label("Zero-Shot = Generalization via Diversity", CX, 660, BLACK, 38, 2)
        sketch(scene, gen_lbl, 8.0, 0.8)
        
        zero_items = [zero_title, icl_box, icl_lbl, prompt_box, prompt_lbl, 
                      a1, latent_circle, latent_lbl, a2, target_box, target_lbl, 
                      math_lbl, gen_lbl]
        erase(scene, zero_items, 12.0)


# ══════════════════════════════════════════════
# SCENE 9  ─  CODEC-BASED
# ══════════════════════════════════════════════
def scene_codec_based(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Neural Audio Codecs like EnCodec and SoundStream are the 'alphabet' of modern TTS. "
            "They use Residual Vector Quantization (RVQ) to compress audio into discrete tokens. "
            "This discretization allows us to treat audio generation as a language modeling problem. "
            "Models like VALL-E or SPEAR-TTS don't predict waveforms; they predict these 'audio tokens', "
            "which are later reconstructed into high-fidelity speech by a neural decoder."
        ),
        voice=VOICE, rate=RATE,
    ):
        codec_title = heading("Neural Codecs & Audio Tokens", INDIGO)
        sketch(scene, codec_title, 0.5, 1.0)
        
        # RVQ explanation
        rvq_box = solid_rect(CX-400, 180, 800, 80, INDIGO, PASTEL_PURPLE, 0.20)
        rvq_lbl = label("Residual Vector Quantization (RVQ) → Discrete Units", CX, 180, INDIGO, 36, 1)
        sketch(scene, rvq_box, 1.2, 0.8)
        sketch(scene, rvq_lbl, 1.5, 0.6)
        
        # Encoder -> Quantization -> Decoder diagram
        # Encoder
        enc_box = solid_rect(300, 400, 200, 100, BLUE, PASTEL_BLUE, 0.30)
        enc_lbl = label("Encoder", 400, 400, BLUE, 32, 2)
        sketch(scene, enc_box, 2.5, 0.8)
        sketch(scene, enc_lbl, 2.7, 0.5)
        
        # Arrow to quantization
        a1 = arrow_right(500, 710, 440, BLACK, 4)
        sketch(scene, a1, 3.2, 0.5)
        
        # Quantization
        quant_box = solid_rect(860, 400, 280, 100, ORANGE, PASTEL_ORANGE, 0.30)
        quant_lbl = label("Quantization\n(Codebooks)", 1000, 400, ORANGE, 30, 1)
        sketch(scene, quant_box, 3.5, 0.8)
        sketch(scene, quant_lbl, 3.8, 0.5)
        
        # Arrow to decoder
        a2 = arrow_right(1140, 1400, 440, BLACK, 4)
        sketch(scene, a2, 4.2, 0.5)
        
        # Decoder
        dec_box = solid_rect(1520-100, 400, 200, 100, GREEN, PASTEL_GREEN, 0.30)
        dec_lbl = label("Decoder", 1520, 400, GREEN, 32, 2)
        sketch(scene, dec_box, 4.8, 0.8)
        sketch(scene, dec_lbl, 5.0, 0.5)
        
        # Token example
        token_lbl = label("Audio Tokens = [ 42, 107, 8, 592, ... ]", CX, 560, DARK_GRAY, 44, 2)
        sketch(scene, token_lbl, 5.8, 1.0)
        
        # VALL-E description
        valle_desc = label("VALL-E: Predicting audio tokens like GPT predicts text", CX, 640, BLACK, 38, 2)
        sketch(scene, valle_desc, 6.8, 0.8)
        
        # Science note
        adv_title = label("Science: Leveraging large-scale speech datasets without labels", CX, 720, BLACK, 36, 1)
        sketch(scene, adv_title, 7.6, 0.8)
        
        codec_items = [codec_title, rvq_box, rvq_lbl, enc_box, enc_lbl, quant_box, quant_lbl,
                       dec_box, dec_lbl, a1, a2, token_lbl, valle_desc, adv_title]
        erase(scene, codec_items, 13.5)


# ══════════════════════════════════════════════
# SCENE 10  ─  DISENTANGLED
# ══════════════════════════════════════════════
def scene_disentangled(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "The scientific core of zero-shot is disentanglement. We must isolate the 'what' from the 'who'. "
            "Content, prosody, and timbre are independent factors of variation. "
            "To achieve this, researchers use 'Information Bottlenecks' or 'Latent Sieves'. "
            "By restricting the capacity of the content encoder, we force it to discard speaker-specific info, "
            "while the speaker encoder captures the unique vocal signature in a separate embedding."
        ),
        voice=VOICE, rate=RATE,
    ):
        dis_title = heading("Science of Disentanglement", PURPLE)
        sketch(scene, dis_title, 0.5, 1.0)
        
        # Left: Audio signal
        voice_box = solid_rect(250, 400, 200, 80, CYAN, PASTEL_CYAN, 0.30)
        voice_lbl = label("Audio Signal", 350, 400, CYAN, 32, 2)
        sketch(scene, voice_box, 1.5, 0.8)
        sketch(scene, voice_lbl, 1.7, 0.5)
        
        # Arrow to prism
        a1 = arrow_right(450, 550, 440, BLACK, 4)
        sketch(scene, a1, 2.2, 0.5)
        
        # Prism symbol (using triangle)
        prism = Polygon(
            points=[(700, 360), (600, 520), (800, 520)],
            stroke_style=StrokeStyle(color=BLACK, width=3),
            sketch_style=SKETCH
        )
        sketch(scene, prism, 2.8, 1.2)
        
        # Arrows from prism to factors
        arrs = [
            arrow_right(700, 900, 380, BLACK, 3),
            arrow_right(700, 900, 440, BLACK, 3),
            arrow_right(700, 900, 500, BLACK, 3),
        ]
        for arr in arrs:
            sketch(scene, arr, 4.0, 0.4)
        
        # Three factors
        factors = [
            ("Content (Text)", 1200, 300, BLUE),
            ("Prosody (Style)", 1200, 420, GREEN),
            ("Timbre (Speaker)", 1200, 540, RED)
        ]
        
        t = 4.5
        for name, cx, cy, col in factors:
            box = solid_rect(cx-150, cy-35, 300, 70, col, PASTEL_BLUE, 0.20)
            lbl = label(name, cx, cy, col, 30, 2)
            sketch(scene, box, t, 0.5)
            sketch(scene, lbl, t+0.2, 0.4)
            t += 0.3
        
        # Bottleneck explanation
        bottleneck_lbl = label("Information Bottleneck: Discarding irrelevant data", CX, 700, DARK_GRAY, 38, 2)
        sketch(scene, bottleneck_lbl, 6.0, 1.0)
        
        # Result
        indep_lbl = label("Result: Independent Factors of Variation", CX, 780, BLACK, 38, 2)
        sketch(scene, indep_lbl, 7.0, 0.8)
        
        dis_items = [dis_title, voice_box, voice_lbl, a1, prism] + arrs
        for name, cx, cy, col in factors:
            dis_items.extend([solid_rect(cx-150, cy-35, 300, 70, col, PASTEL_BLUE, 0.20), 
                            label(name, cx, cy, col, 30, 2)])
        dis_items.extend([bottleneck_lbl, indep_lbl])
        
        erase(scene, dis_items, 11.5)


# ══════════════════════════════════════════════
# SCENE 11  ─  NAR SPEED
# ══════════════════════════════════════════════
def scene_nar_speed(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "To achieve real-time speeds, modern systems have moved to Non-Autoregressive, or NAR, architectures. "
            "Traditional models generate audio tokens one-by-one, which is slow and prone to error accumulation. "
            "NAR models like OmniVoice generate the entire sequence in parallel. "
            "By predicting all tokens simultaneously, we reduce latency from seconds to milliseconds, "
            "enabling truly conversational AI that responds as fast as a human."
        ),
        voice=VOICE, rate=RATE,
    ):
        nar_title = heading("The NAR Speed Revolution", RED)
        sketch(scene, nar_title, 0.5, 1.0)
        
        # Left: Sequential (Autoregressive)
        lp = panel(LP_X, PANEL_TOP, LP_W, 400, RED, PASTEL_RED)
        sketch(scene, lp, 1.2, 1.0)
        
        seq_title = label("Sequential (Autoregressive)", LP_CX, 220, RED, 38, 2)
        sketch(scene, seq_title, 1.5, 0.6)
        
        # Sequential steps (staggered arrows)
        seq_steps = []
        for i in range(5):
            step = solid_rect(LP_X+80+i*100, 350, 80, 50, RED, PASTEL_RED, 0.40)
            lbl = label(f"{i+1}", LP_X+120+i*100, 375, RED, 24, 2)
            seq_steps.extend([step, lbl])
        
        t = 2.0
        for item in seq_steps:
            sketch(scene, item, t, 0.3)
            t += 0.2
        
        speed_l = label("Latency: >2.0s", LP_CX, 500, DARK_GRAY, 36, 2)
        sketch(scene, speed_l, t, 0.6)
        
        # Right: Parallel (Non-Autoregressive)
        rp = panel(RP_X, PANEL_TOP, RP_W, 400, GREEN, PASTEL_GREEN)
        sketch(scene, rp, t, 1.0)
        t += 0.5
        
        nar_title_r = label("Parallel (Non-Autoregressive)", RP_CX, 220, GREEN, 38, 2)
        sketch(scene, nar_title_r, t, 0.6)
        t += 0.5
        
        # All at once
        nar_steps = []
        for i in range(5):
            step = solid_rect(RP_X+120+i*120, 350, 100, 50, GREEN, PASTEL_GREEN, 0.40)
            lbl = label(f"{i+1}", RP_X+170+i*120, 375, GREEN, 24, 2)
            nar_steps.extend([step, lbl])
        
        for item in nar_steps:
            sketch(scene, item, t, 0.3)
        
        speed_r = label("Latency: <0.2s", RP_CX, 500, DARK_GRAY, 36, 2)
        sketch(scene, speed_r, t+0.5, 0.6)
        
        # Result
        realtime_lbl = label("Result: Sub-200ms Conversational Response", CX, 700, BLACK, 44, 2)
        sketch(scene, realtime_lbl, t+1.5, 1.0)
        
        nar_items = [nar_title, lp, rp, seq_title, nar_title_r] + seq_steps + [speed_l, speed_r, realtime_lbl]
        erase(scene, nar_items, 11.0)


# ══════════════════════════════════════════════
# SCENE 12  ─  DIFFUSION & FLOW
# ══════════════════════════════════════════════
def scene_diffusion_flow(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "The most advanced reconstruction techniques have evolved from Diffusion to Flow Matching. "
            "Diffusion models gradually remove Gaussian noise, but they often follow curved, stochastic paths "
            "that require many steps. Flow Matching, used in F5-TTS, learns a straight-path trajectory— "
            "an ODE flow that is faster, more stable, and highly efficient. "
            "By mapping noise directly to data in a linear fashion, we achieve unprecedented vocal clarity "
            "with significantly lower computational overhead."
        ),
        voice=VOICE, rate=RATE,
    ):
        diff_title = heading("Diffusion vs. Flow Matching", VIOLET)
        sketch(scene, diff_title, 0.5, 1.0)
        
        # Start point - Noise
        noise_circle = Circle(center=(300, 400), radius=60,
                              fill_style=FillStyle(color=LIGHT_GRAY, opacity=0.5),
                              stroke_style=StrokeStyle(color=BLACK, width=3),
                              sketch_style=SKETCH)
        noise_lbl = label("Noise", 300, 400, BLACK, 28, 2)
        sketch(scene, noise_circle, 1.2, 0.6)
        sketch(scene, noise_lbl, 1.4, 0.4)
        
        # End point - Speech
        data_circle = Circle(center=(1500, 400), radius=60,
                             fill_style=FillStyle(color=PASTEL_CYAN, opacity=0.5),
                             stroke_style=StrokeStyle(color=CYAN, width=3),
                             sketch_style=SKETCH)
        data_lbl = label("Speech", 1500, 400, CYAN, 28, 2)
        sketch(scene, data_circle, 1.6, 0.6)
        sketch(scene, data_lbl, 1.8, 0.4)
        
        # Curved diffusion path (using polygon to simulate curve)
        curved_path = Polygon(
            points=[(360, 400), (600, 280), (900, 520), (1200, 280), (1440, 400)],
            stroke_style=StrokeStyle(color=GRAY, width=3, dash_array=(10, 5)),
            sketch_style=SKETCH
        )
        curved_lbl = label("Diffusion: Curved/Stochastic", 700, 260, DARK_GRAY, 28, 1)
        sketch(scene, curved_path, 2.5, 2.0)
        sketch(scene, curved_lbl, 3.0, 0.6)
        
        # Straight flow matching path
        straight_path = arrow_right(360, 1440, 400, PURPLE, 6)
        straight_lbl = label("Flow Matching: Straight ODE Path", 900, 480, PURPLE, 32, 2)
        sketch(scene, straight_path, 5.0, 1.0)
        sketch(scene, straight_lbl, 5.5, 0.6)
        
        diff_items = [diff_title, noise_circle, noise_lbl, data_circle, data_lbl, 
                      curved_path, curved_lbl, straight_path, straight_lbl]
        erase(scene, diff_items, 10.0)


# ══════════════════════════════════════════════
# SCENE 13  ─  DPO ALIGNMENT
# ══════════════════════════════════════════════
def scene_preference_alignment(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "The newest frontier is Direct Preference Optimization, or DPO. "
            "Just like LLMs are aligned to human values, TTS models are now aligned to human auditory preferences. "
            "By comparing pairs of generated speech and rewarding the one humans find more natural, "
            "we eliminate robotic artifacts and tongue-twister errors. "
            "This 'alignment' step is what makes modern voices sound indistinguishable from reality."
        ),
        voice=VOICE, rate=RATE,
    ):
        dpo_title = heading("Direct Preference Optimization (DPO)", BLUE)
        sketch(scene, dpo_title, 0.5, 1.0)
        
        # Left: Sample A (Robotic)
        box_a = solid_rect(LP_X+100, 350, 320, 120, RED, PASTEL_RED, 0.20)
        lbl_a = label("Sample A (Robotic)", LP_X+260, 320, RED, 30, 2)
        cross = Text("✗", position=(LP_X+260, 250), font_size=80,
                    stroke_style=StrokeStyle(color=RED, width=5), font_name=FONT)
        sketch(scene, box_a, 1.5, 0.8)
        sketch(scene, lbl_a, 1.7, 0.5)
        sketch(scene, cross, 1.8, 0.6)
        
        # Right: Sample B (Natural)
        box_b = solid_rect(RP_X+100, 350, 320, 120, GREEN, PASTEL_GREEN, 0.25)
        lbl_b = label("Sample B (Natural)", RP_X+260, 320, GREEN, 30, 2)
        check = Text("✓", position=(RP_X+260, 250), font_size=80,
                    stroke_style=StrokeStyle(color=GREEN, width=5), font_name=FONT)
        sketch(scene, box_b, 2.5, 0.8)
        sketch(scene, lbl_b, 2.7, 0.5)
        sketch(scene, check, 2.8, 0.6)
        
        # Comparison vs
        vs_lbl = label("vs", CX, 410, BLACK, 32, 2)
        sketch(scene, vs_lbl, 3.5, 0.4)
        
        # Reward model explanation
        reward_lbl = label("Reward Model: Human-like Prosody > Artifacts", CX, 560, DARK_GRAY, 38, 2)
        sketch(scene, reward_lbl, 4.5, 1.0)
        
        # Result
        align_lbl = label("Result: Indistinguishable Neural Speech", CX, 640, BLACK, 40, 2)
        sketch(scene, align_lbl, 5.5, 0.8)
        
        dpo_items = [dpo_title, box_a, lbl_a, cross, box_b, lbl_b, check, vs_lbl, reward_lbl, align_lbl]
        erase(scene, dpo_items, 9.5)


# ══════════════════════════════════════════════
# SCENE 14  ─  SOTA MODELS
# ══════════════════════════════════════════════
def scene_sota_models(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "In 2026, the state-of-the-art is dominated by OmniVoice and F5-TTS. "
            "OmniVoice uses a Non-Autoregressive architecture to clone voices across 600 languages "
            "with sub-200ms latency. F5-TTS leads in pure naturalness via Flow Matching. "
            "CosyVoice 2 has optimized these models for edge devices, while Fish Speech 1.5 "
            "provides high-performance multilingual synthesis. "
            "The gap between AI and human speech has effectively closed."
        ),
        voice=VOICE, rate=RATE,
    ):
        sota_title = heading("State-of-the-Art (2026)", BLACK)
        sketch(scene, sota_title, 0.5, 1.0)
        
        # Model cards in a 2x3 grid
        models = [
            ("OmniVoice", "600+ Langs, NAR, Ultra-Fast", 480, 250, BLUE),
            ("F5-TTS", "Flow-Matching, SOTA Naturalness", 960, 250, GREEN),
            ("Fish Speech", "High ELO Multilingual", 1440, 250, PURPLE),
            ("CosyVoice 2", "Edge-optimized, 150ms Latency", 480, 450, ORANGE),
            ("AudioSeal", "Integrated Security Watermarking", 960, 450, RED),
        ]
        
        t = 1.5
        model_items = []
        for name, desc, cx, cy, col in models:
            box = solid_rect(cx-180, cy-50, 360, 100, col, PASTEL_BLUE, 0.25)
            name_lbl = label(name, cx, cy-15, col, 36, 2)
            desc_lbl = label(desc, cx, cy+30, DARK_GRAY, 26, 1)
            model_items.extend([box, name_lbl, desc_lbl])
        
        for item in model_items:
            sketch(scene, item, t, 0.5)
            t += 0.15
        
        # Focus note
        field_title = label("Focus: Multilingual Transfer & Real-Time Edge Inference", CX, 650, BLACK, 40, 2)
        sketch(scene, field_title, t+0.5, 0.8)
        
        sota_items = [sota_title, field_title] + model_items
        erase(scene, sota_items, 7.5)


# ══════════════════════════════════════════════
# SCENE 15  ─  ARCHITECTURE PATTERNS
# ══════════════════════════════════════════════
def scene_architecture_patterns(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "The modern zero-shot architecture is built on the Transformer. "
            "It uses Cross-Attention to blend text features with the speaker prompt's style. "
            "A Text Encoder processes phonemes, while a Prompt Encoder extracts timbre. "
            "The Transformer Decoder then generates acoustic tokens or mel-spectrograms. "
            "This modular design allows us to swap encoders or decoders without retraining the entire system."
        ),
        voice=VOICE, rate=RATE,
    ):
        arch_title = heading("Unified Transformer Architecture", TEAL)
        sketch(scene, arch_title, 0.5, 1.0)
        
        # Block diagram - left side
        text_enc = solid_rect(LP_X+150, 300, 200, 80, GREEN, PASTEL_GREEN, 0.30)
        text_lbl = label("Text Encoder", LP_X+250, 300, GREEN, 28, 2)
        
        prompt_enc = solid_rect(LP_X+150, 450, 200, 80, BLUE, PASTEL_BLUE, 0.30)
        prompt_lbl = label("Prompt Encoder", LP_X+250, 450, BLUE, 28, 2)
        
        sketch(scene, text_enc, 1.5, 0.6)
        sketch(scene, text_lbl, 1.7, 0.4)
        sketch(scene, prompt_enc, 2.0, 0.6)
        sketch(scene, prompt_lbl, 2.2, 0.4)
        
        # Arrows to transformer
        a1 = arrow_right(LP_X+350, CX-200, 340, BLACK, 4)
        a2 = arrow_right(LP_X+350, CX-200, 490, BLACK, 4)
        sketch(scene, a1, 2.5, 0.4)
        sketch(scene, a2, 2.6, 0.4)
        
        # Center: Transformer Decoder
        transformer = solid_rect(CX-150, 340, 300, 280, ORANGE, PASTEL_ORANGE, 0.30)
        trans_lbl = label("Transformer\nDecoder", CX, 400, ORANGE, 38, 2)
        sketch(scene, transformer, 3.0, 1.0)
        sketch(scene, trans_lbl, 3.5, 0.6)
        
        # Cross-attention label
        att_box = solid_rect(CX-100, 260, 200, 50, WHITE, PURPLE, 0.40)
        att_lbl = label("Cross-Attention", CX, 260, PURPLE, 24, 1)
        sketch(scene, att_box, 3.8, 0.4)
        sketch(scene, att_lbl, 4.0, 0.3)
        
        # Arrow to output
        a3 = arrow_right(CX+150, RP_X+100, 480, BLACK, 4)
        sketch(scene, a3, 4.5, 0.4)
        
        # Right: Output
        out_box = solid_rect(RP_X+150, 440, 220, 80, RED, PASTEL_RED, 0.30)
        out_lbl = label("Output Audio", RP_X+260, 440, RED, 28, 2)
        sketch(scene, out_box, 5.0, 0.6)
        sketch(scene, out_lbl, 5.2, 0.4)
        
        # Science note
        science_lbl = label("Modular Design: Plug-and-Play Encoders", CX, 750, DARK_GRAY, 38, 2)
        sketch(scene, science_lbl, 6.0, 0.8)
        
        arch_items = [arch_title, text_enc, text_lbl, prompt_enc, prompt_lbl, 
                      a1, a2, transformer, trans_lbl, att_box, att_lbl, a3, out_box, out_lbl, science_lbl]
        erase(scene, arch_items, 11.5)


# ══════════════════════════════════════════════
# SCENE 16  ─  EVALUATION
# ══════════════════════════════════════════════
def scene_evaluation(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Evaluation metrics include objective measures like MCD for Mel-Cepstral Distortion, "
            "PESQ for perceptual quality, and STOI for intelligibility. "
            "Subjective metrics include MOS or Mean Opinion Score on a scale of 1 to 5, "
            "speaker similarity ratings, and EER or Equal Error Rate. "
            "The gold standard is human listening tests."
        ),
        voice=VOICE, rate=RATE,
    ):
        eval_title = heading("Evaluation Metrics", DARK_GRAY)
        sketch(scene, eval_title, 0.5, 1.0)
        
        # Objective metrics - left panel
        lp = panel(LP_X, PANEL_TOP, LP_W, 450, BLACK, LIGHT_GRAY)
        sketch(scene, lp, 1.2, 1.0)
        
        obj_title = label("Objective Metrics:", LP_CX, 220, BLACK, 40, 2)
        sketch(scene, obj_title, 1.5, 0.6)
        
        obj_pts = [
            "MCD: Mel-Cepstral Distortion",
            "PESQ: Perceptual quality",
            "STOI: Intelligibility"
        ]
        t = 2.0
        for i, pt in enumerate(obj_pts):
            lbl = label(f"• {pt}", LP_CX, 300+i*70, DARK_GRAY, 32, 1)
            sketch(scene, lbl, t, 0.4)
            t += 0.4
        
        # Subjective metrics - right panel
        rp = panel(RP_X, PANEL_TOP, RP_W, 450, BLACK, LIGHT_GRAY)
        sketch(scene, rp, t, 1.0)
        t += 0.5
        
        subj_title = label("Subjective Metrics:", RP_CX, 220, BLACK, 40, 2)
        sketch(scene, subj_title, t, 0.6)
        t += 0.5
        
        subj_pts = [
            "MOS: Mean Opinion Score (1-5)",
            "Speaker similarity rating",
            "EER: Equal Error Rate"
        ]
        for i, pt in enumerate(subj_pts):
            lbl = label(f"• {pt}", RP_CX, 300+i*70, DARK_GRAY, 32, 1)
            sketch(scene, lbl, t, 0.4)
            t += 0.4
        
        # Gold standard
        gold_title = label("Gold standard: Human listening tests", CX, 700, ORANGE, 40, 2)
        sketch(scene, gold_title, t+0.5, 0.8)
        
        eval_items = [eval_title, lp, rp, obj_title, subj_title, gold_title]
        for pt in obj_pts:
            eval_items.append(label(f"• {pt}", LP_CX, 300+obj_pts.index(pt)*70, DARK_GRAY, 32, 1))
        for pt in subj_pts:
            eval_items.append(label(f"• {pt}", RP_CX, 300+subj_pts.index(pt)*70, DARK_GRAY, 32, 1))
        
        erase(scene, eval_items, 10.0)


# ══════════════════════════════════════════════
# SCENE 17  ─  CHALLENGES
# ══════════════════════════════════════════════
def scene_challenges(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Challenges and future directions include improving computational efficiency for real-time applications, "
            "enabling cross-lingual voice cloning, achieving fine-grained emotional control, "
            "addressing ethical concerns like deepfakes and watermarking, "
            "and future work on larger models with better disentanglement."
        ),
        voice=VOICE, rate=RATE,
    ):
        chal_title = heading("Challenges & Future Directions", RED)
        sketch(scene, chal_title, 0.5, 1.0)
        
        chal_pts = [
            "Low-latency streaming (<200ms)",
            "Cross-lingual style transfer",
            "AudioSeal: Sample-level watermarking",
            "Biometric security & Deepfake prevention",
            "DPO: Aligning speech to human emotion",
        ]
        
        t = 1.5
        for i, pt in enumerate(chal_pts):
            box = solid_rect(CX-350, 200+i*120, 700, 80, DARK_GRAY, LIGHT_GRAY, 0.20)
            lbl = label(f"• {pt}", CX, 200+i*120, DARK_GRAY, 34, 1)
            sketch(scene, box, t, 0.5)
            sketch(scene, lbl, t+0.2, 0.4)
            t += 0.5
        
        chal_items = [chal_title]
        for i, pt in enumerate(chal_pts):
            chal_items.extend([solid_rect(CX-350, 200+i*120, 700, 80, DARK_GRAY, LIGHT_GRAY, 0.20),
                               label(f"• {pt}", CX, 200+i*120, DARK_GRAY, 34, 1)])
        
        erase(scene, chal_items, 8.5)


# ══════════════════════════════════════════════
# SCENE 18  ─  SUMMARY
# ══════════════════════════════════════════════
def scene_summary(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "To summarize: the evolution has been from traditional methods to few-shot to zero-shot. "
            "Key components include speaker embeddings, neural vocoders, and disentanglement. "
            "Codec-based approaches like VALL-E use language modeling. "
            "Diffusion-based approaches like NaturalSpeech 3 use factorized diffusion. "
            "State-of-the-art models include F5-TTS, XTTS-v2, and Mega-TTS."
        ),
        voice=VOICE, rate=RATE,
    ):
        sum_title = heading("Summary", BLUE)
        sketch(scene, sum_title, 0.5, 1.0)
        
        sum_pts = [
            "Evolution: Traditional → Few-shot → Zero-shot",
            "Key: Speaker embeddings, Neural vocoders, Disentanglement",
            "Codec-based: VALL-E (language modeling)",
            "Diffusion-based: NaturalSpeech 3 (factorized)",
            "SOTA: F5-TTS, XTTS-v2, Mega-TTS",
        ]
        
        t = 1.5
        for i, pt in enumerate(sum_pts):
            box = solid_rect(CX-400, 180+i*110, 800, 80, BLUE, PASTEL_BLUE, 0.20)
            lbl = label(f"• {pt}", CX, 180+i*110, DARK_GRAY, 36, 1)
            sketch(scene, box, t, 0.5)
            sketch(scene, lbl, t+0.2, 0.4)
            t += 0.5
        
        sum_items = [sum_title]
        for i, pt in enumerate(sum_pts):
            sum_items.extend([solid_rect(CX-400, 180+i*110, 800, 80, BLUE, PASTEL_BLUE, 0.20),
                              label(f"• {pt}", CX, 180+i*110, DARK_GRAY, 36, 1)])
        
        erase(scene, sum_items, 8.5)


# ══════════════════════════════════════════════
# SCENE 19  ─  OUTRO
# ══════════════════════════════════════════════
def scene_outro(scene: Scene, tts: EdgeTTSProvider):
    with scene.group(
        tts_provider=tts,
        speech=(
            "Thanks for watching! If you enjoyed this technical deep dive, please like and subscribe for more. "
            "Let me know in the comments what topic you'd like me to cover next."
        ),
        voice=VOICE, rate=RATE,
    ):
        outro_title = Text("Thanks for Watching!", position=(CX, 350), font_size=72,
                           stroke_style=StrokeStyle(color=BLUE, width=4), font_name=FONT)
        like_lbl = label("Like & Subscribe for more technical deep dives", CX, 500, BLACK, 44, 2)
        comment_lbl = label("Comment: What topic should I cover next?", CX, 600, ORANGE, 40, 2)
        
        sketch(scene, outro_title, 0.5, 1.5)
        sketch(scene, like_lbl, 2.0, 1.0)
        sketch(scene, comment_lbl, 3.5, 1.0)


# ══════════════════════════════════════════════
# MAIN RENDERING
# ══════════════════════════════════════════════

def main():
    print("=" * 68)
    print("  Voice Cloning Technical Deep Dive  |  Target: ~15 minutes")
    print("  (Restyled to match deepseek_v4_architecture.py style)")
    print("=" * 68)

    scene = Scene(width=W, height=H, fps=FPS, background_color=BG)
    tts   = EdgeTTSProvider()

    builders = [
        ("Cold Open",                   scene_cold_open),
        ("Title & Hook",                scene_title),
        ("Introduction",                scene_intro),
        ("Speaker Embeddings",          scene_speaker_embeddings),
        ("Neural Vocoders",             scene_neural_vocoders),
        ("Traditional TTS",              scene_traditional_tts),
        ("Few-Shot Cloning",            scene_few_shot),
        ("Zero-Shot Cloning",           scene_zero_shot),
        ("Neural Codecs",               scene_codec_based),
        ("Science of Disentanglement",  scene_disentangled),
        ("The NAR Speed Revolution",    scene_nar_speed),
        ("Diffusion & Flow Matching",   scene_diffusion_flow),
        ("Preference Alignment (DPO)",  scene_preference_alignment),
        ("SOTA Models (2026)",          scene_sota_models),
        ("Architecture Patterns",       scene_architecture_patterns),
        ("Evaluation Metrics",          scene_evaluation),
        ("Challenges & Future Work",    scene_challenges),
        ("Summary",                     scene_summary),
        ("Outro",                       scene_outro),
    ]

    for i, (name, fn) in enumerate(builders, 1):
        print(f"  [{i:02d}/{len(builders)}] Building: {name} ...")
        fn(scene, tts)

    total = scene.get_total_duration()
    print(f"\n  Total Duration : {total:.1f}s  ({total/60:.1f} min)")
    print("  Target         : ~900s  (15 min)")

    out_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "voice_cloning_15min.mp4")

    print(f"\n  Rendering to: {out_path}")
    scene.render(out_path)
    print("  Done! ✓")


if __name__ == "__main__":
    main()