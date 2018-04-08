###############
### IMPORTS ###
###############

# python libraries
import logging as log
from time import sleep, strftime
import multiprocessing as mp
from bajadaq.writer import writer

# import bajadaq classes
from bajadaq.HallSensor import HallSensor

# import pin numbers
import pin

# import rasINerry pi stuff
import RPi.GPIO as GPIO
from RPi.GPIO import IN, OUT, HIGH, LOW, BOARD

# setup RPi
GPIO.setwarnings(False)
GPIO.setmode(BOARD)


# make log filename based on current time and date
log_filename = "logs/hall_log_" + strftime("%Y-%m-%d--%H-%M-%S") + ".txt"

# setup log filename and default log level
log.basicConfig(filename=log_filename, level=log.DEBUG)

local_time = strftime("%Y-%m-%d--%H-%M-%S")
file_name1 = "/home/pi/daq/data/" + local_time + "primary" + ".csv"
file_name2 = "/home/pi/daq/data/" + local_time + "secondary" + ".csv"

# writer processes
a1, b1 = mp.Pipe()
a2, b2 = mp.Pipe()

w1 = mp.Process(target=writer, args=(b1,file_name1,1,))

w2 = mp.Process(target=writer, args=(b2,file_name2,1,))

# create two hall sensor processes
hall_primary = HallSensor(8, 0, 1, "primary", w1, a1)

hall_secondary = HallSensor(10, 0, 3, "secondary", w2, a2)

hall_primary_run = mp.Process(target=hall_primary.collect_rpm, args=())

hall_secondary_run = mp.Process(target=hall_secondary.collect_rpm, args=())



try:
    w1.start()
    w2.start()

    hall_primary_run.start()
    hall_secondary_run.start()

except KeyboardInterrupt:
    hall_primary.set_flag(False)
    hall_secondary.set_flag(False)

    w1.join()
    w2.join()

    sleep(2)

    hall_primary_run.join()
    hall_secondary_run.join()
