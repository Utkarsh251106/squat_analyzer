"""
app.py
------
Streamlit web application for the Squat Analyzer.
Supports live webcam feed and uploaded video files.

Run:
    streamlit run app.py
"""

import cv2
import tempfile
import time
import streamlit as st
from pathlib import Path

from pose_estimator import PoseEstimator
from counter import SquatCounter
from analyzer import analyze_frame

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Squat Analyzer",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark industrial theme */
.stApp {
    background-color: #0d0f12;
    color: #e8e6e0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #131619;
    border-right: 1px solid #2a2d33;
}

/* Metric cards */
.metric-card {
    background: #1a1d22;
    border: 1px solid #2a2d33;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
}
.metric-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    color: #f0c040;
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    color: #7a7f8a;
    text-transform: uppercase;
    margin-top: 6px;
}

/* Status badges */
.status-correct {
    background: #0d2e1a;
    border: 1px solid #1a6b35;
    color: #3ddc70;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 0.9rem;
    font-weight: 600;
}
.status-incorrect {
    background: #2e0d0d;
    border: 1px solid #6b1a1a;
    color: #dc3d3d;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 0.9rem;
    font-weight: 600;
}

/* Title */
.app-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 0.06em;
    color: #f0c040;
    margin-bottom: 0;
    line-height: 1;
}
.app-subtitle {
    color: #7a7f8a;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 24px;
}

/* Buttons */
.stButton > button {
    background: #f0c040 !important;
    color: #0d0f12 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    letter-spacing: 0.05em;
}
.stButton > button:hover {
    background: #d4a830 !important;
}

div[data-testid="stVideo"] video {
    border-radius: 12px;
    border: 1px solid #2a2d33;
}

.feedback-item {
    background: #1a1d22;
    border-left: 3px solid #dc3d3d;
    border-radius: 0 8px 8px 0;
    padding: 8px 14px;
    margin: 4px 0;
    font-size: 0.88rem;
    color: #e8e6e0;
}
.feedback-item.correct {
    border-left-color: #3ddc70;
}

