# main Data Acqusition code
# runs on RPi boot

# we want this code to run on the pi's boot
# what should run on boot
#	-speedometer

# what should run via toggle switches
#	-CVT/gearbox data collection
#	-strain gauge data collection

import threading
import time
import math
from timeit import default_timer as timer 
from multiprocessing import Process, Queue
import shutdownPi

#import ../ADC/ADDAcode/Raspberry/strain/strainTestPythonExt
#import ../ADC/ADDAcode/Raspberry/strain/strainExtTEST

from subprocess import call

# flag to exit the program
exitFlag = 0

import RPi.GPIO as GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # IO 21; sets up a pull up resistor
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	 #program off/on (missle switch)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)	 #strain gauge collection on/off
GPIO.setup(38, GPIO.OUT) #IO 20 led 1
GPIO.setup(36, GPIO.OUT) #IO 16 led 2

GPIO.output(38, GPIO.LOW)
GPIO.output(36, GPIO.LOW)

# original config: left led is engine
#hallLedPins = [38, 36]

# modified so that the brighter led is connected to the engine output
hallLedPins = [36, 38]

segments = [7,21,13,23,15,18,31,32]
digits = [33,29,22,16]

speedNumber = 4444

ON = 0
OFF = 1

# the switch doesnt run with a pull down configuration
# the two pins closer to what you want to be the ON position
# should be connected to give a TRUE value in that position


class HallThread ():
	
	# initiate myThread object
	# threadID hallSensor position ("cvt" or "sec")
	# name - thread name 
	def __init__(self, threadID, name, counter, pinNumber, hallSensor_Num, diameter, gearBoxRatio,resFlag):
		#threading.Thread.__init__(self)
		print("Initializing Hall Sensor on pin " + str(pinNumber) + ".")
		self.threadID = threadID
		self.name = name
		self.pinNumber = pinNumber
		self.diameter = diameter
		self.gearBoxRatio = gearBoxRatio
		self.runningFlag = 1
		self.ledPin = hallLedPins[hallSensor_Num - 1]
		
		self.isHallSenWithBoard = False
		
		# setup input pin for hallsensor
		if resFlag == 0:
			GPIO.setup( pinNumber, GPIO.IN )
		elif resFlag==1:
			GPIO.setup(pinNumber,GPIO.IN, pull_up_down=GPIO.PUD_UP)
		
		# open file to write to
		# based on pin number and counter
		localtime = time.asctime( time.localtime(time.time()))
		localtimeStr = str(localtime).replace(" ", "_")
		self.file_str = "data/HallSensors/hallSen_Data"+ str(pinNumber) + "_" + localtimeStr + ".csv"
		self.text_file = open(self.file_str, "w")
		
		# initial time for time vector
		# self.initTime = time.time()
		self.initTime = timer()
		
		# initialize 
		self.t1 = 0
		self.t2 = 0
		self.hallFlag = 0
		self.gearRatio = 11.5
		
		print("Done.\n")
		
		
		
	def run(self, q, useQueue):
		print("Running hall sensor on pin " + str(self.pinNumber) + ".")
		print("Writing to " + self.file_str)
		# while switch is toggled on
		
		global speedNumber
		self.counter = 0
		
		while self.runningFlag == 1:
			self.input_hallSen = GPIO.input( self.pinNumber )
			# self.curTime = time.time() - self.initTime
			self.curTime = timer() - self.initTime
			
			if self.input_hallSen == self.isHallSenWithBoard and self.hallFlag == 0:
				GPIO.output(self.ledPin, GPIO.HIGH)
				self.hallFlag = 1
				self.t1 = self.t2													# stores the previous current time from curTime
				self.t2 = self.curTime											# stores the current time in curTime
				self.rpm = 60/(self.t2 - self.t1)
				if (self.rpm > 9999):
					self.rpm = self.rpm / 1000
				self.mph = self.rpm * math.pi * self.diameter / 1056 / self.gearBoxRatio
				
				#sharedValues.setSpeed(int(self.rpm))
				#speedNumber = int(self.rpm)
				
				if useQueue:
					#q.put(int(self.mph))
					q.put(int(self.rpm))
				
				#print(self.name + " - " + str(self.curTime) + "," + str(self.rpm))
				self.text_file.write( str(self.curTime) + "," + str(self.rpm) + "\n" )
				self.text_file.flush()
				
				self.endTime = timer() - self.initTime
				#if self.counter > 9:
				#	self.counter = 0
				#	self.text_file.flush()
				#else:
				#	self.text_file.write( str(self.curTime) + "," + str(self.rpm) + "\n" )
				#	self.counter += 1
				#self.text_file.flush()
				GPIO.output(self.ledPin, GPIO.LOW)
			elif self.input_hallSen == self.isHallSenWithBoard and self.hallFlag == 1:
				self.filler = 0
			
			else:
				self.hallFlag = 0
			time.sleep(0.00005)		#could be wrong, but also tried 0.0005 and seemed to work
		
		self.text_file.write(str(timer()-self.initTime))
		self.text_file.write("END OF DATA")
		self.text_file.flush()
		self.text_file.close()
	
	def setFlag(self, flag):
		self.runningFlag = flag
		
