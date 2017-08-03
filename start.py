import RPi.GPIO as GPIO
from time import sleep
from timeit import default_timer as timer 
from subprocess import call

from shutdown_pi import shutdown
from main import Main

# ------------------------------ #
# ----------- Setup ------------ #
# ------------------------------ #

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# setup toggle switches
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # missle switch
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# hall sen
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# strain gauge		#on switch too!

# setup leds
GPIO.setup(38, GPIO.OUT) #IO 20 led 1
GPIO.setup(36, GPIO.OUT) #IO 16 led 2

# initialize leds to OFF
GPIO.output(38, GPIO.LOW)
GPIO.output(36, GPIO.LOW)

# create Main object - to enter collection standby mode
main = Main()

print("Waiting for Toggle Input")

# check if toggle switches are in the system shutdown position
# and wait for them to get out of it so the system doesn't 
# try to shutdown on boot
input_state = GPIO.input(40)
input_state_strainG = GPIO.input(5)

while not(input_state == False and input_state_strainG == False):
	input_state = GPIO.input(40)
	input_state_strainG = GPIO.input(5)
	
	sleep(1)	
	
# ------------------------------ #
# --------- Main Loop ---------- #
# ------------------------------ #

# enter system standby mode
while True:
	input_state = GPIO.input(40)			# hall sen
	input_state_fire = GPIO.input(3)		# missle switch
	input_state_strainG = GPIO.input(5)		# strain gauge		#on switch too!
	
	# if missle switch is dropped, start collection standby mode (main)
	if input_state_fire == False:		# if missle switch is down
		# call("python3 hallSensors_dan_multi.py", shell=True)
		main.start()
	
	# if all toggles are up, shutdown pi
	elif input_state_fire == True and input_state == True and input_state_strainG == True:		# if missle switch is up
		startTime = timer()																			# and hall sen switch is up
		flag = 0																					# and strain gauge switch is up
																									
		print("Shutting down in 5 seconds. Toggle any switch to cancel.")
		
		while (timer() - startTime < 5.0):
			input_state = GPIO.input(40)
			input_state_fire = GPIO.input(3)
			input_state_strainG = GPIO.input(5)	
			
			if input_state_fire == False or input_state == False or input_state_strainG == False:
				flag = 0
				print("Cancelling shutdown.")
				break
			sleep(0.05)
			flag = 1
			
		if flag == 1:
			break
	
	# blink lights to indicate system standby mode
	GPIO.output(38, GPIO.LOW)
	GPIO.output(36, GPIO.HIGH)
	sleep(0.25)
	GPIO.output(38, GPIO.HIGH)
	GPIO.output(36, GPIO.LOW)
	sleep(0.24)

# when main loop is broken out of, shutdown pi
shutdown()
