from rules import (compute_angle, check_back_angle,
                   check_knee_over_toe, check_hip_depth,
                   is_in_squat_position)


def test_compute_angle_90_degrees():
    a = [1, 0]
    b = [0, 0]
    c = [0, 1]
    angle = compute_angle(a, b, c)
    assert abs(angle - 90.0) < 0.5


def test_back_angle_pass():
    hip      = [0.5, 0.6]
    shoulder = [0.5, 0.3]   # straight up — small angle
    passed, angle = check_back_angle(hip, shoulder, threshold=35)
    assert passed


def test_back_angle_fail():
    hip      = [0.5, 0.6]
    shoulder = [0.8, 0.4]   # leaning forward
    passed, angle = check_back_angle(hip, shoulder, threshold=35)
    assert not passed


def test_knee_over_toe_pass():
    knee  = [0.5, 0.5]
    ankle = [0.5, 0.7]      # knee not past ankle
    passed, _ = check_knee_over_toe(knee, ankle, tolerance=0.05)
    assert passed


def test_knee_over_toe_fail():
    knee  = [0.7, 0.5]
    ankle = [0.5, 0.7]      # knee well past ankle
    passed, _ = check_knee_over_toe(knee, ankle, tolerance=0.05)
    assert not passed


def test_hip_depth_pass():
    hip  = [0.5, 0.65]
    knee = [0.5, 0.60]      # hip below knee (y increases downward)
    passed, _ = check_hip_depth(hip, knee)
    assert passed


def test_hip_depth_fail():
    hip  = [0.5, 0.40]
    knee = [0.5, 0.60]      # hip above knee — not deep enough
    passed, _ = check_hip_depth(hip, knee)
    assert not passed


def test_is_in_squat_position():
    hip   = [0.5, 0.5]
    knee  = [0.5, 0.7]
    ankle = [0.5, 0.9]
    in_squat, angle = is_in_squat_position(hip, knee, ankle)
    assert isinstance(in_squat, bool)
    assert 0 < angle < 200