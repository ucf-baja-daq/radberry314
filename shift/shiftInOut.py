# shift register test with raspberry pi
# shift out - 74HC595n
# shift in - cd4021b

import RPi.GPIO as GPIO
from RPi.GPIO import OUT, IN, HIGH, LOW, BOARD
from time import sleep
import logging

# setup log
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

# Raspberry pi pin numbering setup
GPIO.setwarnings(False)
GPIO.setmode(BOARD)

# LCD shift register pins
lcdClock = 35
lcdLatch = 36
lcdData = 37

# Shift in register pins
inClock = 33
inLatch = 32
inData = 31

# LED shift register pins
ledClock = 7
ledLatch = 8
ledData = 10

# setup pins as input/output
GPIO.setup(lcdClock, OUT)
GPIO.setup(lcdLatch, OUT)
GPIO.setup(lcdData, OUT)

GPIO.setup(inClock, OUT)
GPIO.setup(inLatch, OUT)
GPIO.setup(inData, IN)

GPIO.setup(ledClock, OUT)
GPIO.setup(ledLatch, OUT)
GPIO.setup(ledData, OUT)

class ShiftOut():
	def __init__(self, latchPin, clockPin, serialPin, numOfRegisters):
		self.latchPin = latchPin
		self.clockPin = clockPin
		self.serialPin = serialPin
		self.numOfRegisters = numOfRegisters
		self.register = 0;

		# setup pin binary values
		for i in range (8 * self.numOfRegisters):
			self.pins[i] = 2 ^ i

		# set all registers low
		self.writeOut()

	def writeOut(self):
		logging.debug("writing {:b} to register".format(self.register))
		# create binary list from desired output
		# bin() creates a number '0b101010' - need to read from 3rd digit for actual number
		rawBits = [int(i) for i in bin(self.register)[2:]]

		# make output most significant digit first
		outBits = [0 for i in range(8 * self.numOfRegisters)]
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

	def set(self, index, value):
		logging.debug("Setting register {} to {}".format(index + 1, value))
		if value:
			self.register |= self.pins[index]
		else:
			self.register &= ~self.pins[index]

	def clear(self):
		logging.debug("Setting all registers LOW.")
		for i in range(8 * self.numOfRegisters):
			self.setRegister(i, LOW)
		self.writeOut()

	def setAll(self):
		logging.debug("Setting all registers HIGH.")
		for i in range(8 * self.numOfRegisters):
			self.setRegister(i, HIGH)
		self.writeOut()


class ShiftIn():
	def __init__(self, latchPin, clockPin, serialPin, numOfRegisters):
		self.latchPin = latchPin
		self.clockPin = clockPin
		self.serialPin = serialPin
		self.numOfRegisters = numOfRegisters
		self.stateArray = None
		self.state = 0

		# inactive state
		GPIO.output(inLatch, LOW)
		GPIO.output(inClock, HIGH)

	def read(self):
		# pulse latch to begin reading
		GPIO.output(inLatch, HIGH)
		sleep(0.00002)
		GPIO.output(inLatch, LOW)

		# move from pin 8 to pin 1 on shift register
		for i in range(numOfRegisters - 1, -1, -1):
			# set clock low to read data pin
			GPIO.output(inClock, LOW)

			# check value of data pin and write to proper binary location in state
			if (GPIO.input(inData)):
				byte |= (1 << i)

			# set clock high for next cycle
			GPIO.output(inClock, HIGH)

		# put state into an array
		# in this case, a 0 in state will be considered ON (1) in the array
		# it assumes that the input pins are pulled up and active low (for example, a button press will send a LOW signal and will be HIGH otherwise)
		for i in range (8 * numOfRegisters):
			if (~state & (1 << i)):
				stateArray[i] = 1
			else:
				stateArray[i] = 0


ledShift = ShiftOut(ledLatch, ledClock, ledData, 1)

while(True):
	ledShift.setAll()
	sleep(1)
	ledShift.clear()
	sleep(1)
