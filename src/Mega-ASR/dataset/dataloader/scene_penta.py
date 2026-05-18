# scene_combinations_five.py
# 五组合场景配置文件

SCENE_COMBINATIONS = [
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

ENABLED_COMBINATIONS = [
    "barrier_crosstalk_distortion_stutter_noise",
    "far_field_crosstalk_distortion_stutter_noise",
    "strong_echo_crosstalk_distortion_stutter_noise",
]
