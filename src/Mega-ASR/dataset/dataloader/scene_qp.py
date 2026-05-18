# scene_combinations_four.py
# 四组合场景配置文件

# 基础类别顺序：
# crosstalk > distortion > stutter > noise

# 三三组合（来源集合：crosstalk, distortion, stutter, noise）
TRIPLE_BASE = [
    ["crosstalk", "distortion", "stutter"],
    ["crosstalk", "distortion", "noise"],
    ["crosstalk", "stutter",  "noise"],
    ["distortion", "stutter", "noise"],
]

PREFIXES = ["barrier", "far_field", "strong_echo"]

SCENE_COMBINATIONS = [
    # ========== 前 12 个：三三组合 + 三大前缀（barrier / far_field / strong_echo） ==========

    # --- barrier ---
    {"name": "barrier_crosstalk_distortion_stutter",
     "scenes": ["barrier", "crosstalk", "distortion", "stutter"]},

    {"name": "barrier_crosstalk_distortion_noise",
     "scenes": ["barrier", "crosstalk", "distortion", "noise"]},

    {"name": "barrier_crosstalk_stutter_noise",
     "scenes": ["barrier", "crosstalk", "stutter", "noise"]},

    {"name": "barrier_distortion_stutter_noise",
     "scenes": ["barrier", "distortion", "stutter", "noise"]},

    # --- far_field ---
    {"name": "far_field_crosstalk_distortion_stutter",
     "scenes": ["far_field", "crosstalk", "distortion", "stutter"]},

    {"name": "far_field_crosstalk_distortion_noise",
     "scenes": ["far_field", "crosstalk", "distortion", "noise"]},

    {"name": "far_field_crosstalk_stutter_noise",
     "scenes": ["far_field", "crosstalk", "stutter", "noise"]},

    {"name": "far_field_distortion_stutter_noise",
     "scenes": ["far_field", "distortion", "stutter", "noise"]},

    # --- strong_echo ---
    {"name": "strong_echo_crosstalk_distortion_stutter",
     "scenes": ["strong_echo", "crosstalk", "distortion", "stutter"]},

    {"name": "strong_echo_crosstalk_distortion_noise",
     "scenes": ["strong_echo", "crosstalk", "distortion", "noise"]},

    {"name": "strong_echo_crosstalk_stutter_noise",
     "scenes": ["strong_echo", "crosstalk", "stutter", "noise"]},

    {"name": "strong_echo_distortion_stutter_noise",
     "scenes": ["strong_echo", "distortion", "stutter", "noise"]},

    # ========== 最后 1 个：四组合基础集合 ==========
    {
        "name": "crosstalk_distortion_stutter_noise",
        "scenes": ["crosstalk", "distortion", "stutter", "noise"]
    },


    {
        "name": "barrier_crosstalk_distortion_stutter_noise",
        "scenes": ["barrier", "crosstalk", "distortion", "stutter", "noise"]
    },
    {
        "name": "far_field_crosstalk_distortion_stutter_noise",
        "scenes": ["far_field", "crosstalk", "distortion", "stutter", "noise"]
    },
    {
        "name": "strong_echo_crosstalk_distortion_stutter_noise",
        "scenes": ["strong_echo", "crosstalk", "distortion", "stutter", "noise"]
    }

]


# ========== 启用全部配置 ==========
ENABLED_COMBINATIONS = [
    # --- barrier ---
    "barrier_crosstalk_distortion_stutter",
    "barrier_crosstalk_distortion_noise",
    "barrier_crosstalk_stutter_noise",
    "barrier_distortion_stutter_noise",

    # --- far_field ---
    "far_field_crosstalk_distortion_stutter",
    "far_field_crosstalk_distortion_noise",
    "far_field_crosstalk_stutter_noise",
    "far_field_distortion_stutter_noise",

    # --- strong_echo ---
    "strong_echo_crosstalk_distortion_stutter",
    "strong_echo_crosstalk_distortion_noise",
    "strong_echo_crosstalk_stutter_noise",
    "strong_echo_distortion_stutter_noise",

    # --- 基础四组合 ---
    "crosstalk_distortion_stutter_noise",




    "barrier_crosstalk_distortion_stutter_noise",
    "far_field_crosstalk_distortion_stutter_noise",
    "strong_echo_crosstalk_distortion_stutter_noise",
]
