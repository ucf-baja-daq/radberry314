# liquid_crystal_595.py
# Library to interface with HD44780 LCD through a shift register on Raspberry Pi 3

# import shift register class
from shift_out import shift_out
from time import sleep
import RPi.GPIO as GPIO
from GPIO import OUT, HIGH, LOW

# Commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Entry flags
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Control flags
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Move flags
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Function set flags
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# Offset for up to 4 rows.
LCD_ROW_OFFSETS = (0x00, 0x40, 0x14, 0x54)

# shift register pin addresses
PIN_D4 = 0
PIN_D5 = 1
PIN_D6 = 2
PIN_D7 = 3
PIN_RS = 4
PIN_E = 5

class LCDShift():
    """class to interface with lcd over shift register"""

    #### initialization functions ####
    def __init__(self, latch_pin, clock_pin, serial_pin):
        # set up shift register object. Only one register
        self._shift_reg = shift_out(latch_pin, clock_pin, serial_pin, 1)

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
        self._cols = 0

    def begin(self, cols, lines, dotsize):
        """set up lcd dimensions"""

        # only support up to 2 lines
        if lines > 1:
            self._display_function |= LCD_2LINE

        # total number of lines
        self._num_lines = lines

        # current line. default 0 (first line)
        self._current_line = 0

        # total number of columns
        self._cols = cols

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
        # according to HD44780 datasheet, figure 24 on page 46
        self._write4bits(0x03)
        sleep(0.0045)

        self._write4bits(0x03)
        sleep(0.0045)

        self._write4bits(0x03)
        sleep(0.00015)

        self._write4bits(0x02)

        # setup values defined in display function above
        self._command(LCD_FUNCTIONSET | self._display_function)

        # turn the display on with no cursor and no blinking by default
        self._display_control = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()

        # clear display
        self.clear()

        # initialize text direction as left to right
        self._display_mode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self._command(LCD_ENTRYMODESET | self._display_mode)

    #### user functions ####
    def clear(self):
        """clear display and set cursor to 0,0"""
        self._command(LCD_CLEARDISPLAY)
        sleep(0.002)

    def home(self):
        """set cursor position to 0,0"""
        self._command(LCD_RETURNHOME)
        sleep(0.002)

    def set_cursor(self, col, row):
        """set cursor location"""
        # if row is more than num_lines, make it last row
        # row count starts at 0
        if row >= self._num_lines:
            row = self._num_lines - 1

        self._command(LCD_SETDDRAMADDR | (col + LCD_ROW_OFFSETS[row]))

    def no_display(self):
        """turn off display"""
        self._display_control &= ~LCD_DISPLAYON
        self._command(LCD_DISPLAYCONTROL | self._display_control)

    def display(self):
        """turn on display"""
        self._display_control |= LCD_DISPLAYON
        self._command(LCD_DISPLAYCONTROL | self._display_control)

    def no_cursor(self):
        """hide cursor"""
        self._display_control &= ~LCD_CURSORON
        self._command(LCD_DISPLAYCONTROL | self._display_control)

    def cursor(self):
        """show cursor"""
        self._display_control |= LCD_CURSORON
        self._command(LCD_DISPLAYCONTROL | self._display_control)

    def no_blink(self):
        """don't blink cursor"""
        self._display_control &= ~LCD_BLINKON
        self._command(LCD_DISPLAYCONTROL | self._display_control)

    def blink(self):
        """blink cursor"""
        self._display_control |= LCD_BLINKON
        self._command(LCD_DISPLAYCONTROL | self._display_control)

    def scroll_display_left(self):
        """scroll text from right to left"""
        self._command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scroll_display_right(self):
        """scroll text from left to right"""
        self._command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    def left_to_right(self):
        """display text from left to right"""
        self._display_mode |= LCD_ENTRYLEFT
        self._command(LCD_ENTRYMODESET | self._display_mode)

    def right_to_left(self):
        """display text from right to left"""
        self._display_mode &= ~LCD_ENTRYLEFT
        self._command(LCD_ENTRYMODESET | self._display_mode)

    def autoscroll(self):
        """right justify text from the cursor"""
        self._display_mode |= LCD_ENTRYSHIFTINCREMENT
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
        self._command(LCD_SETCGRAMADDR | (location << 3))

        # write bits in charmap
        for i in range(8):
            self._write(charmap[i])

    def message(self, text):
        """write text to display"""
        line = 0

        # iterate through each character
        for char in text:
            # advance to next line if character is newline
            if char == '\n':
                line += 1

                # move to left or right side depending on text direction
                col = 0 if self._display_mode & LCD_ENTRYLEFT > 0 else self._cols - 1

                self.set_cursor(col, line)

            # write character to display
            else:
                self._write(ord(char))

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
