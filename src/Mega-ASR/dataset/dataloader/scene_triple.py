SCENE_COMBINATIONS = [
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



ENABLED_COMBINATIONS = [
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
