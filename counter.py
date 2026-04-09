from collections import deque


class SquatCounter:
    """
    Counts squat repetitions using a state machine.
    States: STANDING -> DOWN -> STANDING (= 1 rep)
    Uses a rolling window to smooth knee angle readings and avoid false triggers.
    """

    def __init__(self, window_size=8, down_threshold=100, up_threshold=150):
        self.count = 0
        self.state = "STANDING"          # STANDING | DESCENDING | DOWN
        self.window = deque(maxlen=window_size)
        self.down_threshold = down_threshold   # knee angle < this = in squat
        self.up_threshold = up_threshold       # knee angle > this = standing

    def update(self, knee_angle):
        """
        Feed a new knee angle reading. Returns current rep count.
        """
        self.window.append(knee_angle)
        if len(self.window) < self.window.maxlen:
            return self.count  # wait for window to fill

        smoothed = sum(self.window) / len(self.window)

        if self.state == "STANDING" and smoothed < self.down_threshold:
            self.state = "DOWN"

        elif self.state == "DOWN" and smoothed > self.up_threshold:
            self.state = "STANDING"
            self.count += 1   # completed one full rep

        return self.count

    def reset(self):
        self.count = 0
        self.state = "STANDING"
        self.window.clear()