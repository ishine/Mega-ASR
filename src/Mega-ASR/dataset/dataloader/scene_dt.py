# scene_combinations.py
# 场景组合配置文件

SCENE_COMBINATIONS = [
    # # ========== 单类场景 ==========
    # {"name": "barrier", "scenes": ["barrier"]},
    # {"name": "crosstalk", "scenes": ["crosstalk"]},
    # {"name": "distortion", "scenes": ["distortion"]},
    # {"name": "far_field", "scenes": ["far_field"]},
    # {"name": "noise", "scenes": ["noise"]},
    # {"name": "strong_echo", "scenes": ["strong_echo"]},
    # {"name": "stutter", "scenes": ["stutter"]},

    # ========== 双类组合 ==========
    # barrier 组合（不能与 far_field / strong_echo 同时出现）
    {"name": "barrier_crosstalk", "scenes": ["barrier", "crosstalk"]},
    {"name": "barrier_distortion", "scenes": ["barrier", "distortion"]},
    {"name": "barrier_noise", "scenes": ["barrier", "noise"]},
    {"name": "barrier_stutter", "scenes": ["barrier", "stutter"]},

    # far_field 组合（不能与 barrier / strong_echo 同时出现）
    {"name": "far_field_crosstalk", "scenes": ["far_field", "crosstalk"]},
    {"name": "far_field_distortion", "scenes": ["far_field", "distortion"]},
    {"name": "far_field_noise", "scenes": ["far_field", "noise"]},
    {"name": "far_field_stutter", "scenes": ["far_field", "stutter"]},

    # strong_echo 组合（不能与 barrier / far_field 同时出现）
    {"name": "strong_echo_crosstalk", "scenes": ["strong_echo", "crosstalk"]},
    {"name": "strong_echo_distortion", "scenes": ["strong_echo", "distortion"]},
    {"name": "strong_echo_noise", "scenes": ["strong_echo", "noise"]},
    {"name": "strong_echo_stutter", "scenes": ["strong_echo", "stutter"]},

    # 余下类别之间两两组合（crosstalk / distortion / noise / stutter）
    {"name": "crosstalk_distortion", "scenes": ["crosstalk", "distortion"]},
    {"name": "crosstalk_noise", "scenes": ["crosstalk", "noise"]},
    {"name": "crosstalk_stutter", "scenes": ["crosstalk", "stutter"]},

    {"name": "distortion_noise", "scenes": ["distortion", "noise"]},
    {"name": "distortion_stutter", "scenes": ["distortion", "stutter"]},

    {"name": "noise_stutter", "scenes": ["noise", "stutter"]},

    # ========== 前 9 个：三大前缀 + (crosstalk/distortion/stutter)两两组合 ==========

    # --- barrier ---
    {"name": "barrier_crosstalk_distortion", "scenes": ["barrier", "crosstalk", "distortion"]},
    {"name": "barrier_crosstalk_stutter",    "scenes": ["barrier", "crosstalk", "stutter"]},
    {"name": "barrier_distortion_stutter",   "scenes": ["barrier", "distortion", "stutter"]},

    # --- far_field ---
    {"name": "far_field_crosstalk_distortion", "scenes": ["far_field", "crosstalk", "distortion"]},
    {"name": "far_field_crosstalk_stutter",    "scenes": ["far_field", "crosstalk", "stutter"]},
    {"name": "far_field_distortion_stutter",   "scenes": ["far_field", "distortion", "stutter"]},

    # --- strong_echo ---
    {"name": "strong_echo_crosstalk_distortion", "scenes": ["strong_echo", "crosstalk", "distortion"]},
    {"name": "strong_echo_crosstalk_stutter",    "scenes": ["strong_echo", "crosstalk", "stutter"]},
    {"name": "strong_echo_distortion_stutter",   "scenes": ["strong_echo", "distortion", "stutter"]},

    # ========== 后 4 个：(crosstalk/distortion/stutter/noise) 三三组合 ==========
    {"name": "crosstalk_distortion_stutter", "scenes": ["crosstalk", "distortion", "stutter"]},
    {"name": "crosstalk_distortion_noise",   "scenes": ["crosstalk", "distortion", "noise"]},
    {"name": "crosstalk_stutter_noise",      "scenes": ["crosstalk", "stutter", "noise"]},
    {"name": "distortion_stutter_noise",     "scenes": ["distortion", "stutter", "noise"]},
]

# 启用全部组合
ENABLED_COMBINATIONS = [
    # # 单类
    # "barrier", "crosstalk", "distortion", "far_field",
    # "noise", "strong_echo", "stutter",

    # # barrier *
    "barrier_crosstalk", "barrier_distortion",
    "barrier_noise", "barrier_stutter",

    # far_field *
    "far_field_crosstalk", 
    "far_field_distortion",
    "far_field_noise", "far_field_stutter",

    # strong_echo *
    "strong_echo_crosstalk", "strong_echo_distortion",
    "strong_echo_noise", "strong_echo_stutter",

    # 余下四类内部组合
    "crosstalk_distortion", "crosstalk_noise", "crosstalk_stutter",
    "distortion_noise", "distortion_stutter",
    "noise_stutter",

    # --- barrier 前缀 ---
    "barrier_crosstalk_distortion",
    "barrier_crosstalk_stutter",
    "barrier_distortion_stutter",

    # --- far_field 前缀 ---
    "far_field_crosstalk_distortion",
    "far_field_crosstalk_stutter",
    "far_field_distortion_stutter",

    # --- strong_echo 前缀 ---
    "strong_echo_crosstalk_distortion",
    "strong_echo_crosstalk_stutter",
    "strong_echo_distortion_stutter",

    # --- 内部三三组合 ---
    "crosstalk_distortion_stutter",
    "crosstalk_distortion_noise",
    "crosstalk_stutter_noise",
    "distortion_stutter_noise",
]
