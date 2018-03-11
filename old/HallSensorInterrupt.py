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
		self.file_str = "/home/pi/Desktop/data/hallSen_Data"+ str(pinNumber) + "_" + localtimeStr + ".txt"
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