class HallSensorInterrupt():
	#!/usr/bin/python3
	dist_meas = 0.00
	km_per_hour = 0
	rpm = 0
	elapse = 0
	pulse = 0
	start_timer = time.time()

	def __init__(self, threadID, name, counter, pinNumber, hallSensor_Num, diameter):
		#threading.Thread.__init__(self)
		print("Initializing Hall Sensor on pin " + str(pinNumber) + ".")
		self.threadID = threadID
		self.name = name
		self.pinNumber = pinNumber
		self.runningFlag = 1
		self.ledPin = hallLedPins[hallSensor_Num - 1]
		
		self.isHallSenWithBoard = False
		
		# setup input pin for hallsensor
		GPIO.setup( pinNumber, GPIO.IN )
		
		# open file to write to
		# based on pin number and counter
		localtime = time.asctime( time.localtime(time.time()))
		localtimeStr = str(localtime).replace(" ", "_")
		self.file_str = "data/hallSen_Data"+ str(pinNumber) + "_" + localtimeStr + ".txt"
		self.text_file = open(self.file_str, "w")
		
		# initial time for time vector
		# self.initTime = time.time()
		self.initTime = timer()
		
		# initialize 
		self.t1 = 0
		self.t2 = 0
		self.hallFlag = 0
		self.gearRatio = 11.5
		GPIO.add_event_detect(pinNumber, GPIO.FALLING, callback = calculate_elapse, bouncetime = 5)
		print("Done.\n")

	def init_GPIO():               # initialize GPIO
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		GPIO.setup(pinNumber,GPIO.IN)

	def calculate_elapse(channel):            	# callback function
		global pulse, start_timer, elapse
		pulse+=1                        			# increase pulse by 1 whenever interrupt occurred
		elapse = time.time() - start_timer      	# elapse for every 1 complete rotation made!
		start_timer = time.time()            	# let current time equals to start_timer

	def calculate_speed(r_cm):
		global pulse,elapse,rpm,dist_km,dist_meas,km_per_sec,km_per_hour
		if elapse !=0:                     		# to avoid DivisionByZero error
			if time.time() - start_timer < 2:
				rpm = 1/elapse * 60
				circ_cm = (2*math.pi)*r_cm         	# calculate wheel circumference in CM
				dist_km = circ_cm/100000          	# convert cm to km
				km_per_sec = dist_km / elapse      	# calculate KM/sec
				km_per_hour = km_per_sec * 3600     	# calculate KM/h
				dist_meas = (dist_km*pulse)*1000   	# measure distance traverse in meter
				return km_per_hour
			else:
				rpm = 0

	def init_interrupt():
		GPIO.add_event_detect(pinNumber, GPIO.FALLING, callback = calculate_elapse, bouncetime = 5)
	   

	def run(self, q, useQueue):
		#init_GPIO()
		#init_interrupt()
		global pulse,elapse,rpm,dist_km,dist_meas,km_per_sec,km_per_hour
		while True:
			#calculate_speed(20)   				# call this function with wheel radius as parameter
			if elapse !=0:                     		# to avoid DivisionByZero error
				if time.time() - start_timer < 2:
					rpm = 1/elapse * 60
			else:rpm = 0
			#print('rpm:{0:.0f}-RPM kmh:{1:.0f}-KMH dist_meas:{2:.2f}m pulse:{3}'.format(rpm,km_per_hour,dist_meas,pulse))
			print('rpm:{0:.0f}-RPM'.format(rpm))
			self.text_file.write( str(self.curTime) + "," + str(rpm) + "\n" )
			if useQueue:
				q.put(rpm) 
			sleep(.0005)
			
		self.text_file.write(str(timer()-self.initTime))
		self.text_file.flush()
		self.text_file.close()

		
