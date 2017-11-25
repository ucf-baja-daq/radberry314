class ChunkedFileIOQ:
    """Write to disk in a chunked fashion."""
    buf = []
    overflow = []

    def __init__(self, file_path, chunk_size, header_values):
        self.chunk_size = chunk_size
        self.file_path = file_path
        self.buf_is_locked = False
        self.header_values = header_values
        self.resetBuffersWithHeaders()

    def _write(self):
        """Force a write to disk and flush buffer"""
        with open(self.file_path, 'w') as file_out:
            file_out.write(joinDataPoints(self.buf))

    def push(self, data_point):
        """Push data to data buffer"""
        # print('buffer length [%d], chunk size [%d]' %
        #   (len(self.buf), self.chunk_size))
        if self.buf_is_locked is True:
            # print('buffer is locked')
            self.overflow.append(data_point)
            return

        # print('buffer not locked')
        self.buf.append(data_point)
        if len(self.buf) == self.chunk_size:
            self._write()
            self.resetBuffers()
        else:
            print('%d /= %d' % (len(self.buf), self.chunk_size))

    def resetBuffersWithHeaders(self):
        self.buf_is_locked = True
        self.buf = self.header_values
        for overflowval in self.overflow:
            self.buf.append(overflowval)
        self.overflow = []
        self.buf_is_locked = False

    def resetBuffers(self):
        self.buf_is_locked = True
        self.buf = self.overflow
        self.overflow = []
        self.buf_is_locked = False

    def _flush(self):
        """Flush data buffer"""
        self.buf = []

    # self.writeAsync(self, data_points, lambda:
    #     self.buf = self.overflow
    #     self.overflow = []
    #     self.buf_is_locked = False
    # )
    # def writeAsync(self, data_points, callback):
        # write then callback


def joinArrayToString(array, delimiter):
    """Join array to string"""
    return delimiter.join([str(val) for val in array])


def joinDataPoints(data_points):
    """
    Join items in an array into a string on a comma delimiter.
    End new string with new line character
    """
    print(data_points)
    for row_index in range(0, len(data_points) - 1):
        data_points[row_index] = joinArrayToString(
            data_points[row_index],
            ','
        )
    return joinArrayToString(data_points, ',\n')
