# liquid_crystal_595.py
# Library to interface with LCD through a shift register on Raspberry Pi 3

# import shift register class
from shift_out import shift_out
import liquid_crystal_const

# shift register pin addresses
ENABLE_PIN = 0b00000001
RS_PIN = 0b10000000
LED1_PIN = 0b00100000
LED2_PIN = 0b01000000
DATABITS = 0b00011110
PIN_D4 = 0b00010000
PIN_D5 = 0b00001000
PIN_D6 = 0b00000100
PIN_D7 = 0b00000010

class liquid_crystal_595():
    """class to interface with lcd over shift register"""

    def __init__(self, latch_pin, clock_pin, serial_pin):
        # set up shift register object. Only one daisy chain
        self.sr = shift_out(latch_pin, clock_pin, serial_pin, 1)

        # clear shift register
        self.sr.clear()