class SevenSegThread():
	def __init__(self, threadID, name):
		#hreading.Thread.__init__(self)
		print("Initializing Seven Segment Display.")
		self.threadID = threadID
		self.name = name
		
		#					  e    d    dp   c    g    b    f    a
		self.numbers = { ' ':[OFF, OFF, OFF, OFF, OFF, OFF, OFF, OFF],
						 '0':[ON , ON , OFF, ON , OFF, ON , ON , ON ],
						 '1':[OFF, OFF, OFF, ON , OFF, ON , OFF, OFF],
						 '2':[ON , ON , OFF, OFF,  ON, ON , OFF, ON ],
						 '3':[OFF, ON , OFF, ON , ON , ON , OFF, ON ],
						 '4':[OFF, OFF, OFF, ON , ON , ON , ON , OFF],
						 '5':[OFF, ON , OFF, ON , ON , OFF, ON , ON ],
						 '6':[ON , ON , OFF, ON , ON , OFF, ON , ON ],
						 '7':[OFF, OFF, OFF, ON , OFF, ON , ON , ON ],
						 '8':[ON , ON , OFF, ON , ON , ON , ON , ON ],
						 '9':[OFF, ON , OFF, ON , ON , ON , ON , ON ],
						 'B':[ON , ON , OFF, ON , ON , ON , ON , ON ],
						 'A':[ON , OFF, OFF, ON , ON , ON , ON , ON ],
					     'J':[ON , ON , OFF, ON , OFF, ON , OFF, OFF],
					     'C':[OFF, OFF, OFF, OFF, OFF, OFF, OFF, OFF] }
						 
		self.numKeys = [' ','0','1','2','3','4','5','6','7','8','9','B', 'A', 'J', 'C']
		
		for seg in segments:
			GPIO.setup(seg, GPIO.OUT)
			GPIO.output(seg, False);
			
		for dig in digits:
			GPIO.setup(dig, GPIO.OUT)
			GPIO.output(dig, False)
			
		self.num = 0
		self.length = 0
		
		self.inputStr = str( int(self.num) )
		
		self.length = len(self.inputStr)
		self.display = [0]*self.length
		self.actualDigits = [0]*self.length
		
		for i in range (0, self.length):
			self.display[i] = self.inputStr[i]
			
		self.k = 3
		for i in range(self.length - 1, -1, -1):
			self.actualDigits[i] = digits[self.k]
			self.k = self.k - 1
					
		print("Seven Seg SetUp: Done.\n")	
		
	def run(self, q):
		
		global speedNumber
		
		prevNum = 0
		
		stTime = timer()
		
		while True:
			if not q.empty():
				temp = q.get()
				if temp == "BAJA" or temp == 'C':
					self.num = temp
				elif temp % 2 == 0:
					self.num = temp
				prevNum = self.num
				stTime = timer()
			elif q.empty() and timer()-stTime > 2 and not(self.num == "BAJA") and not(self.num == "C"):
				self.num = 0
				prevNum = self.num
				stTime = timer()

			self.inputStr = str( self.num )

			self.length = len(self.inputStr)
			self.display = [0]*self.length
			self.actualDigits = [0]*self.length

			for i in range (0,self.length):
				self.display[i] = self.inputStr[i]           # putting input Number into display array

			self.k = 3
			for i in range (self.length - 1, -1, -1):
				self.actualDigits[i] = digits[self.k]
				self.k = self.k - 1

			i = 0
			for dig in self.actualDigits:
					
				onOFF_value = self.numbers[self.display[i]]

				j = 0
				for val in onOFF_value:
					GPIO.output( segments[j], val )
					j = j + 1

				GPIO.output(dig, True)
				time.sleep(0.0005)
				GPIO.output(dig, False)

				i = i + 1
	
