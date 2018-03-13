# 74HC595.py
# 74HC595 Shift Register Library
# For Raspberry Pi 3 and Python3

import logging
import RPi.GPIO as GPIO
from RPi.GPIO import HIGH, LOW, BOARD

class shift_out():
    """Used to interface with 74HC595 shift register on Raspberry Pi"""
    def __init__(self, latch_pin, clock_pin, serial_pin, number_of_registers):
        # shift register control pins
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self.serial_pin = serial_pin

        # number of shift registers controlled by 3 pins above
        self.number_of_registers = number_of_registers

        # binary number that holds the HIGH or LOW state of each
        # shift register pin - most significant (rightmost) digit
        # corresponds to pin 1
        self.register = 0

        # setup pin binary values - used to alter specific values in self.register
        self.pins = [0] * 8 * self.number_of_registers
        for i in range(8 * self.number_of_registers):
            self.pins[i] = 2 ^ i

        # set all registers to default value of self.register above
        self.write_out()

    def write_out(self):
        """latch values in self.register to shift register and output"""
        logging.debug("writing {:b} to register".format(self.register))
        # create binary list from desired output
        # bin() creates a number '0b101010' - need to read from 3rd digit for actual number
        raw_bits = [int(i) for i in bin(self.register)[2:]]

        # make output most significant digit first
        out_bits = [0 for i in range(8 * self.number_of_registers)]
        for i in range(1, len(raw_bits) + 1):
            out_bits[-i] = raw_bits[-i]

        # set latch low to begin writing
        GPIO.output(self.latch_pin, LOW)

        # send bits to shift register
        # most significant digit first
        for bit in out_bits:
            # set output value
            GPIO.output(self.serial_pin, bit)

            # pull pulse clock high to write
            GPIO.output(self.clock_pin, HIGH)

            # pull serial low for next write
            GPIO.output(self.serial_pin, LOW)

            # pull clock low for next write
            GPIO.output(self.clock_pin, LOW)

        # set latch high to latch values to register
        GPIO.output(self.latch_pin, HIGH)

    def set(self, index, value):
        """Set the value of a specified pin in self.register"""
        logging.debug("Setting register {:d} to {:d}".format(index + 1, value))
        if value:
            self.register |= self.pins[index]
        else:
            self.register &= ~self.pins[index]

    def clear(self):
        """Set all shift register outputs LOW"""
        logging.debug("Setting all registers LOW.")
        for i in range(8 * self.number_of_registers):
            self.set(i, LOW)
        self.write_out()

    def set_all(self):
        """Set all shift register outputs HIGH"""
        logging.debug("Setting all registers HIGH.")
        for i in range(8 * self.number_of_registers):
            self.set(i, HIGH)
        self.write_out()
