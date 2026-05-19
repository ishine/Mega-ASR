#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mega-ASR Router Gradio UI.

This UI wraps Qwen3ASRRouter:
- Base Qwen3-ASR model
- Three LoRA delta switch
- Audio quality router
- Optional force_base / force_lora mode
"""

import argparse
import os
import traceback
from typing import Optional

import gradio as gr

from inference_router import Qwen3ASRRouter, format_output


ROUTER = None
CURRENT_CONFIG = None


def get_router(
    model_path: str,
    lora_b_dir: str,
    lora_c_dir: str,
    lora_d_dir: str,
    quality_model_dir: str,
    quality_checkpoint: str,
    quality_threshold: float,
    routing_enabled: bool,
    device_map: str,
    quality_device: str,
    max_inference_batch_size: int,
    max_new_tokens: int,
    verbose: bool,
):
    """
    Cache the router globally.
    The model will be reloaded only when configuration changes.
    """
    global ROUTER, CURRENT_CONFIG

    config = {
        "model_path": model_path,
        "lora_b_dir": lora_b_dir,
        "lora_c_dir": lora_c_dir,
        "lora_d_dir": lora_d_dir,
        "quality_model_dir": quality_model_dir,
        "quality_checkpoint": quality_checkpoint,
        "quality_threshold": float(quality_threshold),
        "routing_enabled": bool(routing_enabled),
        "device_map": device_map,
        "quality_device": quality_device,
        "max_inference_batch_size": int(max_inference_batch_size),
        "max_new_tokens": int(max_new_tokens),
        "verbose": bool(verbose),
    }

    if ROUTER is None or CURRENT_CONFIG != config:
        ROUTER = Qwen3ASRRouter(
            model_path=model_path,
            lora_b_dir=lora_b_dir,
            lora_c_dir=lora_c_dir,
            lora_d_dir=lora_d_dir,
            quality_model_dir=quality_model_dir,
            quality_checkpoint=quality_checkpoint,
            quality_threshold=float(quality_threshold),
            routing_enabled=bool(routing_enabled),
            device_map=device_map,
            quality_device=quality_device,
            max_inference_batch_size=int(max_inference_batch_size),
            max_new_tokens=int(max_new_tokens),
            verbose=bool(verbose),
        )
        CURRENT_CONFIG = config

    return ROUTER


def transcribe_router(
    audio_path: Optional[str],
    route_mode: str,
    output_format: str,
    model_path: str,
    lora_b_dir: str,
    lora_c_dir: str,
    lora_d_dir: str,
    quality_model_dir: str,
    quality_checkpoint: str,
    quality_threshold: float,
    disable_quality_routing: bool,
    device_map: str,
    quality_device: str,
    max_inference_batch_size: int,
    max_new_tokens: int,
    verbose: bool,
):
    if audio_path is None:
        return (
            "Please upload or record an audio file first.",
            "",
            "",
            "",
            "",
            "",
            "",
        )

    if not os.path.exists(audio_path):
        return (
            f"Audio file not found: {audio_path}",
            "",
            "",
            "",
            "",
            "",
            "",
        )

    try:
        routing_enabled = not bool(disable_quality_routing)

        router = get_router(
            model_path=model_path,
            lora_b_dir=lora_b_dir,
            lora_c_dir=lora_c_dir,
            lora_d_dir=lora_d_dir,
            quality_model_dir=quality_model_dir,
            quality_checkpoint=quality_checkpoint,
            quality_threshold=float(quality_threshold),
            routing_enabled=routing_enabled,
            device_map=device_map,
            quality_device=quality_device,
            max_inference_batch_size=int(max_inference_batch_size),
            max_new_tokens=int(max_new_tokens),
            verbose=bool(verbose),
        )

        force_base = route_mode == "Force Base"
        force_lora = route_mode == "Force LoRA"

        result = router.infer_one(
            audio=audio_path,
            force_base=force_base,
            force_lora=force_lora,
        )

        formatted = format_output(result, output_format)

        items = result.get("items", [])
        language = "\n".join([x.get("language", "") for x in items])
        text = "\n".join([x.get("text", "") for x in items])

        use_lora = result.get("use_lora", None)
        route_source = result.get("route_source", "")
        dirty_prob = result.get("dirty_prob", None)
        elapsed = result.get("elapsed", None)

        if dirty_prob is None:
            dirty_prob_str = "N/A"
        else:
            dirty_prob_str = f"{float(dirty_prob):.6f}"

        elapsed_str = "N/A" if elapsed is None else f"{float(elapsed):.3f} s"
        use_lora_str = "LoRA" if use_lora else "Base"

        return (
            formatted,
            language,
            text,
            use_lora_str,
            route_source,
            dirty_prob_str,
            elapsed_str,
        )

    except Exception as e:
        err = traceback.format_exc()
        return (
            f"[ERROR]\n{str(e)}\n\n{err}",
            "",
            "",
            "",
            "",
            "",
            "",
        )


def build_demo(args):
    with gr.Blocks(title="Mega-ASR For All Demo") as demo:
        gr.Markdown(
            """
# Mega-ASR Router Demo

Upload an audio file and run Mega-ASR with quality-aware routing.