############	
	
def start():
	global exitFlag
	global hallLedPins
		
	counter = 0
	switchFlag = 0

	hall1Proc_active = False
	hall2Proc_acitve = False
	strainGauge_active = False

	#startup LED
	GPIO.output(38, GPIO.HIGH)
	GPIO.output(36, GPIO.HIGH)
	time.sleep(3)
	GPIO.output(38, GPIO.LOW)
	GPIO.output(36, GPIO.LOW)
	
	queue = Queue()
	queue.put("BAJA")

	sevsegObj = SevenSegThread(3, "sevSeg")
	sevsegProcess = Process(target=sevsegObj.run, args=(queue,))		# do no delete this goddamn comma! please :)
	sevsegProcess.daemon = True
	sevsegProcess.start()
	
	print("hi")
	
	inputCommand = ""

	countStrainGuage = 0

	while exitFlag == 0:
		input_state = GPIO.input(40)			# hall sen
		input_state_fire = GPIO.input(3)		# missle switch
		input_state_strainG = GPIO.input(5)		# strain gauge
		
		if input_state_fire == True and not (input_state == True):
			queue.put('C')
			#hall1.setFlag(0)
			#hall2.setFlag(0)
			
			time.sleep(0.3)
			
			sevsegProcess.terminate()
			
			if hall1Proc_active and hall2Proc_active:
				hall1Process.terminate()
				hall2Process.terminate()
			
			time.sleep(0.5)
			break;
		
		#inputCommand = input()
		#print(str(input_state))
		
		# when toggle goes from off to on
		if input_state == True and switchFlag == 0:
			switchFlag = 1
			counter += 1
			
			print("\nSwitch on.\n")	
			# start the hallsensor thread
			hall1 = HallThread(1, "hall1", counter, 35, 1, 23,11.1,0)
			hall2 = HallThread(2, "hall2", counter, 37, 2, 23,11.1,1)
			
			#hall1 = HallSensorInterrupt(1, "hall1", counter, 35, 1, 22)
			#hall2 = HallSensorInterrupt(2, "hall2", counter, 37, 2, 22)
			
			print("hall1")
			hall1Process = Process(target=hall1.run, args=(queue, True))
			hall1Proc_active = True
			print("hall2")
			hall2Process = Process(target=hall2.run, args=(queue, False))
			hall2Proc_active = True
			
			hall1Process.daemon = True
			hall2Process.daemon = True
			
			hall1Process.start()
			hall2Process.start()
			
			#hall1.start()
			#hall2.start()		
			time.sleep(0.5)
		
		# when toggle goes from on to off
		elif input_state == False and switchFlag == 1:
			switchFlag = 0
			queue.put("BAJA")
			print("\nSwitch off.\n")
			
			# end the hallsensor thread
			hall1.setFlag(0)
			hall2.setFlag(0)
			
			hall1Process.terminate()
			hall2Process.terminate()
			
			hall1Proc_active = False
			hall2Proc_active = False
			
			time.sleep(0.5)
		
		# Strain Guage Execution
		if input_state_strainG == True and strainGauge_active == False:
			localtime = time.asctime( time.localtime(time.time()))
			localtimeStr = str(localtime).replace(" ", "_")
			callInput = "sudo ./../ADC/ADDAcode/Raspberry/strain/strainTest " + localtimeStr
			countStrainGuage += 1
			call(callInput, shell=True)
			strainGauge_active = True
		elif input_state_strainG == False and strainGauge_active == True:
			strainGauge_active = False
		
		#result = strainExtTEST.system()
		
		time.sleep(1.0)
	
	queue.close()

start()

