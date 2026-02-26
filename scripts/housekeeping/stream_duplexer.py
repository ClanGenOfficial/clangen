from scripts.housekeeping.noop_writer import NoopWriter


class BufferedStreamDuplexer:
    def __init__(self, first_stream, second_stream, noop_writer_fallback=True):
        self.firstStream = first_stream
        self.secondStream = second_stream

        if noop_writer_fallback:
            if self.firstStream is None:
                self.firstStream = NoopWriter()
            if self.secondStream is None:
                self.secondStream = NoopWriter()

    def write(self, data):
        self.firstStream.write(data)
        self.secondStream.write(data)

    def flush(self):
        self.firstStream.flush()
        self.secondStream.flush()


class UnbufferedStreamDuplexer:
    def __init__(self, first_stream, second_stream, noop_writer_fallback=True):
        self.firstStream = first_stream
        self.secondStream = second_stream

        if noop_writer_fallback:
            if self.firstStream is None:
                self.firstStream = NoopWriter()
            if self.secondStream is None:
                self.secondStream = NoopWriter()

    def write(self, data):
        self.firstStream.write(data)
        self.firstStream.flush()
        self.secondStream.write(data)
        self.secondStream.flush()

    def flush(self):
        pass
