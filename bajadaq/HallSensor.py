import logging

import RPi.GPIO as GPIO
from RPi.GPIO import HIGH, LOW, IN, PUD_UP
from time import time, sleep, strftime
from multiprocessing import Process, Pipe

# setup RPi
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class HallSensor():
    """read data from writer_comm hall sensor on writer_comm Raspberry Pi 3"""

    def __init__(self, pin, number_of_magnets, identifier, writer, writer_comm, log_file_handler, log_stream_handler):
        # set up log using handlers from main process
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(log_file_handler)
        self.logger.addHandler(log_stream_handler)

        self.logger.info("Setting up hall sensor on pin {}".format(pin))

        # Raspberry Pi pin that hall sensor is connected to
        self.pin = pin

        # set up Raspberry Pi pin
        GPIO.setup(pin, IN, pull_up_down=PUD_UP)

        # number of magnets on rotating element
        self.number_of_magnets = number_of_magnets

        self.writer_comm = writer_comm

        self.writer = writer

        # flag to control running loop
        self.run_flag = 1

        # variable to hold current rpm
        self.rpm = 0

    def run(self):
        """collect hall sensor data and write to file"""

        self.logger.info("Collecting data from hall sensor on pin {}".format(self.pin))

        # timing variables
        t1 = time()
        t2 = 0
        start_time = time()
        input = 0

        # flag to indicate magnet is passing sensor
        passing_flag = False

        while self.run_flag:
            # read hall sensor pin
            input = not GPIO.input(self.pin)

            # determine time since start
            current_time = time() - start_time

            if input == HIGH and passing_flag == False:
                # magnet has just entered sensor range

                # set passing flag true so program doesn't read magnet until next pass
                passing_flag = True

                # record elapsed time from last pass
                t1 = t2 # put last time in t1
                t2 = time() # put current time in t2

                # calculate time since last magnet pass
                elapsed_time = t2 - t1

                # calculate current rpm
                self.rpm = 60 / self.number_of_magnets / elapsed_time

                logger.

                # write data point to file
                self.writer_comm.send(','.join([str(current_time), str(self.rpm)]) + "\n")
                print(','.join([str(current_time), str(self.rpm)]))

            elif input == LOW and passing_flag == True:
                # magnet has just left sensor range

                # set passing_flag false so program reads next magnet pass
                passing_flag = False

        self.writer_comm.send("c")
        self.writer_comm.close()

        def set_flag(self, flag):
            """Set running flag false to end loop"""
            self.run_flag = flag
