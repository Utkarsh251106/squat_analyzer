import mediapipe as mp


class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )
        self.last_results = None

    def get_landmarks(self, frame_rgb):
        results = self.pose.process(frame_rgb)
        self.last_results = results
        if results.pose_landmarks:
            return results.pose_landmarks.landmark
        return None