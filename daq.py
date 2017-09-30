# built-in imports
import RPi.GPIO as GPIO

from time import sleep
from subprocess import call
from timeit import default_timer as timer
from multiprocessing import Process, Queue

# local imports
from shutdownPi import shutdown

# functions
def shutdown(q):
	startTime = timer()																			# and hall sen switch is up
	flag = 0																					# and strain gauge switch is up
																								
	print("Shutting down in 5 seconds. Toggle any switch to cancel.")
	
	diff = int(timer() - startTime)
	
	while (diff < 5):
		input_state = GPIO.input(40)
		input_state_fire = GPIO.input(3)
		input_state_strainG = GPIO.input(5)	
		if not q.get() == diff:
			q.put(diff)
		
		if input_state_fire == False or input_state == False or input_state_strainG == False:
			flag = 0
			print("Cancelling shutdown.")
			flag = 0
			break
		sleep(0.05)
		flag = 1
		diff = int(timer() - startTime)
		
	if flag == 1:
		#call("sudo shutdown -h now", shell=True)
		print("shutdown pi")


# classes
class SevenSegDisplay():
	def __init__(self):
		print("Setting up display.")
		self.ON = 0
		self.OFF = 1
		
		self.segments = [7,21,13,23,15,18,31,32]
		self.digits = [33,29,22,16]
		
		#					  e	d	dp   c	g	b	f	a
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

		print("done.\n")

	def run(self, q):
		while True:
			# start timer
			timeState = timer()

			# check if something is in the queue
			if not q.empty():
				# put queue variable in temp
				temp = q.get()
				
				# if queue is BAJA or clear, put it in buffer
				if temp == "BAJA" or temp == 'C':
					self.buffer = temp
				elif temp % 2 == 0:
					self.buffer = temp

				timeState = timer()

			# if queue is empty, 2 seconds have passed, and the buffer value is not BAJA or clear
			elif q.empty() and timer()-timeState > 2 and not(self.buffer == "BAJA") and not(self.buffer == "C"):
				self.buffer = 0
				timeState = timer()

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


# setup RPi board
print("Setting up RPi.")
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
print("Done.\n")

# setup toggle switches
print("Setting up pins.")
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# IO 21; sets up a pull up resistor
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# setup toggle box leds
GPIO.setup(38, GPIO.OUT) # led 1
GPIO.setup(36, GPIO.OUT) # led 2

# default leds to OFF
GPIO.output(38, GPIO.LOW)
GPIO.output(36, GPIO.LOW)
print("Done.\n")

print("Waiting for missle switch.")

# read toggle switches
missile_input = GPIO.input(40)
strain_input = GPIO.input(5)
hall_input = GPIO.input(3)

# check if toggle switches are in system off position
# stay here until the switches are turned off so the next loop doesn't shut off the pi
while missile_input and strain_input and hall_input:
	missile_input = GPIO.input(40)
	strain_input = GPIO.input(5)
	hall_input = GPIO.input(3)
	sleep(1)

# setup queue
queue = Queue()
queue.put("BAJA")

# setup display
sevSeg = SevenSegDisplay()
sevSegProcess = Process(target=sevSeg.run, args=(queue,))  # do not delete this goddamn comma! please :)
sevSegProcess.daemon = True
sevSegProcess.start()

# system standby loop
while True:
	# read toggle switches
	missile_input = GPIO.input(40)
	strain_input = GPIO.input(5)
	hall_input = GPIO.input(3)

	# if missile switch is down
	if not missile_input:
		# call collection standby
		queue.put("C")

	# if all switches are up, shutdown pi
	elif missile_input and strain_input and hall_input:
		shutdown(q)
		
	GPIO.output(38, GPIO.LOW)
	GPIO.output(36, GPIO.HIGH)
	queue.put("BAJA")
	sleep(0.25)
	GPIO.output(38, GPIO.HIGH)
	GPIO.output(36, GPIO.LOW)
	queue.put("C")
	sleep(0.24)
