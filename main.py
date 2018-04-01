###############
### IMPORTS ###
###############

# python libraries
import logging as log
from time import sleep, strftime

# import bajadaq classes
from bajadaq.dependencies.HallSensor import HallSensor
from bajadaq.dependencies.LCDShift import LCDShift
from bajadaq.dependencies.LIS3DH import LIS3DH
from bajadaq.dependencies.ShiftIn import ShiftIn
from bajadaq.dependencies.ShiftOut import ShiftOut

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
log_filename = "log_" + strftime("%Y-%m-%d--%H-%M-%S") + ".txt"

# setup log filename and default log level
log.basicConfig(filename=log_filename, level=log.DEBUG)


## Shift Registers ##

# set up shift register objects
led_shift = ShiftOut(pin.SO2_LATCH, pin.SO2_CLOCK, pin.SO2_SERIAL, 1)
input = ShiftIn(pin.SI_LATCH, pin.SI_CLOCK, pin.SI_SERIAL, 1)


## Program Variables ##

# main loop flag
main_flag = True

# start toggle configuration flag
start_tog_flag = True
start_tog_message_flag = True



#################
### MAIN LOOP ###
#################

if __name__ == "__main__":
    while main_flag:
        # check shift register inputs
        input.read()

        # if any of main collection toggles (hall, vibration, strain) are on on program start, problems could occur.
        # make user turn off main toggle switches in order for program to run.
        if start_tog_flag:
            # if any main toggle switch is on
            if input.state_array[pin.IN_HALL] or input.state_array[pin.IN_STRAIN] or input.state_array[pin.IN_VIBR]:
                # inform user to turn main collection toggles OFF
                # when flag is false, do nothing
                if start_tog_message_flag:
                    # log error
                    log.error("One or more main collection toggles are in ON position. Waiting for user to turn all toggle switches off.")

                    # TODO: display message on LCD

                    # set flag false so error only displays once
                    start_tog_message_flag = False

            else:
                # all toggle switches are off, program can continue
                # if error message was displayed, log that error was resolved. otherwise do nothing
                if not start_tog_message_flag
                    # flag was tripped, error is resolved
                    log.info("Toggles have moved to OFF position. Program can now start.")

                # flip start_tog_flag
                start_tog_flag = False

        else:
            # start_tog_flag flips if the toggles are set to the correct position
            # now the main functions can start

            log.info("Program start.")

            # check whether system is in calibration mode or in data collection mode based on calibration toggle switch
            if input.state_array[pin.IN_CAL]:
                # system is in calibration mode

                log.info("System is in calibration mode.")

                # check main toggle switches
                if input.state_array[pin.IN_HALL]:
                    # hall sensor toggle is on

                    log.info("Hall toggle switch ON. Displaying hall sensor states.")

                    # TODO: display value of hall sensors for verification

                if input.state_array[pin.IN_STAIN]:
                    # strain gauge toggle is on

                    log.info("Strain toggle switch ON. Calibrating strain gauges.")

                    # TODO: use buttons to zero/calibrate strain gauges

                if input.state_array[pin.IN_VIBR]:
                    # arm vibration toggle is on

                    log.info("Vibration toggle swith ON. Calibrating encoders.")

                    # TODO: use buttons to zero/calibrate encoders

            else:
                # system is in data collection mode

                log.info("System is in data collection mode.")

                # check main toggle switches
                if input.state_array[pin.IN_HALL]:
                    # hall sensor toggle is on

                    log.info("Hall toggle switch ON. Collecting RPM data.")

                    # TODO: collect rpm data from hall sensors

                if input.state_array[pin.IN_STAIN]:
                    # strain gauge toggle is on

                    log.info("Strain toggle switch ON. Collecting strain data.")

                    # TODO: collect arm deflection data from strain gauges

                if input.state_array[pin.IN_VIBR]:
                    # arm vibration toggle is on

                    log.info("Vibration toggle swith ON. Collecting arm vibration data.")

                    # TODO: collect vibration data from angular encoder