The router can automatically choose **Base** or **LoRA-enhanced** inference according to the audio quality classifier.
"""
        )

        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(
                    label="Input Audio",
                    type="filepath",
                    sources=["upload", "microphone"],
                )

                route_mode = gr.Radio(
                    label="Routing Mode",
                    choices=[
                        "Auto Router",
                        "Force Base",
                        "Force LoRA",
                    ],
                    value="Auto Router",
                )

                output_format = gr.Dropdown(
                    label="Output Format",
                    choices=["tagged", "language_text", "text", "json"],
                    value="tagged",
                )

                run_btn = gr.Button("Transcribe", variant="primary")

            with gr.Column(scale=1):
                formatted_output = gr.Textbox(
                    label="Formatted Output",
                    lines=8,
                    show_copy_button=True,
                )

                text_output = gr.Textbox(
                    label="ASR Text",
                    lines=6,
                    show_copy_button=True,
                )

                language_output = gr.Textbox(
                    label="Detected Language",
                    lines=2,
                    show_copy_button=True,
                )

        with gr.Row():
            use_lora_output = gr.Textbox(
                label="Selected Branch",
                lines=1,
                interactive=False,
            )
            route_source_output = gr.Textbox(
                label="Route Source",
                lines=1,
                interactive=False,
            )
            dirty_prob_output = gr.Textbox(
                label="Dirty Probability",
                lines=1,
                interactive=False,
            )
            elapsed_output = gr.Textbox(
                label="Elapsed Time",
                lines=1,
                interactive=False,
            )

        with gr.Accordion("Advanced Settings", open=False):
            model_path = gr.Textbox(
                label="Base Model Path",
                value=args.model_path,
            )

            with gr.Row():
                lora_b_dir = gr.Textbox(
                    label="LoRA B Dir / SFT1",
                    value=args.lora_b_dir,
                )
                lora_c_dir = gr.Textbox(
                    label="LoRA C Dir / SFT2",
                    value=args.lora_c_dir,
                )
                lora_d_dir = gr.Textbox(
                    label="LoRA D Dir / SFT3",
                    value=args.lora_d_dir,
                )

            quality_model_dir = gr.Textbox(
                label="Quality Classifier Code Dir",
                value=args.quality_model_dir,
            )

            quality_checkpoint = gr.Textbox(
                label="Quality Classifier Checkpoint",
                value=args.quality_checkpoint,
            )

            with gr.Row():
                quality_threshold = gr.Slider(
                    label="Quality Routing Threshold",
                    minimum=0.0,
                    maximum=1.0,
                    value=args.quality_threshold,
                    step=0.01,
                )

                disable_quality_routing = gr.Checkbox(
                    label="Disable Quality Routing",
                    value=args.disable_quality_routing,
                )

            with gr.Row():
                device_map = gr.Textbox(
                    label="Model Device Map",
                    value=args.device_map,
                )

                quality_device = gr.Textbox(
                    label="Quality Classifier Device",
                    value=args.quality_device,
                )

            with gr.Row():
                max_inference_batch_size = gr.Number(
                    label="Max Inference Batch Size",
                    value=args.max_inference_batch_size,
                    precision=0,
                )

                max_new_tokens = gr.Number(
                    label="Max New Tokens",
                    value=args.max_new_tokens,
                    precision=0,
                )

            verbose = gr.Checkbox(
                label="Verbose Logs",
                value=args.verbose,
            )

        run_btn.click(
            fn=transcribe_router,
            inputs=[
                audio_input,
                route_mode,
                output_format,
                model_path,
                lora_b_dir,
                lora_c_dir,
                lora_d_dir,
                quality_model_dir,
                quality_checkpoint,
                quality_threshold,
                disable_quality_routing,
                device_map,
                quality_device,
                max_inference_batch_size,
                max_new_tokens,
                verbose,
            ],
            outputs=[
                formatted_output,
                language_output,
                text_output,
                use_lora_output,
                route_source_output,
                dirty_prob_output,
                elapsed_output,
            ],
        )

    return demo


def main():
    parser = argparse.ArgumentParser(description="Mega-ASR Router Gradio UI")

    parser.add_argument(
        "--model_path",
        type=str,
        default="/data/haobin/Qwen3-ASR/Qwen3-ASR-1.7B",
    )

    parser.add_argument(
        "--lora_b_dir",
        type=str,
        default="/data/haobin/open/lora/lora1",
    )
    parser.add_argument(
        "--lora_c_dir",
        type=str,
        default="/data/haobin/open/lora/lora2",
    )
    parser.add_argument(
        "--lora_d_dir",
        type=str,
        default="/data/haobin/open/lora/lora3",
    )

    parser.add_argument(
        "--quality_model_dir",
        type=str,
        default="/data/haobin/audio_quality_classifier_dataset/audio_quality_classifier",
    )
    parser.add_argument(
        "--quality_checkpoint",
        type=str,
        default="/data/haobin/audio_quality_classifier_dataset/audio_quality_classifier/runs/exp_20260211_1layer/best_acc_model.pt",
    )
    parser.add_argument("--quality_threshold", type=float, default=0.5)
    parser.add_argument("--disable_quality_routing", action="store_true")

    parser.add_argument("--device_map", type=str, default="cuda:0")
    parser.add_argument("--quality_device", type=str, default="cuda")
    parser.add_argument("--max_inference_batch_size", type=int, default=32)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument("--verbose", action="store_true")

    parser.add_argument("--server_name", type=str, default="0.0.0.0")
    parser.add_argument("--server_port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")

    args = parser.parse_args()

    demo = build_demo(args)
    demo.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        share=args.share,
    )


if __name__ == "__main__":
    main()