import numpy as np

def compute_angle(a, b, c):
    """Angle at point b, formed by vectors b→a and b→c."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

def check_back_angle(hip, shoulder, threshold=35):
    """
    Compute angle of hip→shoulder vector from vertical.
    Uses a vertical reference point directly above the hip.
    Returns (passed: bool, angle: float)
    """
    vertical_ref = [hip[0], hip[1] - 0.1]  # point directly above hip
    angle = compute_angle(shoulder, hip, vertical_ref)
    return angle <= threshold, angle

def check_knee_over_toe(knee, ankle, tolerance=0.05):
    """
    In a side-on view, knee x should not exceed ankle x by more than tolerance.
    Returns (passed: bool, overshoot: float)
    """
    overshoot = knee[0] - ankle[0]
    return overshoot <= tolerance, overshoot

def check_hip_depth(hip, knee, tolerance=0.02):
    """
    Hip y should be >= knee y (image y increases downward).
    Only checked if the person appears to be in the squat position.
    Returns (passed: bool, delta: float)
    """
    delta = hip[1] - knee[1]
    return delta >= -tolerance, delta

def is_in_squat_position(hip, knee, ankle, threshold=120):
    """Check if the person is in a squat position based on knee angle."""
    knee_angle = compute_angle(hip, knee, ankle)
    return knee_angle < threshold, knee_angle