# liquid_crystal_595.py
# Library to interface with LCD through a shift register on Raspberry Pi 3

# import shift register class
from shift_out import shift_out
from time import sleep
import RPi.GPIO as GPIO
from GPIO import OUT, HIGH, LOW
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

    #### initialization functions ####
    def __init__(self, latch_pin, clock_pin, serial_pin):
        # set up shift register object. Only one register
        self._shift_reg = shift_out(latch_pin, clock_pin, serial_pin, 1)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        # set up pin outputs
        GPIO.setup(latch_pin, OUT)
        GPIO.setup(clock_pin, OUT)
        GPIO.setup(serial_pin, OUT)

        # display control
        self._display_function = LCD_4BITMODE
        self._display_control = 0
        self._display_mode = 0

        # location control
        self._num_lines = 0
        self._current_line = 0

    def begin(self, cols, lines, dotsize):
        """set up lcd dimensions"""

        # only support up to 2 lines
        if (lines > 1):
            self._display_function |= LCD_2LINE

        # total number of lines
        self._num_lines = lines

        # current line. default 0 (first line)
        self._current_line = 0

        # for some 1 line displays you can select a 10 pixel high font
        if dotsize and lines == 1:
            self._display_function |= LCD_5x10DOTS

        # see page 45/46 for initialization specification
        # according to datasheet, we need at least 40ms after power rises above 2.7V
        # we'll sleep 50ms
        sleep(0.050)

        # pull RS and E low to begin commands
        self._shift_reg.set(PIN_RS, LOW)
        self._shift_reg.set(PIN_E, LOW)

        # write out shift register
        self._shift_reg.write_out()

        # put lcd into 4bit mode

        # start in 8bit mode, try to set 4bit mode

    #### user functions ####
    def clear(self):


    def home(self):


    def set_cursor():


    def no_display(self):


    def display(self):


    def no_cursor(self):


    def cursor(self):


    def no_blink(self):


    def blink(self):


    def scroll_display_left(self):


    def scroll_display_right(self):


    def left_to_right(self):


    def right_to_left(self):
        """display text from right to left"""
        self._display_mode &= ~LCD_ENTRYLEFT
        self._command(LCD_ENTRYMODESET | self._display_mode)

    def autoscroll(self):
        """right justify text from the cursor"""
        self._display_mode &= LCD_ENTRYSHIFTINCREMENT
        self._command(LCD_ENTRYMODESET | self._display_mode)

    def no_autoscroll(self):
        """left justify text from the cursor"""
        self._display_mode &= ~LCD_ENTRYSHIFTINCREMENT
        self._command(LCD_ENTRYMODESET | self._display_mode)


    def create_char(self, location, charmap):
        """fill first 8 CGRAM locations with custom characters"""
        # only take 8 locations
        location &= 0x7

        # ???
        self._command(LCD_SETCGRAMADDR | location << 3)

        # write bits in charmap
        for i in range(8):
            self._write(charmap[i])

    #### mid level functions ###
    def _command(self, value):
        """send value using COMMAND function"""
        self._send(value, LOW)

    def _write(self, value):
        """send value using WRITE function"""
        self._send(value, HIGH)

    #### low level functions ###
    def _send(self, value, mode):
        """write either command or data"""
        # choose command (LOW) or write(HIGH)
        self._shift_reg.set(PIN_RS, mode)
        self._shift_reg.write_out()

        # write value out using 4 bits
        # most significant 4 bits first
        self._write4bits(value >> 4)
        # least significant 4 bits second
        self._write4bits(value)

    def _write4bits(self, value):
        """write 4 least significant digits of value to 4 serial pins"""
        # 1st bit - D4
        self._shift_reg.set(PIN_D4, value & 1)

        # shift value to right - 2nd digit becomes 1st
        value >>= 1

        # 2nd bit - D5
        self._shift_reg.set(PIN_D5, value & 1)

        # shift value to right
        value >>= 1

        # 3rd bit - D6
        self._shift_reg.set(PIN_D6, value & 1)

        # shift value to right
        value >>= 1

        # 4th bit - D7
        self._shift_reg.set(PIN_D7, value & 1)

        # write register to lcd
        self._pulse_enable()

    def _pulse_enable(self):
        """pulse PIN_E LOW-HIGH-LOW - sends register to lcd"""
        self._shift_reg.set(PIN_E, LOW)
        self._shift_reg.write_out()

        # sleep 1us
        sleep(0.000001)
        self._shift_reg.set(PIN_E, HIGH)
        self._shift_reg.write_out()

        # sleep 1us - enable pulse must be >450ns
        sleep(0.000001)
        self._shift_reg.set(PIN_E, LOW)
        self._shift_reg.write_out()

        # sleep 100us - command needs >37us to settle
        sleep(0.0001)
