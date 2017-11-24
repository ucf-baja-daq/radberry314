from multiprocessing import Process, Pipe
import time
from components.dq import Dq
from components.fileio import ChunkedFileIOQ

NUM_TIME_POINTS_PER_LINE = 1
NUM_DATA_POINTS_PER_LINE = 7
NUM_DATA_ENTRIES_PER_LINE = NUM_TIME_POINTS_PER_LINE + NUM_DATA_POINTS_PER_LINE
NUM_ROWS_PER_WRITE = 1000
CHUNK_SIZE = NUM_ROWS_PER_WRITE * NUM_DATA_ENTRIES_PER_LINE
POLLS_PER_SECOND = 50000
POLL_TIMEOUT = 1 / POLLS_PER_SECOND
HALL_DIR = '/data/hall'


def readFromInputs(dataq):
    while True:
        dataq.push('// jake was here //')
        time.sleep(1 / 500)


def shutdown():
    consumer_proc.terminate()
    producer_proc.terminate()


def createOnData(chunkedIo):
    return lambda data: chunkedio.push(data)


def ondata(data):
    """Do something when new data is seen"""
    chunkedio.push(data)


if __name__ == '__main__':
    localtime = time.asctime(time.localtime(time.time()))
    localtimeStr = str(localtime).replace(" ", "_")
    file_path = HALL_DIR + '/1' + localtimeStr + ".csv"
    chunkedio = ChunkedFileIOQ(file_path, CHUNK_SIZE)
    dq = Dq(ondata)

    consumer_conn, producer_conn = Pipe()
    consumer_proc = Process(target=dq.poll, args=(POLL_TIMEOUT,))
    producer_proc = Process(target=readFromInputs, args=(dq,))
    consumer_proc.start()
    producer_proc.start()
    time.sleep(3)
    shutdown()
