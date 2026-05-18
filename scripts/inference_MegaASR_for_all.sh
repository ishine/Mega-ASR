CUDA_VISIBLE_DEVICES=5 python inference_MegaASR_for_all.py \
  --audio example/distortion.wav \
  --model_path Qwen3-ASR/Qwen3-ASR-1.7B \
  --lora_b_dir A2S-SFT-LORA/lora1 \
  --lora_c_dir A2S-SFT-LORA/lora2 \
  --lora_d_dir A2S-SFT-LORA/lora3 \
  --quality_checkpoint best_acc_model.pt \
  --quality_model_dir audio_quality_classifier \
  --quality_threshold 0.5 
