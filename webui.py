"""
语音识别控制台 v2
布局：1:1:3 横向
- 左栏：系统监控（CPU/GPU/内存等，0.5s 刷新）
- 中栏：控制台（语言选择 + Qwen3 对比开关）
- 右栏:转写记录（金色频谱 + 重播 + 下载，支持对比双列）
"""

import base64
import math
import os
import platform
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# ──────────────────────────────────────────────
# 可选依赖：psutil（CPU/内存），pynvml（NVIDIA GPU）
# 任何缺失都不报错，对应字段显示为 "—"
# ──────────────────────────────────────────────
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_NVML = True
except Exception:
    HAS_NVML = False

OS_NAME = platform.system()  # 'Darwin' | 'Windows' | 'Linux'

# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Mega-ASR Console",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# 样式
# ──────────────────────────────────────────────
GOLD = "#d4af37"
GOLD_SOFT = "#b8941f"
INK = "#1a1a1a"
LINE = "#ececec"
MUTE = "#8a8a8a"

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
    }}
    #MainMenu, header, footer {{ visibility: hidden; }}
    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }}

    /* ── 顶部 logo + 标题 ───────────────────────── */
    .brand {{
        display: flex; align-items: center; gap: 0.9rem;
        margin-bottom: 1.5rem;
    }}
    .brand img {{ width: 38px; height: 38px; border-radius: 6px; }}
    .brand-title {{
        font-size: 1.35rem; font-weight: 600; color: {INK};
        letter-spacing: 0.01em; line-height: 1.1;
    }}
    .brand-sub {{
        font-size: 0.7rem; color: {MUTE};
        letter-spacing: 0.18em; text-transform: uppercase;
        margin-top: 2px;
    }}

    /* ── 区段标题 ──────────────────────────────── */
    .section-label {{
        font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.16em; text-transform: uppercase;
        color: #9a9a9a;
        margin: 0 0 0.8rem 0;
    }}

    /* ── 卡片 ──────────────────────────────────── */
    .panel {{
        background: #ffffff;
        border: 1px solid {LINE};
        border-radius: 8px;
        padding: 1.25rem 1.25rem;
    }}

    /* ── 系统监控指标 ──────────────────────────── */
    .metric {{
        padding: 0.9rem 0;
        border-bottom: 1px solid #f3f3f3;
    }}
    .metric:last-child {{ border-bottom: none; }}
    .metric-label {{
        font-size: 0.68rem; color: {MUTE};
        letter-spacing: 0.12em; text-transform: uppercase;
        margin-bottom: 0.35rem;
    }}
    .metric-row {{
        display: flex; align-items: baseline; justify-content: space-between;
        gap: 0.5rem;
    }}
    .metric-val {{
        font-size: 1.5rem; font-weight: 600; color: {INK};
        font-variant-numeric: tabular-nums;
        line-height: 1;
    }}
    .metric-unit {{
        font-size: 0.75rem; color: {MUTE};
        font-weight: 500;
    }}
    .metric-bar {{
        position: relative;
        height: 3px; background: #f0f0f0; border-radius: 2px;
        margin-top: 0.55rem; overflow: hidden;
    }}
    .metric-bar > span {{
        position: absolute; left: 0; top: 0; bottom: 0;
        background: {INK}; border-radius: 2px;
        transition: width 0.4s ease;
    }}
    .metric-bar.gold > span {{ background: {GOLD}; }}
    .metric-na {{ color: #c0c0c0; font-size: 1.2rem; font-weight: 500; }}

    /* ── 状态徽章 ──────────────────────────────── */
    .status-pill {{
        display: inline-flex; align-items: center; gap: 0.5rem;
        font-size: 0.75rem; color: #555;
        padding: 0.3rem 0.7rem;
        background: #f7f7f7;
        border-radius: 999px;
        border: 1px solid {LINE};
        margin-bottom: 1rem;
    }}
    .dot {{ width: 6px; height: 6px; border-radius: 50%; background: #c0c0c0; }}
    .dot.live {{ background: #d64545; animation: pulse 1.4s infinite; }}
    @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0   rgba(214,69,69,.5); }}
        70%  {{ box-shadow: 0 0 0 8px rgba(214,69,69,0); }}
        100% {{ box-shadow: 0 0 0 0   rgba(214,69,69,0); }}
    }}

    /* ── 按钮 ──────────────────────────────────── */
    .stButton > button {{
        width: 100%;
        border-radius: 6px;
        border: 1px solid {INK};
        background: {INK};
        color: #fafafa;
        font-weight: 500;
        letter-spacing: 0.04em;
        padding: 0.55rem 1rem;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        background: #333; border-color: #333; color: #fff;
        transform: translateY(-1px);
    }}
    div[data-testid="column"]:nth-of-type(2) > div .stButton > button {{
        background: #ffffff; color: {INK}; border: 1px solid #d8d8d8;
    }}
    div[data-testid="column"]:nth-of-type(2) > div .stButton > button:hover {{
        background: #f5f5f5; border-color: {INK};
    }}

    /* ── 控件文字 ──────────────────────────────── */
    .stSelectbox label, .stToggle label, .stRadio label {{
        font-size: 0.78rem !important;
        color: #555 !important;
        font-weight: 500 !important;
    }}

    /* ── 转写条目 ──────────────────────────────── */
    .entry {{
        padding: 1.1rem 0 1.25rem 0;
        border-bottom: 1px solid #f0f0f0;
    }}
    .entry:last-child {{ border-bottom: none; }}
    .entry-meta {{
        font-size: 0.72rem; color: #a8a8a8;
        letter-spacing: 0.04em; font-variant-numeric: tabular-nums;
        margin-bottom: 0.6rem;
        display: flex; gap: 0.6rem; align-items: center;
    }}
    .entry-meta .sep {{ color: #d0d0d0; }}
    .entry-text {{
        font-size: 0.98rem; color: #1f1f1f; line-height: 1.65;
    }}

    /* 对比双列 */
    .cmp-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.9rem;
        margin-top: 0.5rem;
    }}
    .cmp-card {{
        padding: 0.7rem 0.85rem;
        border: 1px solid {LINE};
        border-radius: 6px;
        background: #fafafa;
    }}
    .cmp-tag {{
        font-size: 0.65rem; font-weight: 600;
        letter-spacing: 0.14em; text-transform: uppercase;
        color: {MUTE};
        margin-bottom: 0.4rem;
    }}
    .cmp-tag.primary {{ color: {GOLD_SOFT}; }}
    .cmp-card.primary {{ background: #fffaf0; border-color: #f0e3b8; }}

    /* 频谱容器 */
    .spec-wrap {{
        background: #0e0e0e;
        border-radius: 6px;
        padding: 0;
        margin: 0.6rem 0 0.7rem 0;
        overflow: hidden;
    }}

    /* 音频播放器细化 */
    audio {{ width: 100%; height: 34px; margin-top: 0.2rem; }}

    /* 下载按钮 */
    .dl-link {{
        display: inline-block;
        font-size: 0.72rem; color: {MUTE};
        text-decoration: none;
        padding: 0.25rem 0.65rem;
        border: 1px solid {LINE};
        border-radius: 4px;
        margin-left: 0.5rem;
        transition: all 0.15s ease;
    }}
    .dl-link:hover {{ color: {INK}; border-color: {INK}; }}

    /* 空状态 */
    .empty {{
        text-align: center; padding: 4rem 1rem;
        color: #bdbdbd; font-size: 0.9rem;
    }}
    .empty-mark {{
        font-size: 2rem; color: #e0e0e0;
        margin-bottom: 0.8rem; font-weight: 200;
    }}

    hr {{ border: none; border-top: 1px solid {LINE}; margin: 1rem 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 系统指标读取（跨平台容错）
# ──────────────────────────────────────────────
def read_cpu_percent():
    if not HAS_PSUTIL:
        return None
    try:
        return psutil.cpu_percent(interval=None)
    except Exception:
        return None


def read_mem_percent():
    if not HAS_PSUTIL:
        return None
    try:
        return psutil.virtual_memory().percent
    except Exception:
        return None


def read_gpu():
    """返回 (使用率%, 显存%)；任何平台失败返回 (None, None)"""
    if HAS_NVML:
        try:
            h = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
            mem = pynvml.nvmlDeviceGetMemoryInfo(h)
            return util, mem.used / mem.total * 100
        except Exception:
            return None, None
    return None, None


def read_disk_percent():
    if not HAS_PSUTIL:
        return None
    try:
        path = "C:\\" if OS_NAME == "Windows" else "/"
        return psutil.disk_usage(path).percent
    except Exception:
        return None


def read_net_kbps():
    """瞬时网速（KB/s），基于两次采样差"""
    if not HAS_PSUTIL:
        return None
    try:
        now = psutil.net_io_counters()
        t = time.time()
        prev = st.session_state.get("_net_prev")
        st.session_state._net_prev = (now.bytes_sent + now.bytes_recv, t)
        if prev is None:
            return 0.0
        dbytes = (now.bytes_sent + now.bytes_recv) - prev[0]
        dt = max(t - prev[1], 1e-6)
        return max(dbytes / dt / 1024, 0)
    except Exception:
        return None


def render_metric(label, value, unit="%", bar=True, gold=False, max_bar=100):
    """渲染一条指标。value 为 None 时显示 N/A。"""
    if value is None:
        body = '<div class="metric-row"><span class="metric-na">—</span></div>'
    else:
        v_display = f"{value:.1f}" if isinstance(value, float) else str(value)
        body = (
            f'<div class="metric-row">'
            f'<span class="metric-val">{v_display}</span>'
            f'<span class="metric-unit">{unit}</span>'
            f"</div>"
        )
        if bar:
            pct = min(max(value / max_bar * 100, 0), 100)
            cls = "metric-bar gold" if gold else "metric-bar"
            body += f'<div class="{cls}"><span style="width:{pct:.1f}%"></span></div>'
    return (
        f'<div class="metric">'
        f'<div class="metric-label">{label}</div>'
        f"{body}</div>"
    )


# ──────────────────────────────────────────────
# 模拟波形 + 频谱 SVG
# ──────────────────────────────────────────────
def gen_waveform(duration_s: float, seed: int) -> list:
    """生成 0~1 范围的波形数据，bars 数固定 100 条（对应 10s）"""
    rng = random.Random(seed)
    total_bars = 100
    active = min(int(duration_s * 10), total_bars)
    bars = []
    for i in range(total_bars):
        if i < active:
            envelope = 0.4 + 0.4 * abs(math.sin(i * 0.18 + seed * 0.1))
            jitter = rng.random() * 0.55
            bars.append(min(envelope * (0.5 + jitter), 1.0))
        else:
            bars.append(0)  # 未填充 → 黑色
    return bars


def waveform_svg(bars: list, height: int = 64) -> str:
    """金色频谱 SVG，居中对称"""
    width = 100 * 6  # 600px，100 根 × 6px
    bar_w = 4
    gap = 2
    mid = height / 2
    rects = []
    for i, v in enumerate(bars):
        if v <= 0:
            continue
        h = max(v * (height - 4), 2)
        x = i * (bar_w + gap)
        y = mid - h / 2
        rects.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" '
            f'rx="1" fill="{GOLD}"/>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" '
        f'style="display:block;background:#0e0e0e;">'
        + "".join(rects)
        + "</svg>"
    )


# ──────────────────────────────────────────────
# 生成一段 WAV 音频（模拟）
# ──────────────────────────────────────────────
def make_wav_bytes(duration_s: float, seed: int) -> bytes:
    import io, struct, wave

    sr = 16000
    n = int(sr * duration_s)
    rng = random.Random(seed)
    base_freq = 180 + rng.random() * 80
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            envelope = math.sin(t * 2 * math.pi / max(duration_s, 0.01)) ** 2
            tone = math.sin(2 * math.pi * base_freq * t) * 0.25
            noise = (rng.random() - 0.5) * 0.12
            sample = int((tone + noise) * envelope * 30000)
            sample = max(-32768, min(32767, sample))
            frames += struct.pack("<h", sample)
        w.writeframes(bytes(frames))
    return buf.getvalue()


def audio_data_uri(wav_bytes: bytes) -> str:
    b64 = base64.b64encode(wav_bytes).decode()
    return f"data:audio/wav;base64,{b64}"


# ──────────────────────────────────────────────
# 状态初始化
# ──────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = []
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "seed_counter" not in st.session_state:
    st.session_state.seed_counter = 1

MOCK_TEXTS = [
    "今天的会议主要讨论了第四季度的产品路线图。",
    "我们需要在本月底之前完成原型设计。",
    "客户反馈表明界面的响应速度仍有提升空间。",
    "下一步计划是在两周内启动用户测试。",
    "服务器在高并发场景下的稳定性已通过验证。",
    "整体进度比预期提前了大约三天。",
]


def qwen_variant(text: str, seed: int) -> str:
    rng = random.Random(seed)
    swaps = [
        ("第四季度", "Q4"),
        ("产品路线图", "产品规划"),
        ("原型设计", "原型"),
        ("界面", "UI"),
        ("响应速度", "响应延迟"),
        ("启动用户测试", "开始用户测试"),
        ("服务器", "后端服务"),
        ("高并发", "并发"),
        ("整体进度", "进度"),
    ]
    out = text
    for a, b in swaps:
        if a in out and rng.random() < 0.55:
            out = out.replace(a, b)
    return out


def add_record(language: str, compare: bool):
    seed = st.session_state.seed_counter
    st.session_state.seed_counter += 1
    duration = round(random.uniform(3, 12), 1)
    text = random.choice(MOCK_TEXTS)
    record = {
        "id": seed,
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "language": language,
        "duration": duration,
        "text": text,
        "compare": compare,
        "qwen_text": qwen_variant(text, seed) if compare else None,
        "audio": make_wav_bytes(min(duration, 10), seed),
        "waveform": gen_waveform(duration, seed),
    }
    st.session_state.records.insert(0, record)


# ──────────────────────────────────────────────
# Logo + 标题
# ──────────────────────────────────────────────
try:
    logo_path = Path(__file__).parent / "logo.png"
except NameError:
    logo_path = Path("logo.png")

if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="logo"/>'
else:
    logo_html = '<div style="width:38px;height:38px;background:#1a1a1a;border-radius:6px;"></div>'

st.markdown(
    f"""
    <div class="brand">
        {logo_html}
        <div>
            <div class="brand-title">Mega-ASR Console</div>
            <div class="brand-sub">Speech Recognition · Realtime</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 三栏布局 1:1:3
# ──────────────────────────────────────────────
col_sys, col_ctrl, col_log = st.columns([1, 1, 3], gap="large")

# ============== 左栏：系统监控 ==============
with col_sys:
    st.markdown('<div class="section-label">系统监控</div>', unsafe_allow_html=True)

    cpu = read_cpu_percent()
    mem = read_mem_percent()
    gpu_util, gpu_mem = read_gpu()
    disk = read_disk_percent()
    net = read_net_kbps()

    html = '<div class="panel">'
    html += render_metric("CPU 使用率", cpu, "%", gold=True)
    html += render_metric("内存", mem, "%")
    html += render_metric("GPU 使用率", gpu_util, "%", gold=True)
    html += render_metric("显存", gpu_mem, "%")
    html += render_metric("磁盘", disk, "%")
    html += render_metric("网络 I/O", net, "KB/s", max_bar=512)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:0.68rem;color:#b0b0b0;margin-top:0.8rem;'
        f'letter-spacing:0.1em;text-align:center;">'
        f'{OS_NAME.upper()} · {platform.machine()}</div>',
        unsafe_allow_html=True,
    )

# ============== 中栏：控制台 ==============
with col_ctrl:
    st.markdown('<div class="section-label">控制台</div>', unsafe_allow_html=True)

    status_dot = "live" if st.session_state.is_recording else ""
    status_label = "录音中" if st.session_state.is_recording else "待机"
    st.markdown(
        f'<div class="status-pill"><span class="dot {status_dot}"></span>{status_label}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="font-size:0.7rem;color:{MUTE};letter-spacing:0.12em;'
        f'text-transform:uppercase;margin-bottom:0.3rem;">模型</div>'
        f'<div style="font-size:1rem;color:{INK};font-weight:600;'
        f'margin-bottom:1rem;">Mega-ASR</div>',
        unsafe_allow_html=True,
    )

    language = st.selectbox(
        "识别语言",
        ["中文（普通话）", "English", "中英混合", "日本語"],
        label_visibility="visible",
    )

    compare = st.toggle("启用 Qwen3-ASR 对比", value=False)

    st.markdown("<hr>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        btn = "停止" if st.session_state.is_recording else "开始录音"
        if st.button(btn, use_container_width=True, key="rec_btn"):
            if st.session_state.is_recording:
                add_record(language, compare)
                st.session_state.is_recording = False
            else:
                st.session_state.is_recording = True
            st.rerun()
    with c2:
        if st.button("清空记录", use_container_width=True, key="clr_btn"):
            st.session_state.records = []
            st.rerun()

# ============== 右栏：转写记录 ==============
with col_log:
    head_l, head_r = st.columns([3, 1])
    with head_l:
        st.markdown('<div class="section-label">转写记录</div>', unsafe_allow_html=True)
    with head_r:
        st.markdown(
            f'<div style="text-align:right;font-size:0.72rem;color:{MUTE};'
            f'margin-top:2px;">共 {len(st.session_state.records)} 条</div>',
            unsafe_allow_html=True,
        )

    if not st.session_state.records:
        st.markdown(
            '<div class="panel"><div class="empty">'
            '<div class="empty-mark">◌</div>'
            '暂无记录 · 点击"开始录音"以生成示例'
            "</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        for r in st.session_state.records:
            duration_disp = f"{r['duration']:.1f}s"
            if r["duration"] > 10:
                duration_disp += " · 频谱仅显示前 10s"

            meta = (
                f'<div class="entry-meta">'
                f'<span>{r["date"]} {r["time"]}</span>'
                f'<span class="sep">·</span>'
                f'<span>{r["language"]}</span>'
                f'<span class="sep">·</span>'
                f'<span>{duration_disp}</span>'
                f"</div>"
            )

            svg = waveform_svg(r["waveform"])
            spec = f'<div class="spec-wrap">{svg}</div>'

            uri = audio_data_uri(r["audio"])
            player = (
                f'<div style="display:flex;align-items:center;gap:0.5rem;'
                f'margin-bottom:0.3rem;">'
                f'<audio controls preload="none" src="{uri}"></audio>'
                f'<a class="dl-link" href="{uri}" '
                f'download="mega-asr-{r["id"]}.wav">下载</a>'
                f"</div>"
            )

            if r["compare"] and r["qwen_text"]:
                body = (
                    '<div class="cmp-grid">'
                    f'<div class="cmp-card primary">'
                    f'<div class="cmp-tag primary">Mega-ASR</div>'
                    f'<div class="entry-text">{r["text"]}</div>'
                    f"</div>"
                    f'<div class="cmp-card">'
                    f'<div class="cmp-tag">Qwen3-ASR</div>'
                    f'<div class="entry-text">{r["qwen_text"]}</div>'
                    f"</div>"
                    "</div>"
                )
            else:
                body = f'<div class="entry-text">{r["text"]}</div>'

            st.markdown(
                f'<div class="entry">{meta}{spec}{player}{body}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 自动刷新：监控 0.5s；录音中追加记录
# ──────────────────────────────────────────────
if st.session_state.is_recording:
    time.sleep(1.8)
    add_record(language, compare)
    st.rerun()
else:
    time.sleep(0.5)
    st.rerun()