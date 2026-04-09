def generate_feedback(back_ok, knee_ok, depth_ok, in_squat):
    """
    Generate feedback messages based on rule evaluation results.
    Returns (is_correct: bool, messages: list[str])
    """
    messages = []
    if not back_ok:
        messages.append("Straighten your back")
    if not knee_ok:
        messages.append("Keep knees behind your toes")
    if in_squat and not depth_ok:
        messages.append("Lower your hips further")

    if not messages:
        return True, ["Correct posture"]
    return False, messages