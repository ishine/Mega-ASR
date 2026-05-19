# Qwen3-ASR Inference + WER/CER JSONL Evaluation

This tool loads Qwen3-ASR, runs ASR prediction for each audio sample in a JSONL file, fills the `prediction` field, computes WER/CER, and writes a new JSONL file.

## 1. Input Format

Default input format:

```json
{"index":1755,"audio_path":"examples/noise.wav","question":"Please transcribe the audio content into text.","answer":"I usually take the quieter road home because the main street gets crowded after work.","subset":"sim-en-noise","name":"vitw_01756_random_synthetic_en_noise","prediction":""}
```

Default required fields:

| Field | Meaning |
|---|---|
| `audio_path` | Audio file path. Can be absolute or relative. |
| `answer` | Reference transcription. |
| `prediction` | Can be empty. The script will overwrite/fill it with Qwen3-ASR output. |

The script also supports the Mega-ASR SFT format:

```json
{"audio": "/path/to/audio.wav", "text": "language English<asr_text>reference text", "prompt": ""}
```

Use:

```bash
--data_format v2
```

or keep the default:

```bash
--data_format auto
```

## 2. Output Format

The output keeps all original fields and adds/updates:

| Field | Meaning |
|---|---|
| `prediction` | Qwen3-ASR transcription text |
| `pred_language` | Language returned by Qwen3-ASR |
| `wer` | Error rate. English uses WER; Chinese uses CER. |
| `metric` | `wer` or `cer` |
| `num_edits` | Levenshtein edit distance |
| `ref_len` | Reference length, counted by words for WER and characters for CER |

Example:

```json
{"index":1755,"audio_path":"examples/noise.wav","question":"Please transcribe the audio content into text.","answer":"I usually take the quieter road home because the main street gets crowded after work.","subset":"sim-en-noise","name":"vitw_01756_random_synthetic_en_noise","prediction":"I usually take the quieter road home because the main street gets crowded after work.","pred_language":"English","wer":0.0,"metric":"wer","num_edits":0,"ref_len":15}
```

## 3. WER / CER Definition

### WER for English

```text
WER = (S + D + I) / N
```

where:

- `S`: substitutions
- `D`: deletions
- `I`: insertions
- `N`: number of words in the reference

Processing steps:

1. Remove tags such as `language English<asr_text>`.
2. Normalize English text with `whisper_normalizer` if available.
3. Lowercase text.
4. Remove punctuation.
5. Split into word tokens.
6. Compute Levenshtein edit distance.

### CER for Chinese

```text
CER = (S + D + I) / N
```

where `N` is the number of reference characters.

Processing steps:

1. Remove tags such as `language Chinese<asr_text>`.
2. Normalize Chinese text with `cn_tn.TextNorm` if available.
3. Remove punctuation and spaces.
4. Split into characters.
5. Compute Levenshtein edit distance.

In auto mode, samples containing Chinese characters or Chinese language hints are evaluated with CER; other samples are evaluated with WER.

## 4. Basic Usage

Single GPU:

```bash
python infer_score_qwen3_asr_jsonl.py \
  --input_jsonl input.jsonl \
  --output_jsonl output_with_pred_wer.jsonl \
  --model_path /data/haobin/Qwen3-ASR/Qwen3-ASR-1.7B \
  --gpus 0 \
  --batch_size 8
```

If audio paths are relative, use `--audio_root`.



## 5. Multi-GPU Usage

```bash
python infer_score_qwen3_asr_jsonl.py \
  --input_jsonl input.jsonl \
  --output_jsonl output_with_pred_wer.jsonl \
  --model_path /data/haobin/Qwen3-ASR/Qwen3-ASR-1.7B \
  --audio_root /data/haobin/open/Mega-ASR \
  --gpus 0,1,2,3 \
  --batch_size 8
```

Each process loads one Qwen3-ASR model on one GPU.

## 6. Optional LoRA Adapter

```bash
python infer_score_qwen3_asr_jsonl.py \
  --input_jsonl input.jsonl \
  --output_jsonl output_with_pred_wer.jsonl \
  --model_path Qwen3-ASR/Qwen3-ASR-1.7B \
  --adapter_dir /path/to/lora_adapter \
  --gpus 0 \
  --batch_size 8
```

## 7. Force English WER or Chinese CER

Force English WER:

```bash
--language en
```

Force Chinese CER:

```bash
--language zh
```

Auto mode is the default:

```bash
--language auto
```

## 8. Debug Normalized Text

```bash
python infer_score_qwen3_asr_jsonl.py \
  --input_jsonl input.jsonl \
  --output_jsonl output_with_pred_wer.jsonl \
  --model_path Qwen3-ASR/Qwen3-ASR-1.7B \
  --keep_norm_text
```

This adds:

```json
{"ref_norm": "...", "pred_norm": "..."}
```

## 9. Dependencies

Minimum:

```bash
pip install tqdm
```

Recommended:

```bash
pip install editdistance whisper-normalizer
```

For Chinese text normalization, place the `cn_tn` folder in the same directory as `evaluate_wer.py`, or make sure it is in `PYTHONPATH`.

