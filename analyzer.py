"""
analyzer.py
-----------
Core per-frame analysis logic shared between main.py (CLI) and app.py (Streamlit).
Call `analyze_frame(frame, estimator, counter)` on every frame.
"""

import cv2
import mediapipe as mp

from rules import (check_back_angle, check_knee_over_toe,
                   check_hip_depth, is_in_squat_position)
from feedback import generate_feedback
from overlay import draw_overlay

PL = mp.solutions.pose.PoseLandmark


def _get_coords(landmarks, idx):
    lm = landmarks[idx]
    return [lm.x, lm.y]


def _pick_side(landmarks):
    """Pick the more visible side of the body."""
    left_vis  = landmarks[PL.LEFT_HIP].visibility
    right_vis = landmarks[PL.RIGHT_HIP].visibility
    return 'LEFT_' if left_vis >= right_vis else 'RIGHT_'


def analyze_frame(frame, estimator, counter):
    """
    Process a single BGR frame.
    Returns annotated frame + dict of analysis results.
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    landmarks = estimator.get_landmarks(rgb)

    result = {
        "landmarks_detected": False,
        "is_correct": False,
        "messages": ["Position yourself in frame"],
        "squat_count": counter.count,
        "knee_angle": 0.0,
        "in_squat": False,
        "back_angle": 0.0,
        "knee_overshoot": 0.0,
    }

    if landmarks:
        result["landmarks_detected"] = True
        prefix = _pick_side(landmarks)

        hip      = _get_coords(landmarks, getattr(PL, prefix + 'HIP'))
        shoulder = _get_coords(landmarks, getattr(PL, prefix + 'SHOULDER'))
        knee     = _get_coords(landmarks, getattr(PL, prefix + 'KNEE'))
        ankle    = _get_coords(landmarks, getattr(PL, prefix + 'ANKLE'))

        in_squat, knee_angle = is_in_squat_position(hip, knee, ankle)
        back_ok,  back_angle = check_back_angle(hip, shoulder)
        knee_ok,  overshoot  = check_knee_over_toe(knee, ankle)
        depth_ok, _          = check_hip_depth(hip, knee)

        is_correct, messages = generate_feedback(back_ok, knee_ok, depth_ok, in_squat)
        squat_count = counter.update(knee_angle)

        result.update({
            "is_correct":     is_correct,
            "messages":       messages,
            "squat_count":    squat_count,
            "knee_angle":     knee_angle,
            "in_squat":       in_squat,
            "back_angle":     back_angle,
            "knee_overshoot": overshoot,
        })

        frame = draw_overlay(
            frame,
            estimator.last_results.pose_landmarks,
            is_correct, messages, frame.shape,
            squat_count=squat_count,
            knee_angle=knee_angle,
            in_squat=in_squat
        )
    else:
        frame = draw_overlay(
            frame, None, False,
            ["Position yourself in frame"],
            frame.shape,
            squat_count=counter.count
        )

    return frame, result