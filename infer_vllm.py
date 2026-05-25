import sys
sys.path.append("src")

import argparse
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_AUDIO = ROOT_DIR / "assets/example/F01_22GC010K_STR.wav"
DEFAULT_CKPT_DIR = ROOT_DIR / "ckpt/Mega-ASR"
DEFAULT_MATERIALIZED_LORA_NAME = "mega-asr-vllm-materialized"
DEFAULT_VLLM_SMALL_GPU_KWARGS = {
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
    "max_num_seqs": 1,
    "max_num_batched_tokens": 2048,
}


def str2bool(value):
    if isinstance(value, bool):
        return value
    return value.lower() in ("1", "true", "yes", "y")


def resolve_path(path):
    path = Path(path)
    return path if path.is_absolute() else ROOT_DIR / path


def materialized_lora_dir(ckpt_dir):
    return Path(ckpt_dir) / DEFAULT_MATERIALIZED_LORA_NAME


def parse_args():
    parser = argparse.ArgumentParser(description="Mega-ASR vLLM inference")
    parser.add_argument("--audio", default=DEFAULT_AUDIO, help="audio file path")
    parser.add_argument("--ckpt_dir", default=DEFAULT_CKPT_DIR, help="Mega-ASR ckpt root")
    parser.add_argument("--gpu", default=None, help="CUDA_VISIBLE_DEVICES, e.g. 0 or 0,1")
    parser.add_argument(
        "--vllm_materialize_lora_force",
        type=str2bool,
        default=False,
        help="rebuild the materialized LoRA checkpoint even if the cache is fresh",
    )
    parser.add_argument(
        "--vllm_materialize_lora_device_map",
        default=None,
        help="device_map used only while materializing LoRA, e.g. cpu or cuda:0",
    )
    parser.add_argument(
        "--gpu_memory_utilization",
        type=float,
        default=None,
        help="vLLM gpu_memory_utilization",
    )
    parser.add_argument(
        "--max_model_len",
        type=int,
        default=None,
        help="vLLM max_model_len. Lower this on small GPUs, e.g. 8192.",
    )
    parser.add_argument(
        "--max_num_seqs",
        type=int,
        default=None,
        help="vLLM max_num_seqs. Use 1 on small GPUs.",
    )
    parser.add_argument(
        "--max_num_batched_tokens",
        type=int,
        default=None,
        help="vLLM max_num_batched_tokens. Lower this on small GPUs.",
    )
    return parser.parse_args()


def build_vllm_kwargs(args):
    kwargs = {}
    for name, default in DEFAULT_VLLM_SMALL_GPU_KWARGS.items():
        value = getattr(args, name)
        kwargs[name] = default if value is None else value
    return kwargs


def main():
    args = parse_args()
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    from MegaASR.model.megaASR import MegaASR

    audio = resolve_path(args.audio)
    ckpt_dir = resolve_path(args.ckpt_dir)
    vllm_kwargs = build_vllm_kwargs(args)

    model = MegaASR(
        model_path=ckpt_dir / "Qwen3-ASR-1.7B",
        lora_dir=ckpt_dir / "mega-asr-merged",
        routing_enabled=False,
        backend="vllm",
        vllm_apply_lora_on_load=True,
        vllm_materialized_lora_dir=materialized_lora_dir(ckpt_dir),
        vllm_materialize_lora_force=args.vllm_materialize_lora_force,
        vllm_materialize_lora_device_map=args.vllm_materialize_lora_device_map,
        **vllm_kwargs,
    )
    result = model.infer(audio, return_route=True)
    print(result)


if __name__ == "__main__":
    main()
