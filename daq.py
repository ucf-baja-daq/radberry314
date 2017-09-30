# built-in imports
import RPi.GPIO as GPIO

from time import sleep
from subprocess import call
from timeit import default_timer as timer
from multiprocessing import Process, Queue

# local imports
from shutdownPi import shutdown

# setup RPi board
print("Setting up RPi.")
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
print("Done.\n")

# setup toggle switches
print("Setting up pins.")
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # IO 21; sets up a pull up resistor
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

# setup display
sevSeg = SevenSegDisplay()
sevSegProcess = Process(target=sevSeg.run, args=(queue,))  # do not delete this goddamn comma! please :)
sevsegProcess.daemon = True
sevsegProcess.start()

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
        shutdown()

def shutdown():
    call("sudo shutdown -h now", shell=True)


class SevenSegDisplay():
    def __init__(self):
        print("Setting up display.")
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

		self.bufferKeys = [' ','0','1','2','3','4','5','6','7','8','9','B', 'A', 'J', 'C']

        # setup segment pins
        for seg in segments:
			GPIO.setup(seg, GPIO.OUT)
			GPIO.output(seg, False);

        # setup digit pins
		for dig in digits:
			GPIO.setup(dig, GPIO.OUT)
			GPIO.output(dig, False)

        self.buffer = "8888"

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

            if self.inputStr == "C":
                self.inputStr == ""

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
				self.actualDigits[i] = digits[self.k]
				self.k -= 1

            # put value on display
			i = 0
			for dig in self.actualDigits:
				charCode = self.numbers[self.display[i]]
				j = 0

				for val in charCode:
					GPIO.output( segments[j], val )
					j += 1

				GPIO.output(dig, True)
				time.sleep(0.0005)
				GPIO.output(dig, False)

				i += 1
