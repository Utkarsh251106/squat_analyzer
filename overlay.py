import cv2
import mediapipe as mp


def draw_overlay(frame, pose_landmarks, is_correct, feedback_msgs, frame_shape,
                 squat_count=0, knee_angle=0, in_squat=False):
    h, w = frame_shape[:2]
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Draw skeleton
    if pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(0, 180, 180), thickness=2)
        )

    # ── Feedback panel (top-left) ──────────────────────────────────────────────
    panel_color = (30, 180, 30) if is_correct else (30, 30, 200)
    cv2.rectangle(frame, (10, 10), (420, 30 + len(feedback_msgs) * 34), (20, 20, 20), -1)
    cv2.rectangle(frame, (10, 10), (420, 30 + len(feedback_msgs) * 34), panel_color, 2)

    y_offset = 40
    for msg in feedback_msgs:
        prefix = "✓  " if is_correct else "✗  "
        cv2.putText(frame, prefix + msg, (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, panel_color, 2, cv2.LINE_AA)
        y_offset += 34

    # ── Squat counter (top-right) ──────────────────────────────────────────────
    counter_x = w - 180
    cv2.rectangle(frame, (counter_x, 10), (w - 10, 100), (20, 20, 20), -1)
    cv2.rectangle(frame, (counter_x, 10), (w - 10, 100), (200, 160, 30), 2)
    cv2.putText(frame, "SQUATS", (counter_x + 20, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 140, 20), 1, cv2.LINE_AA)
    cv2.putText(frame, str(squat_count), (counter_x + 55, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 220, 50), 3, cv2.LINE_AA)

    # ── Knee angle indicator (bottom-left) ─────────────────────────────────────
    phase = "DOWN" if in_squat else "UP"
    phase_color = (50, 200, 255) if in_squat else (200, 200, 200)
    cv2.rectangle(frame, (10, h - 70), (260, h - 10), (20, 20, 20), -1)
    cv2.putText(frame, f"Knee angle: {knee_angle:.1f}°  [{phase}]",
                (18, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, phase_color, 2, cv2.LINE_AA)

    return frame