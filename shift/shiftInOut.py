# shift register test with raspberry pi
# shift out - 74HC595n
# shift in - cd4021b

import RPi.GPIO as GPIO
from RPi.GPIO import OUT, IN, HIGH, LOW, BOARD
from time import sleep

# Raspberry pi pin numbering setup
GPIO.setwarnings(False)
GPIO.setmode(BOARD)

outLatchPin = 36
outClockPin = 35
outSerialPin = 37

inLatchPin = 32
inClockPin = 33
inSerialPin = 31

GPIO.setup(outLatchPin, OUT)
GPIO.setup(outClockPin, OUT)
GPIO.setup(outSerialPin, OUT)

GPIO.setup(inLatchPin, OUT)
GPIO.setup(inClockPin, OUT)
GPIO.setup(inSerialPin, IN)

class ShiftOut():
	def __init__(self, latchPin, clockPin, serialPin):
		self.latchPin = latchPin
		self.clockPin = clockPin
		self.serialPin = serialPin

		# set all registers low
		self.write(0)

	def write(self, output):
		# create binary list from desired output
		# bin() creates a number '0b101010' - need to read from 3rd digit for actual number
		rawBits = [int(i) for i in bin(output)[2:]]

		# make output most significant digit first
		outBits = [0 for i in range(8)]
		for i in range(1, len(rawBits) + 1):
			outBits[-i] = rawBits[-i]

		# set latch low to begin writing
		GPIO.output(self.latchPin, LOW)

		# send bits to shift register
		# most significant digit first
		for bit in outBits:
			# set output value
			GPIO.output(self.serialPin, bit)

			# pull pulse clock high to write
			GPIO.output(self.clockPin, HIGH)

			# pull serial low for next write
			GPIO.output(self.serialPin, LOW)

			# pull clock low for next write
			GPIO.output(self.clockPin, LOW)

		# set latch high to latch values to register
		GPIO.output(self.latchPin, HIGH)


class ShiftIn():
	def __init__(self, latchPin, clockPin, serialPin):
		self.latchPin = latchPin
		self.clockPin = clockPin
		self.serialPin = serialPin

		# set pins low as default
		GPIO.output(self.latchPin, LOW)
		GPIO.output(self.clockPin, LOW)
		GPIO.output(self.serialPin, LOW)

	def read(self):
		pass
