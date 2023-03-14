class BufferedStreamDuplexer:
    def __init__(self, first_stream, second_stream):
        self.firstStream = first_stream
        self.secondStream = second_stream

    def write(self, data):
        self.firstStream.write(data)
        self.secondStream.write(data)

    def flush(self):
        self.firstStream.flush()
        self.secondStream.flush()


class UnbufferedStreamDuplexer:
    def __init__(self, first_stream, second_stream):
        self.firstStream = first_stream
        self.secondStream = second_stream

    def write(self, data):
        self.firstStream.write(data)
        self.firstStream.flush()
        self.secondStream.write(data)
        self.secondStream.flush()

    def flush(self):
        pass
