# import docstring


# class DQ:
#     """Data Queue"""

#     isBeingAccessed = False

#     def __init__(self, chunkSize):
#         self.chunk_size = chunkSize
#         self.queue = []

#     def push(data):
#         # Expects some data as array or item

#     def pop():

#     def pop(n):


from multiprocessing import Pipe, Process
import sys

MAX_POLLING_TIMEOUT = sys.maxsize


class Dq:
    """Data Queue class"""

    def __init__(self, onData):
        self._consumer, self._producer = Pipe()
        self.ondata = onData
        self.enablepolling()

    def hworld(self):
        """Hello world"""
        print('Hello world from dq')

    def push(self, data):
        """
        Push data to shared pipe.
        If data is an array, push data points individually.
        """

        if isinstance(data, list) is True:
            print('sending data point[s]')
            for i, data_point in enumerate(data):
                self._producer.send(data_point)
        else:
            print('sending data point')
            self._producer.send(data)

    def poll(self, timeout_in_seconds):
        """
        Poll shared pipe for data.
        _consumer.poll is blocking, indicate max timeout to block until new
        data is found.
        """

        while self.shouldpoll is True:
            if self._consumer.poll(timeout_in_seconds) is True:
                data_point = self._consumer.recv()
                print('data ' + data_point)
                self.ondata(data_point)
            else:
                print('no new data')

    def enablepolling(self):
        """Set semaphore positive for polling. Start polling pipe for data."""
        self.shouldpoll = True

    def disablepolling(self):
        """Set semaphore negative for polling."""
        self.shouldpoll = False
