###############
### IMPORTS ###
###############

# python libraries
import logging
import logging.handlers
from time import sleep, strftime
import multiprocessing as mp

# import bajadaq classes
from bajadaq.HallSensor import HallSensor
from bajadaq.LCDShift import LCDShift
from bajadaq.LIS3DH import LIS3DH
from bajadaq.ShiftIn import ShiftIn
from bajadaq.ShiftOut import ShiftOut
from bajadaq.writer import writer

# import pin numbers
import pin

# import rasINerry pi stuff
import RPi.GPIO as GPIO
from RPi.GPIO import IN, OUT, HIGH, LOW, BOARD

# setup RPi
GPIO.setwarnings(False)
GPIO.setmode(BOARD)

#############
### SETUP ###
#############

## Logging ##

# Logging Levels:
    # -DEBUG: Detailed information, typically of interest only when diagnosing problems.
    # -INFO: Confirmation that things are working as expected.
    # -WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
    # -ERROR: Due to a more serious problem, the software has not been able to perform some function.
    # -CRITICAL: A serious error, indicating that the program itself may be unable to continue running.

# make log filename based on current time and date
log_filename = "logs/log_" + strftime("%Y-%m-%d--%H-%M-%S") + ".txt"

# setup log
# file logs all
# only INFO and above to console
logger = logging.getLogger(__name__)
log_file_handler = logging.FileHandler(log_filename)
log_stream_handler = logging.StreamHandler()
log_formatter = logging.Formatter("(%(asctime)s)%(processName)s-%(levelname)s: %(message)s")

log_file_handler.setFormat(log_formatter)
log_stream_handler.setFormat(log_formatter)

log_file_handler.setLevel(logging.DEBUG)
log_stream_handler.setLevel(logging.INFO)

logger.addHandler(log_file_handler)
logger.addHandler(log_stream_handler)


## Shift Registers ##

# set up shift register objects
led_shift = ShiftOut(pin.SO2_LATCH, pin.SO2_CLOCK, pin.SO2_SERIAL, 1)
input = ShiftIn(pin.SI_LATCH, pin.SI_CLOCK, pin.SI_SERIAL, 1)


## Program Variables ##

# main loop flag
main_flag = True

# start toggle configuration flag
start_tog_flag = True

# data collection flag
hall_flag = False
strain_flag = False
vibr_flag = False

# log flags
main_loop_log = True

# log flagn
cal_mode_log = True
cal_hall_log = True
cal_strain_log = True
cal_vibr_log = True
data_mode_log = True
data_hall_log = True
data_strain_log = True
data_vibr_log = True
start_tog_log = True



#################
### MAIN LOOP ###
#################

