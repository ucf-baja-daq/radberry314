from dependencies.HallSensor import HallSensor
from dependencies.LCDShift import LCDShift
from dependencies.LIS3DH import LIS3DH
from dependencies.ShiftIn import ShiftIn
from dependencies.ShiftOut import ShiftOut

import RPi.GPIO as GPIO
from GPIO import IN, OUT, HIGH, LOW, BOARD

GPIO.setwarnings(False)
GPIO.setmode(BOARD)
