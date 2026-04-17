# ruff: noqa: E402, PLR0915
"""
Whiteboard explainer: GGUF Complete Guide

This scene is designed for a whiteboard animation style with edge-tts narration,
handwritten fonts, and progressive sketch animations.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import edge_tts
except ImportError as exc:
    msg = "Install edge-tts first (for example: pip install edge-tts or uv add --dev edge-tts)."
    raise SystemExit(msg) from exc

from handanim import Eraser, FillStyle, Rectangle, Scene, SketchStyle, StrokeStyle, Text
from handanim.animations import SketchAnimation
from handanim.primitives import Arrow, Circle, Line
from handanim.stylings.color import BLACK, BLUE, GREEN, ORANGE, PURPLE, RED, WHITE


WIDTH = 1920
HEIGHT = 1080
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
AUDIO_PATH = OUTPUT_DIR / "gguf_explained_narration.mp3"
VIDEO_PATH = OUTPUT_DIR / "gguf_explained_whiteboard.mp4"
VOICE = "en-US-GuyNeural"
VOICE_RATE = "+4%"
VOICE_VOLUME = 1.25
FONT_NAME = "cabin_sketch"

BG = WHITE
SKETCH = SketchStyle(roughness=1.0, bowing=0.8, disable_font_mixture=True)

NARRATION = (
    "<bookmark mark='title'/> GGUF Explained: The Complete Guide to GPT-Generated Unified Format. "
    "<bookmark mark='intro'/> This comprehensive guide covers everything you need to know about GGUF, "
    "from its history and technical structure to quantization methods, conversion processes, and practical usage. "
    "Whether you're a developer, researcher, or enthusiast, understanding GGUF is essential for running AI models locally. "
    
    "<bookmark mark='what_is'/> What is GGUF? GGUF stands for GPT-Generated Unified Format. "
    "It is a binary file format specifically designed for storing and running large language models efficiently on consumer hardware. "
    "Created by the llama.cpp project in August 2023, GGUF has become the de facto standard for local AI inference. "
    "The name reflects its purpose: a unified, standardized way to store AI models that were originally in various formats like PyTorch and SafeTensors. "
    "GGUF files contain everything needed to run a model: metadata, tokenizer information, and quantized weights, all in a single file. "
    
    "<bookmark mark='history'/> The history of GGUF begins with GGML, the original format created by Georgi Gerganov for llama.cpp. "
    "GGML worked well but had limitations: it wasn't easily extensible and sometimes lacked clarity in how model data should be interpreted. "
    "In August 2023, GGUF was introduced as a successor to address these issues. "
    "GGUF was designed to be unambiguous, containing all necessary metadata within the file itself, and extensible for future model architectures. "
    "This evolution marked a significant improvement, making GGUF the preferred format for the local AI community. "
    
    "<bookmark mark='technical_structure'/> GGUF uses a sophisticated single-file format that elegantly combines model metadata and tensor data. "
    "The file contains a header with key-value pairs that describe the model architecture, tokenizer information, hyperparameters, and other essential metadata. "
    "Following the metadata, the actual model weights are stored as tensors in a compressed, quantized format. "
    "This single-file approach makes distribution and loading incredibly simple: you just need one file to run a complete model. "
    "The format is designed to be platform-agnostic, working seamlessly on Windows, Mac, and Linux systems. "
    
    "<bookmark mark='quantization_basics'/> Quantization is the key technology that makes GGUF so efficient. "
    "It reduces the precision of model weights from 32-bit or 16-bit floating point numbers to lower precision formats like 4-bit or 8-bit integers. "
    "This process can reduce model size by 50 to 75 percent while maintaining most of the model's performance. "
    "There is a small trade-off in accuracy, but for most applications, the quality difference is negligible compared to the massive memory savings. "
    "Quantization is what enables running large models on consumer hardware that would otherwise require expensive GPUs. "
    
    "<bookmark mark='quantization_types'/> GGUF supports multiple quantization types, each optimized for different use cases. "
    "Q2_K provides extreme compression with 2-bit quantization, suitable for very limited RAM but with significant quality loss. "
    "Q3_K offers 3-bit quantization as a middle ground between size and quality. "
    "Q4_K_M is the most popular choice, using 4-bit quantization with mixed precision for different layers, balancing size and performance. "
    "Q4_K_S is similar but with different mixing strategies. "
    "Q5_K_M provides slightly better quality at the cost of larger file size, using 5-bit quantization. "
    "Q6_K offers even better quality for critical applications where accuracy matters more than memory. "
    "Q8_0 is nearly lossless, using 8-bit quantization that's very close to original 16-bit quality. "
    "The choice depends on your hardware: use lower quantization on limited RAM, higher quantization when you have more memory available. "
    
    "<bookmark mark='k_quantization'/> The K-method quantization used in GGUF is particularly sophisticated. "
    "It analyzes weight distributions per layer and applies different precision based on importance. "
    "This mixed precision approach allocates more bits to critical layers like attention weights and fewer bits to less important layers. "
    "The result is better quality than uniform quantization at the same average bit width. "
    "Advanced users can use importance matrices generated by llama-imatrix to further optimize quantization quality for specific use cases. "
    "This level of sophistication is what sets GGUF apart from simpler quantization approaches. "
    
    "<bookmark mark='memory_requirements'/> GGUF dramatically reduces memory requirements, making local AI accessible. "
    "A 7-billion parameter model that might need 14 gigabytes in fp16 can run in just 4 to 5 gigabytes with Q4_K_M quantization. "
    "This makes CPU inference viable, allowing models to run on laptops without dedicated GPUs. "
    "When a GPU is available, GGUF can also leverage it for even faster inference through layer offloading. "
    "You can run decent models on 8 gigabyte RAM systems, and powerful models on 16 gigabyte systems, which are common configurations. "
    "Memory mapping allows loading only the parts of the model needed for current tokens, further reducing actual RAM usage. "
    
    "<bookmark mark='ecosystem'/> The GGUF ecosystem is rich with tools that support the format. "
    "llama.cpp remains the reference implementation and the most feature-rich option, offering maximum control and customization. "
    "Ollama provides a user-friendly command-line interface and model management system, making it easy for beginners. "
    "LM Studio offers a beautiful graphical interface for Windows, Mac, and Linux users who prefer a visual experience. "
    "GPT4All focuses on ease of use with a simple installer and interface, ideal for non-technical users. "
    "KoboldCpp is optimized for creative writing and role-playing applications, with special features for text generation. "
    "This wide support means you can use GGUF models in whatever workflow suits you best. "
    
    "<bookmark mark='conversion_overview'/> Converting models to GGUF is straightforward thanks to tools provided by the llama.cpp project. "
    "You'll need Python installed, the llama.cpp repository, and a model from Hugging Face that you want to convert. "
    "The conversion process involves downloading the model in its original format, then running a Python script that transforms it into GGUF. "
    "This works for most popular model architectures including LLaMA, Mistral, Qwen, Phi, and many others. "
    "The process is well-documented and supported by active community forums and guides. "
    
    "<bookmark mark='conversion_step1'/> The first step is downloading your model from Hugging Face. "
    "Use the huggingface-cli download command, specifying the model repository and your desired local directory. "
    "For example, to download Mistral 7B, you would run huggingface-cli download mistralai/Mistral-7B-Instruct-v0.3 --local-dir mistral-7b. "
    "This downloads all the necessary files including config.json, tokenizer files, and the model weights in safetensors or PyTorch format. "
    "Make sure you have adequate disk space, as models can be quite large before quantization. "
    
    "<bookmark mark='conversion_step2'/> Once downloaded, navigate to the llama.cpp directory and locate the convert-hf-to-gguf.py script. "
    "Run this script with the path to your downloaded model directory as the argument. "
    "The script will analyze the model architecture, convert the weights to GGUF format, and output a single GGUF file. "
    "You can specify the quantization type using the outfile parameter, like model.Q4_K_M.gguf for 4-bit quantization. "
    "The conversion process may take several minutes depending on your hardware and model size. "
    
    "<bookmark mark='conversion_step3'/> After conversion, you can further quantize the model using the llama-quantize tool. "
    "This tool takes a GGUF input model file, typically in a high-precision format like F32 or BF16, and converts it to a quantized format. "
    "For example, to quantize to Q4_K_M, you would run llama-quantize input-model-f32.gguf output-model-Q4_K_M.gguf Q4_K_M. "
    "Advanced options include using importance matrices for better quality, leaving specific tensors unquantized, and pruning layers. "
    "The output is a single GGUF file that contains everything needed to run the model. "
    
    "<bookmark mark='conversion_step4'/> The final GGUF file will be significantly smaller than the original. "
    "Typically, a 7B model with Q4_K_M quantization will be 4 to 5 gigabytes in size. "
    "You can now use this file with any GGUF-compatible tool like llama.cpp, Ollama, or LM Studio. "
    "The file is completely self-contained and can be shared or moved between different systems without any additional dependencies. "
    "This portability is one of GGUF's key advantages, making model distribution simple and efficient. "
    
    "<bookmark mark='reverse_conversion'/> Converting GGUF back to the Hugging Face transformers format is also possible. "
    "This is useful when you want to fine-tune a GGUF model, analyze it with PyTorch tools, or convert it to another format. "
    "Hugging Face transformers library now has built-in support for loading GGUF files directly. "
    "When you load a GGUF model, it's automatically dequantized back to full precision fp32 format for PyTorch compatibility. "
    "This creates a flexible workflow where you can move between formats as needed for different purposes. "
    
    "<bookmark mark='reverse_step1'/> To load a GGUF model in transformers, use the AutoModelForCausalLM class with the gguf_file parameter. "
    "You would specify the model repository and the specific GGUF filename. "
    "Similarly, load the tokenizer with the same gguf_file parameter to ensure compatibility. "
    "The loaded model is now a regular PyTorch model that you can use for training, fine-tuning, or any other transformers operation. "
    "This integration makes it easy to leverage the PyTorch ecosystem while starting from efficient GGUF files. "
    
    "<bookmark mark='reverse_step2'/> Once loaded in PyTorch format, you can modify the model however you need. "
    "You might fine-tune it on your own dataset using techniques like LoRA or full fine-tuning. "
    "Or you could analyze the model's weights, perform interventions, or experiment with architectural changes. "
    "This gives you the full power of the PyTorch ecosystem while starting from an efficient GGUF base. "
    "After modifications, you can save it back to Hugging Face format or convert it again to GGUF. "
    
    "<bookmark mark='advanced_features'/> GGUF supports several advanced features for power users. "
    "Importance matrices can be generated using llama-imatrix to optimize quantization quality for specific use cases. "
    "Layer pruning allows removing unnecessary layers to reduce model size further. "
    "Tensor-specific quantization lets you apply different quantization types to different parts of the model. "
    "Expert routing configurations can be overridden for models with mixture-of-experts architectures. "
    "These features provide fine-grained control over the quantization process for optimal results. "
    
    "<bookmark mark='performance'/> GGUF models can run surprisingly fast even on CPU, thanks to optimizations in llama.cpp. "
    "The library supports batching for processing multiple requests simultaneously. "
    "Caching mechanisms store intermediate results to avoid redundant computations. "
    "When you have a GPU, you can offload some layers to GPU memory for even faster inference. "
    "Memory mapping allows loading only the parts of the model needed for current tokens, reducing actual RAM usage. "
    "These optimizations collectively enable responsive performance even on modest hardware. "
    
    "<bookmark mark='finding_models'/> Finding GGUF models is easy thanks to Hugging Face's GGUF tag system. "
    "You can browse all models with GGUF files by filtering by the GGUF tag on Hugging Face. "
    "Popular sources include TheBloke, who maintains thousands of quantized models, and bartowski, known for high-quality quantizations. "
    "Official sources like Qwen and Meta also provide GGUF versions of their models. "
    "Look for files ending in .gguf with quantization suffix like Q4_K_M.gguf. "
    "The Hugging Face GGUF viewer lets you inspect metadata and tensor information before downloading. "
    
    "<bookmark mark='practical_usage'/> Practical usage of GGUF models varies by use case. "
    "For general chatbots and assistants, Q4_K_M provides the best balance of quality and size. "
    "For code generation or technical tasks where accuracy is critical, consider Q5_K_M or Q6_K. "
    "For creative writing, Q4_K_M is usually sufficient, and you might even experiment with Q3_K for faster generation. "
    "Always test different quantization levels to find what works best for your specific application and hardware. "
    "The community provides extensive benchmarks and comparisons to help guide your choice. "
    
    "<bookmark mark='future'/> GGUF continues to evolve with support for new model architectures and quantization methods. "
    "The community around GGUF is active, constantly improving tools and adding support for new models. "
    "GGUF has effectively become a standard for local AI, similar to how MP3 became standard for audio. "
    "This standardization makes it easier for developers to build tools and for users to run models. "
    "Future developments may include even more efficient quantization methods and better integration with emerging hardware. "
    "The ecosystem continues to grow, making it an exciting time to explore local AI with GGUF. "
    
    "<bookmark mark='conclusion'/> GGUF represents a crucial innovation in making AI accessible to everyone. "
    "It combines efficient quantization, a unified format, and broad tool support to enable running powerful models on consumer hardware. "
    "Whether you're a developer, researcher, or enthusiast, GGUF gives you the power to experiment with state-of-the-art AI models locally. "
    "The democratization of AI means anyone with a decent computer can now run models like LLaMA, Mistral, and Qwen without needing cloud services. "
    "The ecosystem continues to grow and improve, making GGUF an essential technology for the future of local AI. "
    "<bookmark mark='final'/> Thank you for watching this complete guide to GGUF. "
    "You now have the knowledge to start running AI models locally efficiently."
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
    text: str, *, y: float, color: tuple[float, float, float] = BLACK, align: str = "center"
) -> Text:
    return Text(
        text,
        position=(960, y),
        font_size=55,
        font_name=FONT_NAME,
        stroke_style=StrokeStyle(color=color, width=3.5),
        sketch_style=SKETCH,
        align=align,
        line_spacing=1.3,
    )


def make_bullet_list(
    lines: list[str],
    *,
    y_start: float,
    x: float = 300,
    color: tuple[float, float, float] = BLACK,
    y_step: float = 85,
) -> list[Text]:
    return [
        Text(
            f"• {line}",
            position=(x, y_start + i * y_step),
            font_size=50,
            font_name=FONT_NAME,
            stroke_style=StrokeStyle(color=color, width=3.5),
            sketch_style=SKETCH,
            align="left",
        )
        for i, line in enumerate(lines)
    ]


def make_eraser(objects_to_erase: list, *, start_time: float, duration: float = 1.5) -> None:
    eraser = Eraser(
        objects_to_erase=objects_to_erase,
        drawable_cache=scene.drawable_cache,
        glow_dot_hint={"color": (0.6, 0.6, 0.6), "radius": 10},
    )
    scene.add(SketchAnimation(start_time=start_time, duration=duration), drawable=eraser)


scene = Scene(width=WIDTH, height=HEIGHT, fps=24, background_color=BG)
scene.set_viewport_to_identity()


def build_scene() -> float:
    with scene.voiceover(str(AUDIO_PATH), text=NARRATION, volume=VOICE_VOLUME) as tracker:
        title_start = tracker.bookmark_time("title")
        intro_start = tracker.bookmark_time("intro")
        what_is_start = tracker.bookmark_time("what_is")
        history_start = tracker.bookmark_time("history")
        technical_start = tracker.bookmark_time("technical_structure")
        quant_basics_start = tracker.bookmark_time("quantization_basics")
        quant_types_start = tracker.bookmark_time("quantization_types")
        k_quant_start = tracker.bookmark_time("k_quantization")
        memory_start = tracker.bookmark_time("memory_requirements")
        ecosystem_start = tracker.bookmark_time("ecosystem")
        conv_overview_start = tracker.bookmark_time("conversion_overview")
        conv_step1_start = tracker.bookmark_time("conversion_step1")
        conv_step2_start = tracker.bookmark_time("conversion_step2")
        conv_step3_start = tracker.bookmark_time("conversion_step3")
        conv_step4_start = tracker.bookmark_time("conversion_step4")
        reverse_start = tracker.bookmark_time("reverse_conversion")
        reverse_step1_start = tracker.bookmark_time("reverse_step1")
        reverse_step2_start = tracker.bookmark_time("reverse_step2")
        advanced_start = tracker.bookmark_time("advanced_features")
        performance_start = tracker.bookmark_time("performance")
        finding_start = tracker.bookmark_time("finding_models")
        practical_start = tracker.bookmark_time("practical_usage")
        future_start = tracker.bookmark_time("future")
        conclusion_start = tracker.bookmark_time("conclusion")
        final_start = tracker.bookmark_time("final")

        # --- Section 1: Title ---
        title = make_title("GGUF Explained", y=250, color=BLUE)
        subtitle = make_body("The Complete Guide to GPT-Generated Unified Format", y=400, color=BLACK)

        scene.add(SketchAnimation(start_time=title_start, duration=2.0), drawable=title)
        scene.add(SketchAnimation(start_time=title_start + 1.5, duration=1.8), drawable=subtitle)

        title_drawables = [title, subtitle]

        # --- Section 2: Introduction ---
        make_eraser(title_drawables, start_time=intro_start - 0.3, duration=1.2)

        intro_title = make_title("Comprehensive Guide", y=200, color=BLUE)
        intro_bullets = make_bullet_list(
            [
                "History and technical structure",
                "Quantization methods explained",
                "Conversion processes",
                "Practical usage tips",
            ],
            y_start=320,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=intro_start + 0.5, duration=1.5), drawable=intro_title)
        for i, bullet in enumerate(intro_bullets):
            scene.add(
                SketchAnimation(start_time=intro_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        intro_drawables = [intro_title] + intro_bullets

        # --- Section 3: What is GGUF ---
        make_eraser(intro_drawables, start_time=what_is_start - 0.3, duration=1.2)

        what_title = make_title("What is GGUF?", y=180, color=BLUE)
        what_bullets = make_bullet_list(
            [
                "GPT-Generated Unified Format",
                "Binary format for LLMs on consumer hardware",
                "Created by llama.cpp (August 2023)",
                "Single file: metadata, tokenizer, weights",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=what_is_start + 0.5, duration=1.5), drawable=what_title)
        for i, bullet in enumerate(what_bullets):
            scene.add(
                SketchAnimation(start_time=what_is_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        what_drawables = [what_title] + what_bullets

        # --- Section 4: History ---
        make_eraser(what_drawables, start_time=history_start - 0.3, duration=1.2)

        hist_title = make_title("History: GGML to GGUF", y=180, color=BLUE)
        hist_bullets = make_bullet_list(
            [
                "GGML: original format by Georgi Gerganov",
                "Limitations: not extensible, unclear interpretation",
                "GGUF introduced August 2023",
                "Unambiguous, extensible, preferred format",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=history_start + 0.5, duration=1.5), drawable=hist_title)
        for i, bullet in enumerate(hist_bullets):
            scene.add(
                SketchAnimation(start_time=history_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        hist_drawables = [hist_title] + hist_bullets

        # --- Section 5: Technical Structure ---
        make_eraser(hist_drawables, start_time=technical_start - 0.3, duration=1.2)

        tech_title = make_title("Technical Structure", y=120, color=BLUE)
        
        # GGUF File Structure Diagram
        header_box = Rectangle(
            top_left=(300, 200),
            width=300,
            height=80,
            stroke_style=StrokeStyle(color=ORANGE, width=3.0),
            fill_style=FillStyle(color=ORANGE, opacity=0.15),
            sketch_style=SKETCH,
        )
        header_text = Text("Header (24 bytes)", position=(450, 240), font_size=32, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        metadata_box = Rectangle(
            top_left=(300, 300),
            width=300,
            height=80,
            stroke_style=StrokeStyle(color=GREEN, width=3.0),
            fill_style=FillStyle(color=GREEN, opacity=0.15),
            sketch_style=SKETCH,
        )
        metadata_text = Text("Key-Value Metadata", position=(450, 340), font_size=32, font_name=FONT_NAME,
                            stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        tensor_box = Rectangle(
            top_left=(300, 400),
            width=300,
            height=80,
            stroke_style=StrokeStyle(color=BLUE, width=3.0),
            fill_style=FillStyle(color=BLUE, opacity=0.15),
            sketch_style=SKETCH,
        )
        tensor_text = Text("Tensor Descriptors", position=(450, 440), font_size=32, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        data_box = Rectangle(
            top_left=(300, 500),
            width=300,
            height=80,
            stroke_style=StrokeStyle(color=RED, width=3.0),
            fill_style=FillStyle(color=RED, opacity=0.15),
            sketch_style=SKETCH,
        )
        data_text = Text("Tensor Data Binary", position=(450, 540), font_size=32, font_name=FONT_NAME,
                        stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        # Arrow connecting boxes
        arrow1 = Arrow(start_point=(450, 280), end_point=(450, 300), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)
        arrow2 = Arrow(start_point=(450, 380), end_point=(450, 400), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)
        arrow3 = Arrow(start_point=(450, 480), end_point=(450, 500), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)

        tech_bullets = make_bullet_list(
            [
                "Platform-agnostic: Windows, Mac, Linux",
                "All info in single file",
                "Memory-mapped access",
            ],
            y_start=620,
            x=700,
            color=BLACK,
            y_step=70,
        )

        scene.add(SketchAnimation(start_time=technical_start + 0.5, duration=1.5), drawable=tech_title)
        scene.add(SketchAnimation(start_time=technical_start + 1.5, duration=1.0), drawable=header_box)
        scene.add(SketchAnimation(start_time=technical_start + 1.5, duration=1.0), drawable=header_text)
        scene.add(SketchAnimation(start_time=technical_start + 2.3, duration=1.0), drawable=arrow1)
        scene.add(SketchAnimation(start_time=technical_start + 2.3, duration=1.0), drawable=metadata_box)
        scene.add(SketchAnimation(start_time=technical_start + 2.3, duration=1.0), drawable=metadata_text)
        scene.add(SketchAnimation(start_time=technical_start + 3.1, duration=1.0), drawable=arrow2)
        scene.add(SketchAnimation(start_time=technical_start + 3.1, duration=1.0), drawable=tensor_box)
        scene.add(SketchAnimation(start_time=technical_start + 3.1, duration=1.0), drawable=tensor_text)
        scene.add(SketchAnimation(start_time=technical_start + 3.9, duration=1.0), drawable=arrow3)
        scene.add(SketchAnimation(start_time=technical_start + 3.9, duration=1.0), drawable=data_box)
        scene.add(SketchAnimation(start_time=technical_start + 3.9, duration=1.0), drawable=data_text)
        for i, bullet in enumerate(tech_bullets):
            scene.add(
                SketchAnimation(start_time=technical_start + 4.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        tech_drawables = [tech_title, header_box, header_text, metadata_box, metadata_text, 
                         tensor_box, tensor_text, data_box, data_text, arrow1, arrow2, arrow3] + tech_bullets

        # --- Section 6: Quantization Basics ---
        make_eraser(tech_drawables, start_time=quant_basics_start - 0.3, duration=1.2)

        qbasics_title = make_title("Quantization Basics", y=180, color=BLUE)
        qbasics_bullets = make_bullet_list(
            [
                "Reduces precision: 32/16-bit to 4/8-bit",
                "50-75% size reduction",
                "Minimal quality loss",
                "Enables consumer hardware inference",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=quant_basics_start + 0.5, duration=1.5), drawable=qbasics_title)
        for i, bullet in enumerate(qbasics_bullets):
            scene.add(
                SketchAnimation(start_time=quant_basics_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        qbasics_drawables = [qbasics_title] + qbasics_bullets

        # --- Section 7: Quantization Types ---
        make_eraser(qbasics_drawables, start_time=quant_types_start - 0.3, duration=1.2)

        qtypes_title = make_title("Quantization Types Comparison", y=100, color=BLUE)
        
        # Quantization Comparison Chart
        chart_title = Text("Size vs Quality Trade-off", position=(960, 160), font_size=36, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        # Chart bars
        q2_bar = Rectangle(top_left=(200, 220), width=150, height=40, stroke_style=StrokeStyle(color=RED, width=2.5),
                          fill_style=FillStyle(color=RED, opacity=0.2), sketch_style=SKETCH)
        q2_label = Text("Q2_K", position=(275, 240), font_size=24, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        q2_desc = Text("Smallest", position=(275, 280), font_size=20, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=1.5), sketch_style=SKETCH)
        
        q3_bar = Rectangle(top_left=(400, 220), width=180, height=50, stroke_style=StrokeStyle(color=ORANGE, width=2.5),
                          fill_style=FillStyle(color=ORANGE, opacity=0.2), sketch_style=SKETCH)
        q3_label = Text("Q3_K", position=(490, 245), font_size=24, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        q3_desc = Text("Small", position=(490, 285), font_size=20, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=1.5), sketch_style=SKETCH)
        
        q4_bar = Rectangle(top_left=(620, 220), width=220, height=60, stroke_style=StrokeStyle(color=GREEN, width=2.5),
                          fill_style=FillStyle(color=GREEN, opacity=0.2), sketch_style=SKETCH)
        q4_label = Text("Q4_K_M", position=(730, 250), font_size=24, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        q4_desc = Text("Balanced", position=(730, 295), font_size=20, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=1.5), sketch_style=SKETCH)
        
        q5_bar = Rectangle(top_left=(870, 220), width=260, height=70, stroke_style=StrokeStyle(color=BLUE, width=2.5),
                          fill_style=FillStyle(color=BLUE, opacity=0.2), sketch_style=SKETCH)
        q5_label = Text("Q5_K_M", position=(1000, 255), font_size=24, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        q5_desc = Text("Good Quality", position=(1000, 305), font_size=20, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=1.5), sketch_style=SKETCH)
        
        q6_bar = Rectangle(top_left=(1160, 220), width=300, height=80, stroke_style=StrokeStyle(color=BLUE, width=2.5),
                          fill_style=FillStyle(color=BLUE, opacity=0.3), sketch_style=SKETCH)
        q6_label = Text("Q6_K", position=(1310, 260), font_size=24, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        q6_desc = Text("High Quality", position=(1310, 315), font_size=20, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=1.5), sketch_style=SKETCH)
        
        q8_bar = Rectangle(top_left=(1490, 220), width=350, height=90, stroke_style=StrokeStyle(color=RED, width=2.5),
                          fill_style=FillStyle(color=RED, opacity=0.3), sketch_style=SKETCH)
        q8_label = Text("Q8_0", position=(1665, 265), font_size=24, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        q8_desc = Text("Near Lossless", position=(1665, 325), font_size=20, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=1.5), sketch_style=SKETCH)

        qtypes_bullets = make_bullet_list(
            [
                "Q2_K: extreme compression, high loss",
                "Q3_K: middle ground 3-bit",
                "Q4_K_M: popular 4-bit mixed",
                "Q4_K_S: alternative 4-bit",
                "Q5_K_M: better quality",
                "Q6_K: critical applications",
                "Q8_0: nearly lossless 8-bit",
            ],
            y_start=380,
            x=200,
            color=BLACK,
            y_step=65,
        )

        scene.add(SketchAnimation(start_time=quant_types_start + 0.5, duration=1.5), drawable=qtypes_title)
        scene.add(SketchAnimation(start_time=quant_types_start + 1.5, duration=1.0), drawable=chart_title)
        scene.add(SketchAnimation(start_time=quant_types_start + 2.2, duration=0.8), drawable=q2_bar)
        scene.add(SketchAnimation(start_time=quant_types_start + 2.2, duration=0.8), drawable=q2_label)
        scene.add(SketchAnimation(start_time=quant_types_start + 2.2, duration=0.8), drawable=q2_desc)
        scene.add(SketchAnimation(start_time=quant_types_start + 2.8, duration=0.8), drawable=q3_bar)
        scene.add(SketchAnimation(start_time=quant_types_start + 2.8, duration=0.8), drawable=q3_label)
        scene.add(SketchAnimation(start_time=quant_types_start + 2.8, duration=0.8), drawable=q3_desc)
        scene.add(SketchAnimation(start_time=quant_types_start + 3.4, duration=0.8), drawable=q4_bar)
        scene.add(SketchAnimation(start_time=quant_types_start + 3.4, duration=0.8), drawable=q4_label)
        scene.add(SketchAnimation(start_time=quant_types_start + 3.4, duration=0.8), drawable=q4_desc)
        scene.add(SketchAnimation(start_time=quant_types_start + 4.0, duration=0.8), drawable=q5_bar)
        scene.add(SketchAnimation(start_time=quant_types_start + 4.0, duration=0.8), drawable=q5_label)
        scene.add(SketchAnimation(start_time=quant_types_start + 4.0, duration=0.8), drawable=q5_desc)
        scene.add(SketchAnimation(start_time=quant_types_start + 4.6, duration=0.8), drawable=q6_bar)
        scene.add(SketchAnimation(start_time=quant_types_start + 4.6, duration=0.8), drawable=q6_label)
        scene.add(SketchAnimation(start_time=quant_types_start + 4.6, duration=0.8), drawable=q6_desc)
        scene.add(SketchAnimation(start_time=quant_types_start + 5.2, duration=0.8), drawable=q8_bar)
        scene.add(SketchAnimation(start_time=quant_types_start + 5.2, duration=0.8), drawable=q8_label)
        scene.add(SketchAnimation(start_time=quant_types_start + 5.2, duration=0.8), drawable=q8_desc)
        for i, bullet in enumerate(qtypes_bullets):
            scene.add(
                SketchAnimation(start_time=quant_types_start + 6.0 + i * 0.6, duration=0.9),
                drawable=bullet,
            )

        qtypes_drawables = [qtypes_title, chart_title, q2_bar, q2_label, q2_desc, q3_bar, q3_label, q3_desc,
                           q4_bar, q4_label, q4_desc, q5_bar, q5_label, q5_desc, q6_bar, q6_label, q6_desc,
                           q8_bar, q8_label, q8_desc] + qtypes_bullets

        # --- Section 8: K-Method Quantization ---
        make_eraser(qtypes_drawables, start_time=k_quant_start - 0.3, duration=1.2)

        kquant_title = make_title("K-Method Quantization", y=180, color=BLUE)
        kquant_bullets = make_bullet_list(
            [
                "Analyzes weight distributions per layer",
                "Mixed precision based on importance",
                "More bits for critical layers (attention)",
                "Better quality than uniform quantization",
                "Importance matrices for optimization",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=k_quant_start + 0.5, duration=1.5), drawable=kquant_title)
        for i, bullet in enumerate(kquant_bullets):
            scene.add(
                SketchAnimation(start_time=k_quant_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        kquant_drawables = [kquant_title] + kquant_bullets

        # --- Section 9: Memory Requirements ---
        make_eraser(kquant_drawables, start_time=memory_start - 0.3, duration=1.2)

        mem_title = make_title("Memory Requirements Comparison", y=100, color=BLUE)
        
        # Memory Comparison Diagram
        fp16_bar = Rectangle(top_left=(200, 180), width=500, height=60, stroke_style=StrokeStyle(color=RED, width=3.0),
                           fill_style=FillStyle(color=RED, opacity=0.2), sketch_style=SKETCH)
        fp16_label = Text("fp16: 14 GB", position=(450, 210), font_size=32, font_name=FONT_NAME,
                         stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        q4_bar = Rectangle(top_left=(200, 260), width=180, height=60, stroke_style=StrokeStyle(color=GREEN, width=3.0),
                          fill_style=FillStyle(color=GREEN, opacity=0.2), sketch_style=SKETCH)
        q4_label = Text("Q4_K_M: 4-5 GB", position=(290, 290), font_size=32, font_name=FONT_NAME,
                       stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        vs_text = Text("vs", position=(960, 230), font_size=40, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLUE, width=3.0), sketch_style=SKETCH)
        
        savings_box = Rectangle(top_left=(1100, 180), width=400, height=140, stroke_style=StrokeStyle(color=ORANGE, width=3.0),
                               fill_style=FillStyle(color=ORANGE, opacity=0.15), sketch_style=SKETCH)
        savings_text = Text("65-70% Memory", position=(1300, 220), font_size=32, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        savings_sub = Text("Savings!", position=(1300, 270), font_size=28, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)

        mem_bullets = make_bullet_list(
            [
                "CPU inference viable on laptops",
                "GPU offloading for faster inference",
                "8GB RAM: decent models",
                "16GB RAM: powerful models",
                "Memory mapping reduces actual RAM",
            ],
            y_start=380,
            x=200,
            color=BLACK,
            y_step=65,
        )

        scene.add(SketchAnimation(start_time=memory_start + 0.5, duration=1.5), drawable=mem_title)
        scene.add(SketchAnimation(start_time=memory_start + 1.5, duration=1.0), drawable=fp16_bar)
        scene.add(SketchAnimation(start_time=memory_start + 1.5, duration=1.0), drawable=fp16_label)
        scene.add(SketchAnimation(start_time=memory_start + 2.3, duration=1.0), drawable=q4_bar)
        scene.add(SketchAnimation(start_time=memory_start + 2.3, duration=1.0), drawable=q4_label)
        scene.add(SketchAnimation(start_time=memory_start + 3.1, duration=1.0), drawable=vs_text)
        scene.add(SketchAnimation(start_time=memory_start + 3.1, duration=1.0), drawable=savings_box)
        scene.add(SketchAnimation(start_time=memory_start + 3.1, duration=1.0), drawable=savings_text)
        scene.add(SketchAnimation(start_time=memory_start + 3.1, duration=1.0), drawable=savings_sub)
        for i, bullet in enumerate(mem_bullets):
            scene.add(
                SketchAnimation(start_time=memory_start + 4.0 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        mem_drawables = [mem_title, fp16_bar, fp16_label, q4_bar, q4_label, vs_text, savings_box, savings_text, savings_sub] + mem_bullets

        # --- Section 10: Ecosystem ---
        make_eraser(mem_drawables, start_time=ecosystem_start - 0.3, duration=1.2)

        eco_title = make_title("GGUF Ecosystem Tools", y=80, color=BLUE)
        
        # Ecosystem Diagram
        center_circle = Circle(center=(960, 250), radius=80, stroke_style=StrokeStyle(color=BLUE, width=3.0),
                             fill_style=FillStyle(color=BLUE, opacity=0.2), sketch_style=SKETCH)
        center_text = Text("GGUF", position=(960, 250), font_size=36, font_name=FONT_NAME,
                         stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        # Tool circles around center
        llamacpp_circle = Circle(center=(960, 100), radius=60, stroke_style=StrokeStyle(color=GREEN, width=2.5),
                                fill_style=FillStyle(color=GREEN, opacity=0.15), sketch_style=SKETCH)
        llamacpp_text = Text("llama.cpp", position=(960, 100), font_size=22, font_name=FONT_NAME,
                           stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        
        ollama_circle = Circle(center=(1200, 180), radius=60, stroke_style=StrokeStyle(color=ORANGE, width=2.5),
                              fill_style=FillStyle(color=ORANGE, opacity=0.15), sketch_style=SKETCH)
        ollama_text = Text("Ollama", position=(1200, 180), font_size=22, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        
        lmstudio_circle = Circle(center=(1200, 320), radius=60, stroke_style=StrokeStyle(color=PURPLE, width=2.5),
                                 fill_style=FillStyle(color=PURPLE, opacity=0.15), sketch_style=SKETCH)
        lmstudio_text = Text("LM Studio", position=(1200, 320), font_size=22, font_name=FONT_NAME,
                            stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        
        gpt4all_circle = Circle(center=(720, 320), radius=60, stroke_style=StrokeStyle(color=RED, width=2.5),
                               fill_style=FillStyle(color=RED, opacity=0.15), sketch_style=SKETCH)
        gpt4all_text = Text("GPT4All", position=(720, 320), font_size=22, font_name=FONT_NAME,
                           stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)
        
        kobold_circle = Circle(center=(720, 180), radius=60, stroke_style=StrokeStyle(color=BLUE, width=2.5),
                              fill_style=FillStyle(color=BLUE, opacity=0.15), sketch_style=SKETCH)
        kobold_text = Text("KoboldCpp", position=(720, 180), font_size=22, font_name=FONT_NAME,
                          stroke_style=StrokeStyle(color=BLACK, width=2.0), sketch_style=SKETCH)

        eco_bullets = make_bullet_list(
            [
                "llama.cpp: reference implementation",
                "Ollama: user-friendly CLI",
                "LM Studio: beautiful GUI",
                "GPT4All: simple installer",
                "KoboldCpp: creative writing",
            ],
            y_start=380,
            x=200,
            color=BLACK,
            y_step=60,
        )

        scene.add(SketchAnimation(start_time=ecosystem_start + 0.5, duration=1.5), drawable=eco_title)
        scene.add(SketchAnimation(start_time=ecosystem_start + 1.5, duration=1.0), drawable=center_circle)
        scene.add(SketchAnimation(start_time=ecosystem_start + 1.5, duration=1.0), drawable=center_text)
        scene.add(SketchAnimation(start_time=ecosystem_start + 2.3, duration=0.8), drawable=llamacpp_circle)
        scene.add(SketchAnimation(start_time=ecosystem_start + 2.3, duration=0.8), drawable=llamacpp_text)
        scene.add(SketchAnimation(start_time=ecosystem_start + 2.8, duration=0.8), drawable=ollama_circle)
        scene.add(SketchAnimation(start_time=ecosystem_start + 2.8, duration=0.8), drawable=ollama_text)
        scene.add(SketchAnimation(start_time=ecosystem_start + 3.3, duration=0.8), drawable=lmstudio_circle)
        scene.add(SketchAnimation(start_time=ecosystem_start + 3.3, duration=0.8), drawable=lmstudio_text)
        scene.add(SketchAnimation(start_time=ecosystem_start + 3.8, duration=0.8), drawable=gpt4all_circle)
        scene.add(SketchAnimation(start_time=ecosystem_start + 3.8, duration=0.8), drawable=gpt4all_text)
        scene.add(SketchAnimation(start_time=ecosystem_start + 4.3, duration=0.8), drawable=kobold_circle)
        scene.add(SketchAnimation(start_time=ecosystem_start + 4.3, duration=0.8), drawable=kobold_text)
        for i, bullet in enumerate(eco_bullets):
            scene.add(
                SketchAnimation(start_time=ecosystem_start + 5.0 + i * 0.7, duration=1.0),
                drawable=bullet,
            )

        eco_drawables = [eco_title, center_circle, center_text, llamacpp_circle, llamacpp_text, ollama_circle, ollama_text,
                        lmstudio_circle, lmstudio_text, gpt4all_circle, gpt4all_text, kobold_circle, kobold_text] + eco_bullets

        # --- Section 11: Conversion Overview ---
        make_eraser(eco_drawables, start_time=conv_overview_start - 0.3, duration=1.2)

        conv_title = make_title("Conversion Process Flowchart", y=100, color=BLUE)
        
        # Conversion Flowchart
        hf_box = Rectangle(top_left=(150, 180), width=300, height=70, stroke_style=StrokeStyle(color=BLUE, width=3.0),
                          fill_style=FillStyle(color=BLUE, opacity=0.15), sketch_style=SKETCH)
        hf_text = Text("Hugging Face Model", position=(300, 215), font_size=28, font_name=FONT_NAME,
                      stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        arrow1 = Arrow(start_point=(450, 215), end_point=(530, 215), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)
        
        download_box = Rectangle(top_left=(530, 180), width=300, height=70, stroke_style=StrokeStyle(color=GREEN, width=3.0),
                                fill_style=FillStyle(color=GREEN, opacity=0.15), sketch_style=SKETCH)
        download_text = Text("Download", position=(680, 215), font_size=28, font_name=FONT_NAME,
                           stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        arrow2 = Arrow(start_point=(830, 215), end_point=(910, 215), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)
        
        convert_box = Rectangle(top_left=(910, 180), width=300, height=70, stroke_style=StrokeStyle(color=ORANGE, width=3.0),
                               fill_style=FillStyle(color=ORANGE, opacity=0.15), sketch_style=SKETCH)
        convert_text = Text("convert-hf-to-gguf.py", position=(1060, 215), font_size=26, font_name=FONT_NAME,
                           stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        arrow3 = Arrow(start_point=(1210, 215), end_point=(1290, 215), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)
        
        quantize_box = Rectangle(top_left=(1290, 180), width=300, height=70, stroke_style=StrokeStyle(color=RED, width=3.0),
                                fill_style=FillStyle(color=RED, opacity=0.15), sketch_style=SKETCH)
        quantize_text = Text("llama-quantize", position=(1440, 215), font_size=28, font_name=FONT_NAME,
                            stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)
        
        arrow4 = Arrow(start_point=(1440, 250), end_point=(1440, 290), stroke_style=StrokeStyle(color=BLACK, width=2.5),
                       sketch_style=SKETCH)
        
        gguf_box = Rectangle(top_left=(1290, 290), width=300, height=70, stroke_style=StrokeStyle(color=BLUE, width=3.0),
                            fill_style=FillStyle(color=BLUE, opacity=0.2), sketch_style=SKETCH)
        gguf_text = Text("GGUF File Ready!", position=(1440, 325), font_size=28, font_name=FONT_NAME,
                         stroke_style=StrokeStyle(color=BLACK, width=2.5), sketch_style=SKETCH)

        conv_bullets = make_bullet_list(
            [
                "Supports: LLaMA, Mistral, Qwen, Phi",
                "Single file output",
                "Self-contained and portable",
                "Works on Windows, Mac, Linux",
            ],
            y_start=420,
            x=200,
            color=BLACK,
            y_step=65,
        )

        scene.add(SketchAnimation(start_time=conv_overview_start + 0.5, duration=1.5), drawable=conv_title)
        scene.add(SketchAnimation(start_time=conv_overview_start + 1.5, duration=1.0), drawable=hf_box)
        scene.add(SketchAnimation(start_time=conv_overview_start + 1.5, duration=1.0), drawable=hf_text)
        scene.add(SketchAnimation(start_time=conv_overview_start + 2.3, duration=0.8), drawable=arrow1)
        scene.add(SketchAnimation(start_time=conv_overview_start + 2.3, duration=1.0), drawable=download_box)
        scene.add(SketchAnimation(start_time=conv_overview_start + 2.3, duration=1.0), drawable=download_text)
        scene.add(SketchAnimation(start_time=conv_overview_start + 3.1, duration=0.8), drawable=arrow2)
        scene.add(SketchAnimation(start_time=conv_overview_start + 3.1, duration=1.0), drawable=convert_box)
        scene.add(SketchAnimation(start_time=conv_overview_start + 3.1, duration=1.0), drawable=convert_text)
        scene.add(SketchAnimation(start_time=conv_overview_start + 3.9, duration=0.8), drawable=arrow3)
        scene.add(SketchAnimation(start_time=conv_overview_start + 3.9, duration=1.0), drawable=quantize_box)
        scene.add(SketchAnimation(start_time=conv_overview_start + 3.9, duration=1.0), drawable=quantize_text)
        scene.add(SketchAnimation(start_time=conv_overview_start + 4.7, duration=0.8), drawable=arrow4)
        scene.add(SketchAnimation(start_time=conv_overview_start + 4.7, duration=1.0), drawable=gguf_box)
        scene.add(SketchAnimation(start_time=conv_overview_start + 4.7, duration=1.0), drawable=gguf_text)
        for i, bullet in enumerate(conv_bullets):
            scene.add(
                SketchAnimation(start_time=conv_overview_start + 5.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        conv_drawables = [conv_title, hf_box, hf_text, download_box, download_text, convert_box, convert_text,
                          quantize_box, quantize_text, gguf_box, gguf_text, arrow1, arrow2, arrow3, arrow4] + conv_bullets

        # --- Section 12: Conversion Step 1 ---
        make_eraser(conv_drawables, start_time=conv_step1_start - 0.3, duration=1.2)

        step1_title = make_title("Step 1: Download", y=180, color=BLUE)
        step1_bullets = make_bullet_list(
            [
                "huggingface-cli download command",
                "Specify repo and local directory",
                "Example: mistralai/Mistral-7B",
                "Downloads config, tokenizer, weights",
                "Ensure adequate disk space",
            ],
            y_start=300,
            color=BLACK,
            y_step=75,
        )

        scene.add(SketchAnimation(start_time=conv_step1_start + 0.5, duration=1.5), drawable=step1_title)
        for i, bullet in enumerate(step1_bullets):
            scene.add(
                SketchAnimation(start_time=conv_step1_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        step1_drawables = [step1_title] + step1_bullets

        # --- Section 13: Conversion Step 2 ---
        make_eraser(step1_drawables, start_time=conv_step2_start - 0.3, duration=1.2)

        step2_title = make_title("Step 2: Convert Script", y=180, color=BLUE)
        step2_bullets = make_bullet_list(
            [
                "Navigate to llama.cpp directory",
                "Run convert-hf-to-gguf.py",
                "Specify model directory path",
                "Output: single GGUF file",
                "May take several minutes",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=conv_step2_start + 0.5, duration=1.5), drawable=step2_title)
        for i, bullet in enumerate(step2_bullets):
            scene.add(
                SketchAnimation(start_time=conv_step2_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        step2_drawables = [step2_title] + step2_bullets

        # --- Section 14: Conversion Step 3 ---
        make_eraser(step2_drawables, start_time=conv_step3_start - 0.3, duration=1.2)

        step3_title = make_title("Step 3: Quantize", y=180, color=BLUE)
        step3_bullets = make_bullet_list(
            [
                "Use llama-quantize tool",
                "Input: F32 or BF16 GGUF",
                "Example: Q4_K_M quantization",
                "Advanced: importance matrices",
                "Pruning, tensor-specific options",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=conv_step3_start + 0.5, duration=1.5), drawable=step3_title)
        for i, bullet in enumerate(step3_bullets):
            scene.add(
                SketchAnimation(start_time=conv_step3_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        step3_drawables = [step3_title] + step3_bullets

        # --- Section 15: Conversion Step 4 ---
        make_eraser(step3_drawables, start_time=conv_step4_start - 0.3, duration=1.2)

        step4_title = make_title("Step 4: Use GGUF", y=180, color=BLUE)
        step4_bullets = make_bullet_list(
            [
                "7B model: 4-5 GB with Q4_K_M",
                "Use with llama.cpp, Ollama, LM Studio",
                "Self-contained, no dependencies",
                "Portable: share between systems",
                "Simple distribution",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=conv_step4_start + 0.5, duration=1.5), drawable=step4_title)
        for i, bullet in enumerate(step4_bullets):
            scene.add(
                SketchAnimation(start_time=conv_step4_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        step4_drawables = [step4_title] + step4_bullets

        # --- Section 16: Reverse Conversion ---
        make_eraser(step4_drawables, start_time=reverse_start - 0.3, duration=1.2)

        rev_title = make_title("GGUF to Transformers", y=180, color=BLUE)
        rev_bullets = make_bullet_list(
            [
                "Useful for fine-tuning, analysis",
                "Hugging Face transformers support",
                "Auto dequantizes to fp32",
                "PyTorch compatibility",
                "Flexible format workflow",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=reverse_start + 0.5, duration=1.5), drawable=rev_title)
        for i, bullet in enumerate(rev_bullets):
            scene.add(
                SketchAnimation(start_time=reverse_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        rev_drawables = [rev_title] + rev_bullets

        # --- Section 17: Reverse Step 1 ---
        make_eraser(rev_drawables, start_time=reverse_step1_start - 0.3, duration=1.2)

        rstep1_title = make_title("Load GGUF in Transformers", y=180, color=BLUE)
        rstep1_bullets = make_bullet_list(
            [
                "AutoModelForCausalLM with gguf_file",
                "Specify repo and GGUF filename",
                "Load tokenizer with gguf_file",
                "Regular PyTorch model result",
                "Full transformers ecosystem access",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=reverse_step1_start + 0.5, duration=1.5), drawable=rstep1_title)
        for i, bullet in enumerate(rstep1_bullets):
            scene.add(
                SketchAnimation(start_time=reverse_step1_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        rstep1_drawables = [rstep1_title] + rstep1_bullets

        # --- Section 18: Reverse Step 2 ---
        make_eraser(rstep1_drawables, start_time=reverse_step2_start - 0.3, duration=1.2)

        rstep2_title = make_title("Modify & Save", y=180, color=BLUE)
        rstep2_bullets = make_bullet_list(
            [
                "Fine-tune with LoRA or full",
                "Analyze weights, interventions",
                "Experiment with architecture",
                "Save with save_pretrained",
                "Convert back to GGUF if needed",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=reverse_step2_start + 0.5, duration=1.5), drawable=rstep2_title)
        for i, bullet in enumerate(rstep2_bullets):
            scene.add(
                SketchAnimation(start_time=reverse_step2_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        rstep2_drawables = [rstep2_title] + rstep2_bullets

        # --- Section 19: Advanced Features ---
        make_eraser(rstep2_drawables, start_time=advanced_start - 0.3, duration=1.2)

        adv_title = make_title("Advanced Features", y=180, color=BLUE)
        adv_bullets = make_bullet_list(
            [
                "Importance matrices (llama-imatrix)",
                "Layer pruning for size reduction",
                "Tensor-specific quantization",
                "Expert routing override",
                "Fine-grained control",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=advanced_start + 0.5, duration=1.5), drawable=adv_title)
        for i, bullet in enumerate(adv_bullets):
            scene.add(
                SketchAnimation(start_time=advanced_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        adv_drawables = [adv_title] + adv_bullets

        # --- Section 20: Performance ---
        make_eraser(adv_drawables, start_time=performance_start - 0.3, duration=1.2)

        perf_title = make_title("Performance", y=180, color=BLUE)
        perf_bullets = make_bullet_list(
            [
                "Fast CPU inference optimizations",
                "Batching for multiple requests",
                "Caching avoids redundant computations",
                "GPU offloading for speed",
                "Memory mapping reduces RAM",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=performance_start + 0.5, duration=1.5), drawable=perf_title)
        for i, bullet in enumerate(perf_bullets):
            scene.add(
                SketchAnimation(start_time=performance_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        perf_drawables = [perf_title] + perf_bullets

        # --- Section 21: Finding Models ---
        make_eraser(perf_drawables, start_time=finding_start - 0.3, duration=1.2)

        find_title = make_title("Finding GGUF Models", y=180, color=BLUE)
        find_bullets = make_bullet_list(
            [
                "Hugging Face GGUF tag filter",
                "TheBloke: thousands of models",
                "bartowski: high-quality quantizations",
                "Official: Qwen, Meta",
                "GGUF viewer for metadata",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=finding_start + 0.5, duration=1.5), drawable=find_title)
        for i, bullet in enumerate(find_bullets):
            scene.add(
                SketchAnimation(start_time=finding_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        find_drawables = [find_title] + find_bullets

        # --- Section 22: Practical Usage ---
        make_eraser(find_drawables, start_time=practical_start - 0.3, duration=1.2)

        prac_title = make_title("Practical Usage", y=180, color=BLUE)
        prac_bullets = make_bullet_list(
            [
                "Chatbots: Q4_K_M best balance",
                "Code: Q5_K_M or Q6_K for accuracy",
                "Creative: Q4_K_M sufficient",
                "Test different quantization levels",
                "Community benchmarks available",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=practical_start + 0.5, duration=1.5), drawable=prac_title)
        for i, bullet in enumerate(prac_bullets):
            scene.add(
                SketchAnimation(start_time=practical_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        prac_drawables = [prac_title] + prac_bullets

        # --- Section 23: Future ---
        make_eraser(prac_drawables, start_time=future_start - 0.3, duration=1.2)

        future_title = make_title("Future of GGUF", y=180, color=BLUE)
        future_bullets = make_bullet_list(
            [
                "New architectures support",
                "Active community improvements",
                "Standard for local AI (like MP3)",
                "Easier tool development",
                "Better hardware integration",
            ],
            y_start=300,
            color=BLACK,
        )

        scene.add(SketchAnimation(start_time=future_start + 0.5, duration=1.5), drawable=future_title)
        for i, bullet in enumerate(future_bullets):
            scene.add(
                SketchAnimation(start_time=future_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )

        future_drawables = [future_title] + future_bullets

        # --- Section 24: Conclusion ---
        make_eraser(future_drawables, start_time=conclusion_start - 0.3, duration=1.2)

        conc_title = make_title("GGUF Democratizes AI", y=180, color=BLUE)
        conc_bullets = make_bullet_list(
            [
                "Efficient quantization",
                "Unified single-file format",
                "Broad tool support",
                "Consumer hardware capability",
                "No cloud services needed",
            ],
            y_start=300,
            color=BLACK,
        )
        conc_note = make_body("Essential for future of local AI", y=580, color=ORANGE)

        scene.add(SketchAnimation(start_time=conclusion_start + 0.5, duration=1.5), drawable=conc_title)
        for i, bullet in enumerate(conc_bullets):
            scene.add(
                SketchAnimation(start_time=conclusion_start + 1.5 + i * 0.8, duration=1.0),
                drawable=bullet,
            )
        scene.add(SketchAnimation(start_time=conclusion_start + 5.0, duration=1.2), drawable=conc_note)

        conc_drawables = [conc_title] + conc_bullets + [conc_note]

        # --- Section 25: Final ---
        make_eraser(conc_drawables, start_time=final_start - 0.3, duration=1.2)

        final_title = make_title("Thank You!", y=350, color=BLUE)
        final_body = make_body("You now have the knowledge to run AI models locally efficiently", y=500, color=BLACK)

        scene.add(SketchAnimation(start_time=final_start + 0.5, duration=1.5), drawable=final_title)
        scene.add(SketchAnimation(start_time=final_start + 1.8, duration=1.5), drawable=final_body)

        return tracker.end_time + 0.8


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize_narration(AUDIO_PATH))
    final_duration = build_scene()
    print("Rendering whiteboard animation...")
    scene.render(str(VIDEO_PATH), max_length=final_duration)
    print(f"Video rendered successfully! Duration: {final_duration:.1f} seconds")


if __name__ == "__main__":
    main()
