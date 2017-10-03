import  RPi.GPIO as GPIO
from time import sleep
from timeit import default_timer as timer
from subprocess import call
import math
import time
from multiprocessing import Process, Queue
import glob     # used to find the flash drives

# Main Setup
missile_switch_pin_number = 3
strain_gauge_pin_number   = 5
hall_sensor_pin_number    = 40

led_1_pin_number = 38
led_2_pin_number = 36

hall_1_pin_number = 35
hall_2_pin_number = 37

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(missile_switch_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(hall_sensor_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(strain_gauge_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_1_pin_number, GPIO.OUT)
GPIO.setup(led_2_pin_number, GPIO.OUT)

GPIO.output(led_1_pin_number, GPIO.LOW)
GPIO.output(led_2_pin_number, GPIO.LOW)
print("Done GPIO Setup.\n")

exitFlag = 0
hallLedPins = [led_2_pin_number, led_1_pin_number]

#segments = [7,21,13,23,15,18,31,32]
#digits = [33,29,22,16]

baja_string     = "BAJA"
clear_character = 'C'

speedNumber = 4444

ON = 0
OFF = 1

#########################	CLASSES

class HallThread():
	# This class represents a hall sensor
	# each sensor takes data individually and writes to its own file
	
	def __init__(self, threadID, name, counter,  pinNumber, hallSensor_Num, diameter, gearBoxRatio, resFlag):
		print("Initializing Hall Sensor on Pin " + str(pinNumber) + ".")
		
		# initialize arguments
		self.threadID     = threadID
		self.name         = name
		self.pinNumber    = pinNumber
		self.diameter     = diameter
		self.gearBoxRatio = gearBoxRatio
		self.runningFlag  = 1
		self.ledPin       = hallLedPins[halSensor_Num - 1]
		
		# used to determine hall sensor trip state
		self.isHallSenWithBoard = False
		
		# setup input pin for hallsensor
		if resFlag == 0:
			GPIO.setup( pinNumber, GPIO.IN )
		elif resFlag == 1:
			GPIO.setup( pinNumber, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			
		# open file to write to
		# based on pin number and counter
		localtime = time.asctime( time.localtime(time.time()))
		localtimeStr = str(localtime).replace(" ", "_")
		
		# Check if usb is plugged in.
		# If so, write to usb.
		# If not, write to pi and set a flag (TODO)
		# so the next time a usb is plugged in, the files written
		# since the flag was created will be moved over
		
		# search for usb dir
		usbDir = glob.glob("/media/pi/*")
		
		# if usb dir exists
		if len(usbDir) > 0:
			self.file_str = usbDir[-1] + "/hallSen_Data" + str(pinNumber) + "_" + str.replace(localtimeStr, ':', '-') + ".csv"
		else:
			self.file_str = "/home/pi/Desktop/data/HallSensor/hallSen_Data" + str(pinNumber) + "_" + str.replace(localtimeStr, ':', '-') + ".csv"
			
		self.text_file = open(self.file_str, "w")
		
		# initial time for the time vector
		# self.initTime = time.time()
		self.initTime = timer()
		
		# initialize
		self.time1     = 0
		self.time2     = 0
		self.hallFlag  = 0
		self.gearRatio = 11.5
		
		print("Done with Hall Sensor Init.\n")
		
	def run(self, queue_reference, useQueue):
		print("Running hall sensor on pin " + str(self.pinNumber) + ".")
		print("Writing to " + self.file_str)
		
		
		global speedNumber
		self.counter = 0
		
		# TODO need to give this value by queue
		while self.runningFlag == 1:
			self.input_hallSen = GPIO.input( self.pinNumber )
			self.curTime = timer() - self.initTime
			
			if self.input_hallSen == self.isHallSenWithBoard and self.hallFlag == 0:
				GPIO.output(self.ledPin, GPIO.HIGH)
				self.hallFlag = 1
				
				# store current time in time2 and move previous time into time1
				self.time1, self.time2 = self.time2, self.curTime
				
				# calculate rpm based on time difference (1 revolution)
				self.rpm = 60/(self.time2 - self.time1)
				
				# calculate mph from rpm. based on wheel diameter
				self.mph = self.rpm * math.pi * self.diameter / 1056
				
				if useQueue:
					q.put(int(self.rpm))
					
				self.text_file.write( str(self.curtime) + "," + str(self.rpm) + "\n" )
				self.text_file.flush()
				
				self.endTime = timer() - self.initTime
				
				GPIO.output( self,ledPin, GPIO.LOW )
				
			elif self.input_hallSen == self.isHallSenWithBoard and self.hallFlag == 1:
				self.filler = 0
				
			else:
				self.hallFlag = 0
				
			time.sleep(0.00005)			#could be wrong, but also tried 0.0005 and seemed to work
			
		self.text_file.write( str(timer() - self.initTime) )
		self.text_file.was( "END OF DATA" )
		self.text_file.flush()
		self.text_file.close()
		
	def setFlag(self, flag):
		self.runningFlag = flag
		

class SevenSegThread():
	def __init__(self, threadID, name):
		print("Initializing Seven Segment Display.")
		
		self.ON  = 0
		self.OFF = 1
		
		self.segments = [7,21,13,23,15,18,31,32]
		self.digits   = [33,29,22,16]
		
		self.threadID = threadID
		self.name     = name
		
		#					  e	        d		  dp        c	      g	        b	      f	        a
		self.numbers = { ' ':[self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF],
						 '0':[self.ON , self.ON , self.OFF, self.ON , self.OFF, self.ON , self.ON , self.ON ],
						 '1':[self.OFF, self.OFF, self.OFF, self.ON , self.OFF, self.ON , self.OFF, self.OFF],
						 '2':[self.ON , self.ON , self.OFF, self.OFF, self.ON , self.ON , self.OFF, self.ON ],
						 '3':[self.OFF, self.ON , self.OFF, self.ON , self.ON , self.ON , self.OFF, self.ON ],
						 '4':[self.OFF, self.OFF, self.OFF, self.ON , self.ON , self.ON , self.ON , self.OFF],
						 '5':[self.OFF, self.ON , self.OFF, self.ON , self.ON , self.OFF, self.ON , self.ON ],
						 '6':[self.ON , self.ON , self.OFF, self.ON , self.ON , self.OFF, self.ON , self.ON ],
						 '7':[self.OFF, self.OFF, self.OFF, self.ON , self.OFF, self.ON , self.ON , self.ON ],
						 '8':[self.ON , self.ON , self.OFF, self.ON , self.ON , self.ON , self.ON , self.ON ],
						 '9':[self.OFF, self.ON , self.OFF, self.ON , self.ON , self.ON , self.ON , self.ON ],
						 'B':[self.ON , self.ON , self.OFF, self.ON , self.ON , self.ON , self.ON , self.ON ],
						 'A':[self.ON , self.OFF, self.OFF, self.ON , self.ON , self.ON , self.ON , self.ON ],
						 'J':[self.ON , self.ON , self.OFF, self.ON , self.OFF, self.ON , self.OFF, self.OFF],
						 'C':[self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF] }

		self.bufferKeys = [' ','0','1','2','3','4','5','6','7','8','9','B', 'A', 'J', 'C']

		# setup segment pins
		for seg in self.segments:
			GPIO.setup(seg, GPIO.OUT)
			GPIO.output(seg, False);

		# setup digit pins
		for dig in self.digits:
			GPIO.setup(dig, GPIO.OUT)
			GPIO.output(dig, False)

		self.buffer = 0
		self.length = 0
		
		self. inputStr = str( int(self.buffer) )
		
		self.length  = len( self.inputStr )
		self.display = [0] * self.length
		self.actualDigits = [0] * self.length
		
		for i in range (0, self.length):
			self.diplay[i] = self.inputStr[i]
			
		self.k = 3
		for i in range(self.length -1, -1, -1):
			self.actualDigits[i] = digits[self.k]
			self.k -= 1
			
		print("Seven Seg SetUp Done.\n")
		
	def run(self, q):
	
		global baja_string
		global clear_character
		global speedNumber
		
		prevNum = 0
		stTime = timer()
	
		while True:
			# check if something is in the queue
			if not q.empty():
				# put queue variable in temp
				temp = q.get()

				# if queue is BAJA or clear, put it in buffer
				if temp == baja_string or temp == clear_character:
					self.buffer = temp
				elif temp % 2 == 0:
					self.buffer = temp

				stTime = timer()

			# if queue is empty, 2 seconds have passed, and the buffer value is not BAJA or clear
			elif q.empty() and timer()-stTime > 2 and not(self.buffer == baja_string) and not(self.buffer == clear_character):
				self.buffer = 0
				stTime = timer()

			# convert buffer to string for processing
			self.inputStr = str( self.buffer )

			self.length = len(self.inputStr)

			# make arrays with number of entries equal to length of value
			self.display = [0]*self.length
			self.actualDigits = [0]*self.length

			# put input number intur display array
			for i in range (self.length):
				self.display[i] = self.inputStr[i]

			# right align string on display, reverse order of seven seg digits
			self.k = 3
			for i in range (self.length - 1, -1, -1):
				self.actualDigits[i] = self.digits[self.k]
				self.k -= 1

			# put value on display
			i = 0
			for dig in self.actualDigits:
				charCode = self.numbers[self.display[i]]
				
				j = 0
				for val in charCode:
					GPIO.output( self.segments[j], val )
					j += 1

				GPIO.output(dig, True)
				sleep(0.0005)
				GPIO.output(dig, False)

				i += 1
		

#########################

def startDAQ():
    global exitFlag
    global hallLedPins

    counter    = 0
    switchFlag = 0

    hall1Process_active = False
    hall2Process_active = False
    strainGauge_active  = False

    GPIO.output(led_1_pin_number, GPIO.HIGH)
    GPIO.output(led_2_pin_number, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(led_1_pin_number, GPIO.LOW)
    GPIO.output(led_2_pin_number, GPIO.LOW)

    queue = Queue()
    queue.put(baja_string)

    sev_seg_object  = SevenSegThread(3, "sevSeg")
    sev_seg_process = Process(target=sev_seg_object.run, args(queue,))
    sev_seg_process.daemon = True
    sev_seg_process.start()

    count_strain_guage = 0

    while exitFlag == 0:
        hall_input    = GPIO.input(hall_sensor_pin_number)
        missile_input = GPIO.input(missile_switch_pin_number)
        strain_input  = GPIO.input(strain_gauge_pin_number)

        if missile_input and not(hall_input):
            queue.put(clear_character)
            time.sleep(0.3)
            sev_seg_process.terminate()

            if hall1Process_active and hall2Process_active:
                hall1Process.terminate()
                hall2Process.terminate()

            time.sleep(0.5)
            break;

		# When Toggle goes from Off to On
        if hall_input and switchFlag == 0:
            switchFlag = 1
            counter += 1

            print("\nSwitch On.\n")

            hall1 = HallThread(1, "hall1", counter, hall_1_pin_number, 1, 23,11.1,0)
            hall2 = HallThread(2, "hall2", counter, hall_2_pin_number, 2, 23,11.1,1)

            print("Hall 1 Process Started")
            hall1Process = Process(target=hall1.run, args=(queue, True))
            hall1Process_active = True

            print("Hall 2 Process Started")
            hall2Process = Process(target=hall2.run, args=(queue, False))
            hall2Process_active = True

            hall1Process.daemon = True
            hall2Process.daemon = True

            hall1Process.start()
            hall2Process.start()

            time.sleep(0.5)

		# When Toggle goes from On to Off
        elif not(hall_input) and switchFlag == 1:
            switchFlag = 0
            queue.put(baja_string)
            print("\nSwitch Off.\n")
			
			# End the Hallsensor threads
			hall1.setFlag(0)
			hall2.setFlag(0)
			
			hall1Process.terminate()
			hall2Process.terminate()
			
			hall1Process_active = False
			hall2Process_active = False
			
			time.sleep(0.5)
			
		# Strain Guage Execution
		if strain_input and not(strainGauge_active):
			localtime = time.asctime( time.localtime(time.time()))
			localtimeStr = str(localtime).replace(" ", "_")
			callInput = "./home/pi/Desktop/daq/radberry314/ADC/ADDAcode/Raspberry/strain/strainTest " + localtimeStr
			count_strain_guage += 1
			call(callInput, shell=True)
			strainGauge_active = True
		elif not(strain_input) and strainGauge_active:
			strainGauge_active = False
			
		time.sleep(1.0)
		
	queue.close()

######################### General Functions

def shutdown():
    call("sudo shutdown -h now", shell=True)

######################### MAIN

print("Waiting for Missile Switch")

missile_input = GPIO.input(missile_switch_pin_number)
strain_input  = GPIO.input(strain_gauge_pin_number)
hall_input    = GPIO.input(hall_sensor_pin_number)

while not(strain_input and hall_input):
    strain_input  = GPIO.input(strain_gauge_pin_number)
    hall_input    = GPIO.input(hall_sensor_pin_number)
    sleep(1)

while True:
    missile_input = GPIO.input(missile_switch_pin_number)
    strain_input  = GPIO.input(strain_gauge_pin_number)
    hall_input    = GPIO.input(hall_sensor_pin_number)

    if not(missile_input):
        startDAQ()																	### START ******

    elif missile_input and hall_input and strain_input:
        startTime = Timer
        flag = 0

        print("Shutting down in 5 seconds. Toggle any switch to cancel.")

        while(timer() - startTime < 5.0):
            hall_input    = GPIO.input(hall_sensor_pin_number)
            missile_input = GPIO.input(missile_switch_pin_number)
            strain_input  = GPIO.input(strain_gauge_pin_number)

            if not(missile_input) or not(hall_input) or not(strain_input):
                flag = 0
                print("Cancelling ShutDown.")
                break
            sleep(0.05)
            flag = 1

        if flag == 1:
            break

    GPIO.output(led_1_pin_number, GPIO.LOW)
    GPIO.output(led_2_pin_number, GPIO.HIGH)
    sleep(0.25)
    GPIO.output(led_1_pin_number, GPIO.HIGH)
    GPIO.output(led_2_pin_number, GPIO.LOW)
    sleep(0.25)

shutdown()
