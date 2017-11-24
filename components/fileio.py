class ChunkedFileIOQ:
    """Write to disk in a chunked fashion."""
    buf = []
    overflow = []

    def __init__(self, file_path, chunk_size):
        self.chunk_size = chunk_size
        self.file_path = file_path
        self.buf_is_locked = False

    def _write(self):
        """Force a write to disk and flush buffer"""
        with open(self.file_path, 'w') as file_out:
            file_out.write(join_data_points(self.buf))
            self._flush()

    def push(self, data_point):
        """Push data to data buffer"""
        if self.buf_is_locked is True:
            self.overflow.append(data_point)
            return

        self.buf.append(data_point)
        if len(self.buf) is self.chunk_size:
            self.buf_is_locked = True
            self._write()
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


def join_array_to_string(array, delimiter):
    """Join array to string"""
    return delimiter.join(['{val}' for val in array])


def join_data_points(data_points):
    """
    Join items in an array  into a string on a comma delimiter.
    End new string with new line character
    """
    for row_index in range(0, len(data_points) - 1):
        data_points[row_index] = join_array_to_string(
            data_points[row_index],
            ','
        )
    return join_array_to_string(data_points, ',\n')
