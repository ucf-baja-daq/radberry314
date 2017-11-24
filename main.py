# from components import dq, fileio
from components.dq import Dq
from multiprocessing import Process, Pipe


def onData(data):
    print('new data' + data)


# dataqueue = dq.Dq(1000, onData)
# dataqueue.hworld()

# components.dq.test()

# get producer and consumer from dq
# push new data to dq
# get data via consumer
# if a buffer limit is reached in the consumer, write to disk in chunks

NUM_TIME_POINTS_PER_LINE = 1
NUM_DATA_POINTS_PER_LINE = 7
NUM_DATA_ENTRIES_PER_LINE = NUM_TIME_POINTS_PER_LINE + NUM_DATA_POINTS_PER_LINE
NUM_ROWS_PER_WRITE = 1000
CHUNK_SIZE = NUM_ROWS_PER_WRITE * NUM_DATA_ENTRIES_PER_LINE


def send(child_conn):
    print('inside send (child)')
    child_conn.send([42, None, 'hello'])
    # child_conn.close()


def recv(parent_conn):
    print('inside recv (parent)')
    print(parent_conn.recv())   # prints "[42, None, 'hello']"


if __name__ == '__main__':
    _dq = Dq(CHUNK_SIZE, onData)
    _dq.push('//jake was here//')
    # consumer_proc = Process(target=dq., args=(parent_conn,))

    # parent_conn, child_conn = Pipe()
    # print('creating parent')
    # parent = Process(target=recv, args=(parent_conn,))
    # print('creating child')
    # child = Process(target=send, args=(child_conn,))
    # parent.start()
    # print('parent started')
    # child.start()
    # print('child started')
    # # p.join()
