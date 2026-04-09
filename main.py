"""
main.py
-------
CLI entry point. Supports webcam and video file input.

Usage:
    python main.py                        # webcam
    python main.py --source video.mp4     # video file
    python main.py --source 0             # explicit webcam index
"""

import argparse
import cv2

from pose_estimator import PoseEstimator
from counter import SquatCounter
from analyzer import analyze_frame


def run(source):
    # Accept integer camera index or file path
    try:
        source = int(source)
    except (ValueError, TypeError):
        pass  # keep as string path

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {source}")
        return

    estimator = PoseEstimator()
    counter   = SquatCounter()

    print("[INFO] Running — press Q to quit, R to reset counter.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of stream.")
            break

        frame, result = analyze_frame(frame, estimator, counter)

        cv2.imshow("Squat Analyzer", frame)
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            counter.reset()
            print("[INFO] Counter reset.")

    cap.release()
    cv2.destroyAllWindows()
    print(f"[DONE] Total squats counted: {counter.count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Squat Analyzer — CLI")
    parser.add_argument("--source", default=0,
                        help="Camera index (0) or path to video file")
    args = parser.parse_args()
    run(args.source)