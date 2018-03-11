import logging

import RPi.GPIO as GPIO
from RPi.GPIO import HIGH, LOW, IN, PUD_UP
from time import sleep, asctime, time, localtime

class hall_sensor():
    """read data from a hall sensor on a Raspberry Pi 3"""

    def __init__(self, pin, pull_up, number_of_magnets, file_path):
        logging.info("Setting up {} hall sensor on pin {}".format(pull_up * "pulled up", pin))

        # Raspberry Pi pin that hall sensor is connected to
        self.pin = pin

        # set up Raspberry Pi pin
        if pull_up == 0:
            GPIO.setup(pin, IN, pull_up_down=PUD_UP)
        else:
            GPIO.setup(pin, IN)

        # number of magnets on rotating element
        self.number_of_magnets = number_of_magnets

        # set up data file to write to
        # make unique by using current time
        self.local_time = str(asctime(localtime(time()))).replace(" ", "_")
        self.file_name = str(file_path) + "_" + str(pin) + "_" local_time + ".csv"
        self.data_file = open(self.file_str, "w")

        logging.info("Writing to {}".format(file_name))

        # flag to control running loop
        self.run_flag = 0

        # variable to hold current rpm
        self.rpm = 0

    def collect_rpm():
        """collect hall sensor data and write to file"""

        logging.info("Collecting data from hall sensor on pin {}".format(self.pin))

        # timing variables
        t1 = time()
        t2 = 0
        start_time = time()

        # flag to indicate magnet is passing sensor
        passing_flag = False

        while self.run_flag:
            # read hall sensor pin
            input = GPIO.input(self.pin)

            # determine time since start
            current_time = time() - start_time

            if input = HIGH and passing_flag = False:
                # magnet has just entered sensor range

                # set passing flag true so program doesn't read magnet until next pass
                passing_flag = True

                # record elapsed time from last pass
                t1 = t2 # put last time in t1
                t2 = time() # put current time in t2

                # calculate time since last magnet pass
                elapsed_time = t2 - t1

                # calculate current rpm
                self.rpm = 60 / number_of_magnets / elapsed_time

                # write data point to file
                self.data_file.write(",".join([current_time, self.rpm]))
                self.data_file.flush()

            elif input = LOW and passing_flag = True:
                # magnet has just left sensor range

                # set passing_flag false so program reads next magnet pass
                passing_flag = False

        def set_flag(self, flag):
            """Set running flag false to end loop"""
            self.run_flag = flag

        def close_file(self):
            """Close file"""
            self.data_file.flush()
