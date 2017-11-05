import  RPi.GPIO as GPIO
import pyadda
from adc_consts import *
import time

# Raspberry pi pin numbering setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

PIN_DRDY = 11

GPIO.setup(PIN_DRDY, GPIO.IN)

# define gain, sampling rate, and scan mode
gain = ADS1256_GAIN['1']
samplingRate = ADS1256_DRATE['10']
scanMode = ADS1256_SMODE['DIFFERENTIAL']

# setup ads1256 chip
pyadda.startADC(gain, samplingRate, scanMode)

prevTime = time.time()
meanSampleRate = 0
counter = 0

GPIO.add_event_detect(PIN_DRDY, GPIO.FALLING, callback=pyadda.collectData)
while True:
	if GPIO.event_detected(PIN_DRDY):
		print("{:d} - {:.8f} (V)".format(pyadda.readChannelRaw(0), pyadda.readChannelVolts(0)))
