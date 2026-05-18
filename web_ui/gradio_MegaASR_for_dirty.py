#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import traceback
from typing import Optional

import gradio as gr

# 如果你直接在 src_MegaASR/inference/ 下运行这个文件，
# 可以直接从同目录导入你已经跑通的推理代码
from inference_merge_v2 import Qwen3ASRMerged, format_output


MODEL = None
CURRENT_CONFIG = None


def get_model(
    model_path: str,
    device_map: str,
    max_inference_batch_size: int,
    max_new_tokens: int,
    verbose: bool = False,
):
    """
    全局缓存模型，避免每次点击按钮都重新加载。
    如果 model_path / device_map / batch_size / max_new_tokens 变了，才重新加载。
    """
    global MODEL, CURRENT_CONFIG

    config = {
        "model_path": model_path,
        "device_map": device_map,
        "max_inference_batch_size": max_inference_batch_size,
        "max_new_tokens": max_new_tokens,
        "verbose": verbose,
    }

    if MODEL is None or CURRENT_CONFIG != config:
        MODEL = Qwen3ASRMerged(
            model_path=model_path,
            device_map=device_map,
            max_inference_batch_size=max_inference_batch_size,
            max_new_tokens=max_new_tokens,
            verbose=verbose,
        )
        CURRENT_CONFIG = config

    return MODEL


def transcribe_audio(
    audio_path: Optional[str],
    model_path: str,
    device_map: str,
    max_inference_batch_size: int,
    max_new_tokens: int,
    output_format: str,
    verbose: bool,
):
    """
    Gradio 按钮回调函数。
    """
    if audio_path is None:
        return "Please upload an audio file first.", "", ""

    if not os.path.exists(audio_path):
        return f"Audio file not found: {audio_path}", "", ""

    try:
        model = get_model(
            model_path=model_path,
            device_map=device_map,
            max_inference_batch_size=max_inference_batch_size,
            max_new_tokens=max_new_tokens,
            verbose=verbose,
        )

        result = model.infer_one(audio_path)
        formatted = format_output(result, output_format)

        # 同时给 UI 拆出 language 和 pure text，方便网页展示
        items = result.get("items", [])
        languages = "\n".join([item.get("language", "") for item in items])
        texts = "\n".join([item.get("text", "") for item in items])

        return formatted, languages, texts

    except Exception as e:
        err = traceback.format_exc()
        return f"[ERROR]\n{str(e)}\n\n{err}", "", ""


def build_demo(
    default_model_path: str,
    default_device_map: str,
    default_max_inference_batch_size: int,
    default_max_new_tokens: int,
):
    with gr.Blocks(title="Mega-ASR For Dirty Demo") as demo:
        gr.Markdown(
            """
# Mega-ASR Demo

Upload an audio file and run Mega-ASR transcription.

The output includes language detection and ASR text.
"""
        )

        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(
                    label="Input Audio",
                    type="filepath",
                    sources=["upload", "microphone"],
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

                language_output = gr.Textbox(
                    label="Detected Language",
                    lines=2,
                    show_copy_button=True,
                )

                text_output = gr.Textbox(
                    label="ASR Text",
                    lines=6,
                    show_copy_button=True,
                )

        with gr.Accordion("Advanced Settings", open=False):
            model_path = gr.Textbox(
                label="Model Path",
                value=default_model_path,
            )

            device_map = gr.Textbox(
                label="Device Map",
                value=default_device_map,
            )

            max_inference_batch_size = gr.Number(
                label="Max Inference Batch Size",
                value=default_max_inference_batch_size,
                precision=0,
            )

            max_new_tokens = gr.Number(
                label="Max New Tokens",
                value=default_max_new_tokens,
                precision=0,
            )

            verbose = gr.Checkbox(
                label="Verbose Logs",
                value=False,
            )

        run_btn.click(
            fn=transcribe_audio,
            inputs=[
                audio_input,
                model_path,
                device_map,
                max_inference_batch_size,
                max_new_tokens,
                output_format,
                verbose,
            ],
            outputs=[
                formatted_output,
                language_output,
                text_output,
            ],
        )

    return demo


def main():
    parser = argparse.ArgumentParser(description="Mega-ASR Gradio UI")

    parser.add_argument(
        "--model_path",
        type=str,
        default="/data/haobin/Qwen3-ASR/Qwen3-ASR-1.7B-lora-merged_v2",
        help="Path to the merged Mega-ASR / Qwen3-ASR model.",
    )
    parser.add_argument("--device_map", type=str, default="cuda:0")
    parser.add_argument("--max_inference_batch_size", type=int, default=32)
    parser.add_argument("--max_new_tokens", type=int, default=256)

    parser.add_argument("--server_name", type=str, default="0.0.0.0")
    parser.add_argument("--server_port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")

    args = parser.parse_args()

    demo = build_demo(
        default_model_path=args.model_path,
        default_device_map=args.device_map,
        default_max_inference_batch_size=args.max_inference_batch_size,
        default_max_new_tokens=args.max_new_tokens,
    )

    demo.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        share=args.share,
    )


if __name__ == "__main__":
    main()