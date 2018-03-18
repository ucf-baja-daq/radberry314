# liquid_crystal_595.py
# Library to interface with LCD through a shift register on Raspberry Pi 3

# import shift register class
from shift_out import shift_out
from time import sleep
import RPi.GPIO as GPIO
from GPIO import OUT
# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# shift register pin addresses
PIN_D4 = 0
PIN_D5 = 1
PIN_D6 = 2
PIN_D7 = 3
PIN_RS = 4
PIN_E = 5

class liquid_crystal_595():
    """class to interface with lcd over shift register"""

    def __init__(self, latch_pin, clock_pin, serial_pin):
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self.serial_pin = serial_pin

        # set up shift register object. Only one daisy chain
        self.shift_reg = shift_out(latch_pin, clock_pin, serial_pin, 1)

        # clear shift register
        self.shift_reg.clear()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        # set up pin outputs
        GPIO.setup(latch_pin, OUT)
        GPIO.setup(clock_pin, OUT)
        GPIO.setup(serial_pin)

        # displayfunction binary
        self.display_function = LCD_4BITMODE

    def begin(self, cols, lines, dotsize):
        """set up lcd dimensions"""

        # only support up to 2 lines
        if (lines > 1):
            display_function |= LCD_2LINE

        # total number of lines
        self.num_lines = lines

        # current line. default 0 (first line)
        self.current_line = 0

        # for some 1 line displays you can select a 10 pixel high font
        if dotsize and lines == 1:
            display_function |= LCD_5x10DOTS

        # see page 45/46 for initialization specification
        # according to datasheet, we need at least 40ms after power rises above 2.7V
        # we'll sleep 50ms
        sleep(0.050)

        # pull RS and E low to begin commands
        self.shift_reg.set(PIN_RS, LOW)
        self.shift_reg.set(PIN_E, LOW)

        # write out shift register
        self.shift_reg.write_out()

        # put lcd into 4bit mode

        # start in 8bit mode, try to set 4bit mode


    def _write4bits(self, value):
        self.shift_reg.set(PIN_D4, value & 1)
        value >>= 1

        self.shift_reg.set(PIN_D5, value & 1)
        value >>= 1

        self.shift_reg.set(PIN_D6, value & 1)
        value >>= '

        self.shift_reg.set(PIN_D7, value & 1)

        self.pulse_enable()

    def _pulse_enable(self):
        'self.shift_reg.set(PIN_E)
