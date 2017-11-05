import  RPi.GPIO as GPIO
import pyadda
from py_adc import *
import time

# Raspberry pi pin numbering setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

PIN_DRDY = 11

GPIO.setup(PIN_DRDY, GPIO.IN)

# define gain, sampling rate, and scan mode
gain = ADS1256_GAIN['1']
samplingRate = ADS1256_DRATE['2d5']
scanMode = ADS1256_SMODE['SINGLE_ENDED']

# setup ads1256 chip
pyadda.startADC(gain, samplingRate, scanMode)

startTime = time.time()

GPIO.add_event_detect(PIN_DRDY, GPIO.FALLING)
while True:
	if GPIO.event_detected(PIN_DRDY):
		print('Sample ready! {}ms'.format(int((time.time()-startTime)*1000)))
