from multiprocessing import Process, Pipe
import pyadda
from adc_consts import *
import time
import os
from components.dq import Dq
from components.fileio import ChunkedFileIOQ
import RPi.GPIO as GPIO

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


def onData(data):
    """Do something when new data is seen"""
    chunked_file_io.push(data)


def setupADCReader(data_pipe):
    def interruptInterpreter(channel):
        sample_time = time.time() - start_time
        if channel == PIN_DRDY:
            # collect data from ads1256
            pyadda.collectData()
            volts = pyadda.readAllChannelsVolts(adc_channels)
            row = volts
            row.insert(0, sample_time)
            data_pipe.push(row)

    # Wait for DRDY low - indicating data is ready
    GPIO.add_event_detect(PIN_DRDY, GPIO.FALLING,
                          callback=interruptInterpreter)


if __name__ == '__main__':
    # Raspberry pi pin numbering setup
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    PIN_DRDY = 11

    GPIO.setup(PIN_DRDY, GPIO.IN)

    # define gain, sampling rate, and scan mode
    gain = ADS1256_GAIN['1']
    sampling_rate = ADS1256_DRATE['30000']
    scanMode = ADS1256_SMODE['SINGLE_ENDED']

    adc_channels = 8 - 4 * scanMode

    # Setup ads1256 chip
    pyadda.startADC(gain, sampling_rate, scanMode)
    start_time = time.time()

    data_pipe = Dq(onData)
    consumer_conn, producer_conn = Pipe()
    consumer_proc = Process(target=data_pipe.poll, args=(POLL_TIMEOUT,))
    producer_proc = Process(target=setupADCReader, args=(data_pipe,))
    consumer_proc.start()
    producer_proc.start()

    while True:
        pass
