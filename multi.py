from multiprocessing import Process, Pipe
import time
import os
from components.dq import Dq
from components.fileio import ChunkedFileIOQ

NUM_TIME_POINTS_PER_LINE = 1
NUM_DATA_POINTS_PER_LINE = 7
NUM_DATA_ENTRIES_PER_LINE = NUM_TIME_POINTS_PER_LINE + NUM_DATA_POINTS_PER_LINE
NUM_ROWS_PER_WRITE = 100
CHUNK_SIZE = NUM_ROWS_PER_WRITE * NUM_DATA_ENTRIES_PER_LINE
POLLS_PER_SECOND = 10000
POLL_TIMEOUT = 1 / POLLS_PER_SECOND

LOCAL_TIME = time.asctime(time.localtime(time.time()))
LOCAL_TIME_STR = str(LOCAL_TIME).replace(' ', '_').replace(':', '.')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = '1' + LOCAL_TIME_STR + '.csv'
LOCAL_DATA_PATH = 'data/adc'
FILE_PATH = os.path.abspath(os.path.join(LOCAL_DATA_PATH, FILE_NAME))
CSV_HEADERS = [['Time (s)', 'Channel 0', 'Channel 1', 'Channel 2',
                'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6', 'Channel 7']]
chunked_file_io = ChunkedFileIOQ(FILE_PATH, CHUNK_SIZE, CSV_HEADERS)


def readFromInputs(dataq):
    """Read data from ADC inputs"""
    while True:
        dataq.push([0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7])


def shutdown():
    """Terminate processes"""
    consumer_proc.terminate()
    producer_proc.terminate()


def ondata(data):
    """Do something when new data is seen"""
    chunked_file_io.push(data)


if __name__ == '__main__':
    dq = Dq(ondata)

    consumer_conn, producer_conn = Pipe()
    consumer_proc = Process(target=dq.poll, args=(POLL_TIMEOUT,))
    producer_proc = Process(target=readFromInputs, args=(dq,))
    consumer_proc.start()
    producer_proc.start()
    # time.sleep(.5)
    # shutdown()
