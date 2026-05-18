# scene_combinations_single.py
# 单类场景配置文件（共 7 个）

SCENE_COMBINATIONS = [
    {"name": "barrier",      "scenes": ["barrier"]},
    {"name": "crosstalk",    "scenes": ["crosstalk"]},
    {"name": "distortion",   "scenes": ["distortion"]},
    {"name": "far_field",    "scenes": ["far_field"]},
    {"name": "noise",        "scenes": ["noise"]},
    {"name": "strong_echo",  "scenes": ["strong_echo"]},
    {"name": "stutter",      "scenes": ["stutter"]},
]

ENABLED_COMBINATIONS = [
    "barrier",
    "crosstalk",
    "distortion",
    "far_field",
    "noise",
    "strong_echo",
    "stutter",
]
