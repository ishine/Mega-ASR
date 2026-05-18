python web_ui/gradio_MegaASR_for_all.py \
  --model_path Qwen3-ASR/Qwen3-ASR-1.7B \
  --lora_b_dir A2S-SFT-LORA/lora1 \
  --lora_c_dir A2S-SFT-LORA/lora2 \
  --lora_d_dir A2S-SFT-LORA/lora3 \
  
  --device_map cuda:0   \
  --quality_device cuda  \
  --server_name 0.0.0.0   \
  --server_port 7860