.rule-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1a1d22;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px 0;
    font-size: 0.82rem;
}
.rule-pass { color: #3ddc70; font-weight: 600; }
.rule-fail { color: #dc3d3d; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏋️ Squat Analyzer")
    st.markdown("---")

    mode = st.radio(
        "Input mode",
        ["📹 Live Webcam", "📂 Upload Video"],
        index=0
    )

    st.markdown("---")
    st.markdown("### Thresholds")
    back_thresh  = st.slider("Max back angle (°)",  10, 60, 35)
    knee_thresh  = st.slider("Knee overshoot tolerance", 0.01, 0.15, 0.05, 0.01)
    down_angle   = st.slider("Squat 'down' knee angle (°)", 70, 120, 100)
    up_angle     = st.slider("Squat 'up' knee angle (°)",  130, 170, 150)

    st.markdown("---")
    st.markdown("### About")
    st.caption(
        "Uses MediaPipe BlazePose to extract 33 body landmarks and applies "
        "3 computational rules to evaluate squat form in real time."
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="app-title">SQUAT ANALYZER</p>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">AI-powered posture evaluation & rep counter</p>',
            unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_feed, col_stats = st.columns([3, 1], gap="large")

# ── Session state ─────────────────────────────────────────────────────────────
if "counter" not in st.session_state:
    st.session_state.counter   = SquatCounter(
        down_threshold=down_angle, up_threshold=up_angle
    )
if "estimator" not in st.session_state:
    st.session_state.estimator = PoseEstimator()
if "running" not in st.session_state:
    st.session_state.running   = False
if "last_result" not in st.session_state:
    st.session_state.last_result = {}


# ── Stats panel (right column) ─────────────────────────────────────────────
with col_stats:
    st.markdown("#### Live Stats")

    count_ph    = st.empty()
    status_ph   = st.empty()
    angle_ph    = st.empty()
    feedback_ph = st.empty()

    st.markdown("---")
    if st.button("🔄 Reset Counter"):
        st.session_state.counter.reset()
        st.rerun()

    st.markdown("---")
    st.markdown("#### Rule checks")
    rules_ph = st.empty()

    def render_stats(result):
        count_ph.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{result.get('squat_count', 0)}</div>
            <div class="metric-label">Squats</div>
        </div>""", unsafe_allow_html=True)

        if result.get("is_correct"):
            status_ph.markdown(
                '<div class="status-correct">✓ Correct posture</div>',
                unsafe_allow_html=True)
        else:
            status_ph.markdown(
                '<div class="status-incorrect">✗ Form issues detected</div>',
                unsafe_allow_html=True)

        angle_ph.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="font-size:2rem">
                {result.get('knee_angle', 0):.0f}°
            </div>
            <div class="metric-label">Knee angle</div>
        </div>""", unsafe_allow_html=True)

        msgs = result.get("messages", [])
        is_ok = result.get("is_correct", False)
        fb_html = "".join(
            f'<div class="feedback-item {"correct" if is_ok else ""}">'
            f'{"✓" if is_ok else "✗"} {m}</div>'
            for m in msgs
        )
        feedback_ph.markdown(fb_html, unsafe_allow_html=True)

        back_angle = result.get("back_angle", 0)
        overshoot  = result.get("knee_overshoot", 0)
        in_squat   = result.get("in_squat", False)
        rules_ph.markdown(f"""
        <div class="rule-bar">
            <span>Back angle</span>
            <span class="{'rule-pass' if back_angle <= back_thresh else 'rule-fail'}">
                {back_angle:.1f}°
            </span>
        </div>
        <div class="rule-bar">
            <span>Knee overshoot</span>
            <span class="{'rule-pass' if overshoot <= knee_thresh else 'rule-fail'}">
                {overshoot:.3f}
            </span>
        </div>
        <div class="rule-bar">
            <span>Phase</span>
            <span class="rule-pass">{"↓ DOWN" if in_squat else "↑ UP"}</span>
        </div>
        """, unsafe_allow_html=True)

    render_stats({})


# ── Main feed ─────────────────────────────────────────────────────────────────
with col_feed:

    # ── VIDEO FILE MODE ───────────────────────────────────────────────────────
    if "Upload" in mode:
        uploaded = st.file_uploader(
            "Upload a video file", type=["mp4", "mov", "avi", "mkv"]
        )

        if uploaded:
            # Save to temp file
            tfile = tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded.name).suffix
            )
            tfile.write(uploaded.read())
            tfile.flush()

            col_b1, col_b2 = st.columns(2)
            start_btn = col_b1.button("▶ Analyze Video")
            stop_btn  = col_b2.button("⏹ Stop")

            if start_btn:
                st.session_state.running = True
                st.session_state.counter.reset()

            if stop_btn:
                st.session_state.running = False

            frame_ph = st.empty()

            if st.session_state.running:
                cap = cv2.VideoCapture(tfile.name)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30
                estimator = st.session_state.estimator
                counter   = st.session_state.counter

                while cap.isOpened() and st.session_state.running:
                    ret, frame = cap.read()
                    if not ret:
                        st.session_state.running = False
                        break

                    frame, result = analyze_frame(frame, estimator, counter)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_ph.image(frame_rgb, channels="RGB", use_column_width=True)

                    with col_stats:
                        render_stats(result)

                    time.sleep(1 / fps)

                cap.release()
                st.success(f"✅ Analysis complete — {counter.count} squats counted.")

    # ── WEBCAM MODE ───────────────────────────────────────────────────────────
    else:
        st.info(
            "💡 **Webcam mode** — position yourself **side-on** to the camera "
            "for best accuracy. Press **Start** to begin."
        )

        col_b1, col_b2 = st.columns(2)
        start_btn = col_b1.button("▶ Start Webcam")
        stop_btn  = col_b2.button("⏹ Stop")

        if start_btn:
            st.session_state.running = True
            st.session_state.counter.reset()
        if stop_btn:
            st.session_state.running = False

        frame_ph = st.empty()

        if st.session_state.running:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Cannot access webcam. Check your camera permissions.")
                st.session_state.running = False
            else:
                estimator = st.session_state.estimator
                counter   = st.session_state.counter

                while st.session_state.running:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame, result = analyze_frame(frame, estimator, counter)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_ph.image(frame_rgb, channels="RGB", use_column_width=True)

                    with col_stats:
                        render_stats(result)

                cap.release()