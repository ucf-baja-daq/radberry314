# main - collection standby mode
# reads toggle switches to begin hall sensor and strain gauge collection

import RPi.GPIO as GPIO
import threading
import time
import math
from timeit import default_timer as timer 
from multiprocessing import Process, Queue
from subprocess import call

from seven_seg import SevenSeg
from hall import Hall

class Main():
	def __init__(self):
		# flag to exit the program
		self.exitFlag = 0

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
		self.hallLedPins = [36, 38]

		self.segments = [7,21,13,23,15,18,31,32]
		self.digits = [33,29,22,16]

		self.speedNumber = 4444

		# the switch doesnt run with a pull down configuration
		# the two pins closer to what you want to be the ON position
		# should be connected to give a TRUE value in that position
		
	def start(self):
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

		sevsegObj = SevenSeg(self.segments, self.digits)
		sevsegProcess = Process(target=sevsegObj.run, args=(queue,))		# do not delete this goddamn comma! please :)
		sevsegProcess.daemon = True
		sevsegProcess.start()
		
		countStrainGuage = 0

		while self.exitFlag == 0:
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
				hall1 = Hall(1, "hall1", counter, 35, 1, self.hallLedPins, 23,11.1,0)
				hall2 = Hall(2, "hall2", counter, 37, 2, self.hallLedPins, 23,11.1,1)
				
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
				callInput = "./home/pi/Desktop/daq/radberry314/ADC/ADDAcode/Raspberry/strain/strainTest " + localtimeStr
				countStrainGuage += 1
				call(callInput, shell=True)
				strainGauge_active = True
			elif input_state_strainG == False and strainGauge_active == True:
				strainGauge_active = False
			
			#result = strainExtTEST.system()
			
			time.sleep(1.0)
		
		queue.close()
