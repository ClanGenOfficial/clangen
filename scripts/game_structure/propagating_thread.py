from threading import Thread
from time import time


class PropagatingThread(Thread):
    """Thread that catched any exceptions and re-raised them when .join is called.
    Heavily barrowed from https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread
    """

    def start(self) -> None:
        self.start_time = time()

        return super().start()

    def run(self):
        self.exc = None
        try:
            self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    def join(self, timeout=None):
        super(PropagatingThread, self).join(timeout)
        if self.exc:
            raise self.exc
        return self.ret

    def get_time_from_start(self):
        """Returns the time since the tread started"""
        return time() - self.start_time
