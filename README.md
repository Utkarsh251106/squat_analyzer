# 🏋️ Squat Analyzer

AI-powered squat posture evaluation and rep counter using MediaPipe BlazePose.

---

## Technical Approach

- **Pose estimation**: MediaPipe BlazePose (33 landmarks, normalized coordinates)
- **3 evaluation rules**:
  - **Rule A — Back angle**: Computes the angle of the hip→shoulder vector relative to vertical. Must stay ≤ 35°.
  - **Rule B — Knee over toe**: In side-on view, knee x-coordinate must not exceed ankle x by more than 0.05 (normalized).
  - **Rule C — Hip depth**: At squat depth, hip y must be ≥ knee y (image coordinates). Only checked when knee angle < 120°.
- **Rep counting**: State machine (STANDING → DOWN → STANDING = 1 rep) with rolling-window smoothing over 8 frames.
- **Rendering**: OpenCV overlays for skeleton, feedback panel, squat counter, and knee angle.

---

## Assumptions

- Camera is positioned **side-on** to the user (Rule B requires side view)
- Single person in frame
- Adequate lighting for landmark detection
- User's full body (head to ankle) is visible in frame

---

## Limitations

- Side-on camera only — front-facing camera makes knee-over-toe rule unreliable
- No temporal smoothing on feedback text (may flicker on borderline frames)
- Thresholds (35° back angle, 0.05 knee overshoot) are fixed defaults — may need tuning per individual body proportions
- Occlusion of key landmarks causes fallback to "Position yourself in frame"
- Webcam in Streamlit app requires browser camera permissions

---

## Project Structure

```
squat_analyzer/
├── main.py            # CLI entry point (webcam + video file)
├── app.py             # Streamlit web application
├── analyzer.py        # Shared per-frame analysis logic
├── pose_estimator.py  # MediaPipe BlazePose wrapper
├── rules.py           # 3 evaluation rules (back, knee, depth)
├── feedback.py        # Rule results → feedback messages
├── counter.py         # Rep counting state machine
├── overlay.py         # OpenCV drawing utilities
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# Create conda environment
conda create -n squat_analyzer python=3.11 -y
conda activate squat_analyzer

# Install dependencies
pip install -r requirements.txt
```

---

## How to Run

### CLI — Webcam
```bash
python main.py
```

### CLI — Video file
```bash
python main.py --source path/to/video.mp4
```

### Streamlit Web App
```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

**Controls:**
- `Q` — quit (CLI only)
- `R` — reset counter (CLI only)
- Sidebar sliders adjust thresholds live (Streamlit only)