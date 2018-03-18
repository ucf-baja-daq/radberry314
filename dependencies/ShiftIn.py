# CD4021B.py
# CD4021B Shift Register Library
# For Raspberry Pi 3 and Python3

import logging
import RPi.GPIO as GPIO
from RPi.GPIO import HIGH, LOW, BOARD
from time import sleep

class ShiftIn():
    """Used to interface with CD4021B shift register on Raspberry Pi"""
    def __init__(self, latch_pin, clock_pin, serial_pin, number_of_registers):
        # shift register control pins
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self.serial_pin = serial_pin

        # number of shift registers controlled by 3 pins above
        self.number_of_registers = number_of_registers

        # binary number that holds the HIGH or LOW state of each
        self.state = 0

        # array that holds the state of each pin
        self.state_array = [0] * 8 * self.number_of_registers

        # inactive state
        GPIO.output(self.latch_pin, LOW)
        GPIO.output(self.clock_pin, HIGH)

    def read(self):
        """read value of each input pin from shift register"""
        # pulse latch to begin reading
        GPIO.output(self.latch_pin, HIGH)
        sleep(0.00002)
        GPIO.output(self.latch_pin, LOW)

        # move from pin 8 to pin 1 on shift register
        for i in range(self.number_of_registers - 1, -1, -1):
            # set clock low to read data pin
            GPIO.output(self.clock_pin, LOW)

            # check value of data pin and write to proper binary location in state
            if GPIO.input(self.serial_pin):
                self.state |= (1 << i)

            # set clock high for next cycle
            GPIO.output(self.clock_pin, HIGH)

        # put state into an array
        # in this case, a 0 in state will be considered ON (1) in the array
        # it assumes that the input pins are pulled up and active low (for example, a button press will send a LOW signal and will be HIGH otherwise)
        for i in range(8 * self.number_of_registers):
            if ~self.state & (1 << i):
                self.state_array[i] = 1
            else:
                self.state_array[i] = 0
