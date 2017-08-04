import glob
import RPi.GPIO as GPIO
import time
import math
from timeit import default_timer as timer 

class Hall ():
	
	# initiate myThread object
	# threadID hallSensor position ("cvt" or "sec")
	# name - thread name 
	def __init__(self, threadID, name, counter, pinNumber, hallSensor_Num, hallLedPins, diameter, gearBoxRatio,resFlag):
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
		
		# check if usb is plugged in
		# if so, write to usb. if not, write to pi and set a flag (TODO)
		# so the next time a usb is plugged in, the files written
		# since the flag was created will be moved over

		# search for usb dir
		usbDir = glob.glob("/media/pi/*")

		# if usb dir exists
		if usbDir.len() > 0:
			self.file_str = usbDir[0] + "hallSen_Data"+ str(pinNumber) + "_" + localtimeStr + ".csv"
		else:
			self.file_str = "/home/pi/Desktop/data/HallSensors/hallSen_Data"+ str(pinNumber) + "_" + localtimeStr + ".csv"

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