# if called as main process
if __name__ == "__main__":
    logger.debug("Enter main program")

    while main_flag:
        # initial log message
        if main_loop_log:
            logger.debug("Enter main loop. main_flag == {}".format(main_flag))

            # set flag false so message is only logged once
            main_loop_log = False

        # check shift register inputs
        input.read()

        # if any of main collection toggles (hall, vibration, strain) are on on program start, problems could occur.
        # make user turn off main toggle switches in order for program to run.
        if start_tog_flag:
            # check if any main toggle switch is on
            if input.state_array[pin.IN_HALL] or input.state_array[pin.IN_STRAIN] or input.state_array[pin.IN_VIBR]:
                # inform user to turn main collection toggles OFF
                # when flag is false, do nothing
                if start_tog_log:
                    # log error
                    logger.error("One or more main collection toggles are in ON position. Waiting for user to turn all toggle switches off.")

                    # TODO: display message on LCD

                    # set flag false so error only displays once
                    start_tog_log = False

            else:
                # all toggle switches are off, program can continue
                # if error message was displayed, log that error was resolved. otherwise do nothing
                if not start_tog_log:
                    # flag was tripped, error is resolved
                    logger.info("Toggles have moved to OFF position. Program can now start.")

                # flip start_tog_flag
                start_tog_flag = False

        else:
            # start_tog_flag flips if the toggles are set to the correct position
            # now the main functions can start

            logger.info("Main toggles switches are OFF. Main program start.")

            # check whether system is in calibration mode or in data collection mode based on calibration toggle switch
            if input.state_array[pin.IN_CAL]:
                # system is in calibration mode

                if cal_mode_log:
                    logger.info("System is in calibration mode.")

                    # set flags to display data collection next toggle switch
                    data_mode_log = True
                    cal_mode_log = False


                # check main toggle switches

                # hall sensor calibration
                if input.state_array[pin.IN_HALL]:
                    # hall sensor toggle is on

                    if cal_hall_log:
                        logger.info("Enter hall sensor calibration.")

                        # set log false so it only displays once
                        cal_hall_log = False

                    # TODO: display value of hall sensors for verification

                elif not (input.state_array(pin.IN_HALL) and cal_hall_log):
                    logger.info("Exit hall sensor calibration.")

                    # set log true for next toggle switch
                    cal_hall_log = True


                # strain gauge calibration
                if input.state_array[pin.IN_STAIN]:
                    # strain gauge toggle is on

                    if cal_strain_log:
                        logger.info("Enter strain gauge calibration.")

                        # set log false so it only displays once
                        cal_strain_log = False

                    # TODO: use buttons to zero/calibrate strain gauges

                elif not (input.state_array(pin.IN_STAIN) and cal_strain_log):
                    logger.info("Exit strain gauge calibration.")

                    # set log true for next toggle switch
                    cal_strain_log = True


                # encoder calibration
                if input.state_array[pin.IN_VIBR]:
                    # arm vibration toggle is on

                    if cal_vibr_log:
                        logger.info("Enter encoder calibration.")

                        # set log false so it only displays once
                        cal_vibr_log = False

                    # TODO: use buttons to zero/calibrate encoders

                elif not (input.state_array(pin.IN_VIBR) and cal_vibr_log):
                    logger.info("Exit encoder calibration.")

                    # set log true for next toggle switch
                    cal_vibr_log = True

            # otherwise, system is in data collection mode
            else:
                # system is in data collection mode
                if data_mode_log:
                    logger.info("System is in data collection mode.")

                    # set flags to display calibration next toggle switch
                    data_mode_log = False
                    cal_mode_log = True

                # check main toggle switches

                # hall sensor data collection
                if input.state_array[pin.IN_HALL] and not hall_flag:
                    # hall sensor toggle is on
                    hall_flag = True

                    # log event
                    if data_hall_log:
                        logger.info("Begin hall sensor data collection.")

                        data_hall_log = False

                    # get local time for filename
                    local_time = strftime("%Y-%m-%d--%H-%M-%S")

                    # create file names
                    hall_file_primary = "/home/pi/daq/data/hall_" + local_time + "_primary" + ".csv"
                    hall_file_secondary = "/home/pi/daq/data/hall_" + local_time + "_secondary" + ".csv"

                    # writer pipe communication channels
                    hall_send_primary, hall_rec_primary = mp.Pipe()
                    hall_send_secondary, hall_rec_secondary = mp.Pipe()

                    # create writer processes
                    hall_writer_primary = mp.Process(target=writer, args=(hall_rec_primary,hall_file_primary,1,))
                    hall_writer_secondary = mp.Process(target=writer, args=(hall_rec_secondary,hall_file_secondary,1,))

                    hall_writer_primary.name = "PrimaryHallWriterProcess"
                    hall_writer_secondary.name = "SecondaryHallWriterProcess"

                    # create two hall sensor objects
                    # TODO make number of magnets a variable
                    hall_primary = HallSensor(pin.HALL_SEN_PRIMARY, 1, "primary", hall_writer_primary, hall_send_primary, log_file_handler, log_stream_handler)
                    hall_secondary = HallSensor(pin.HALL_SEN_SECONDARY, 3, "secondary", hall_writer_secondary, hall_send_secondary, log_file_handler, log_stream_handler)

                    # create hall sensor collection processes
                    hall_collect_primary = mp.Process(target=hall_primary.run, args=())
                    hall_collect_secondary = mp.Process(target=hall_secondary.run, args=())

                    hall_collect_primary.name = "PrimaryHallCollectorProcess"
                    hall_collect_secondary.name = "SecondaryHallCollectorProcess"

                    # begin hall sensor writer processes
                    hall_writer_primary.start()
                    hall_writer_secondary.start()

                    # begin hall sensor collection processes
                    hall_collect_primary.start()
                    hall_collect_secondary.start()

                    # TODO send hall sensor speed to seven segment display
                    # TODO add logging messages in writer and HallSensor

                elif not input.state_array[pin.IN_HALL] and hall_flag:
                    logger.info("End hall sensor data collection.")

                    hall_flag = False
                    data_hall_log = True

                    # end collection
                    hall_primary.set_flag(False)
                    hall_secondary.set_flag(False)

                    hall_writer_primary.join()
                    hall_writer_secondary.join()

                    hall_collect_primary.join()
                    hall_collect_secondary.join()


                # strain gauge data collection
                if input.state_array[pin.IN_STRAIN] and not strain_flag:
                    # strain gauge toggle is on
                    strain_flag = True

                    if data_strain_log:
                        logger.info("Begin strain gauge data collection.")

                        data_strain_log = False

                    # TODO: collect arm deflection data from strain gauges

                elif not input.state_array[pin.IN_STRAIN] and strain_flag:
                    logger.info("End strain gauge data collection")

                    strain_flag = False
                    data_strain_log = True


                # encoder vibration data collection
                if input.state_array[pin.IN_VIBR] and not vibr_flag:
                    # arm vibration toggle is on
                    vibr_flag = True

                    if data_vibr_log:
                        logger.info("Begin encoder vibration data collection.")

                        data_vibr_log = False

                    # TODO: collect vibration data from angular encoder

                elif not input.state_array[pin.IN_VIBR] and vibr_flag:
                    logger.info("End encoder vibration data collection")

                    vibr_flag = False
                    data_vibr_log = True
