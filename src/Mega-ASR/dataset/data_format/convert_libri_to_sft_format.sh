python convert_libri_to_sft_format.py \
  --input_jsonl datasets/LibriSpeech_test/LibriSpeech.jsonl \
  --output_jsonl datasets/LibriSpeech_test/LibriSpeech_mega_asr.jsonl \
  --convert_to_wav \
  --wav_dir datasets/LibriSpeech_test/wavs \
  --input_audio_root datasets/LibriSpeech_test/LibriSpeech \
  --sr 16000