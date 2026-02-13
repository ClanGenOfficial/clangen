import time
from threading import Timer


class AudioTimer(Timer):
    """
    A subclass of python's threading timer that includes new methods for finding elapsed and remaining time
    """

    started_at = None

    def start(self):
        self.started_at = time.time()
        super().start()

    @property
    def elapsed(self):
        return time.time() - self.started_at

    @property
    def remaining(self):
        return self.interval - self.elapsed
