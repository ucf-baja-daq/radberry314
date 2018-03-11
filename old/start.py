from subprocess import call
import RPi.GPIO as GPIO
from time import sleep
from shutdownPi import shutdown 
from timeit import default_timer as timer 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # IO 21; sets up a pull up resistor
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)


GPIO.setup(38, GPIO.OUT) #IO 20 led 1
GPIO.setup(36, GPIO.OUT) #IO 16 led 2


GPIO.output(38, GPIO.LOW)
GPIO.output(36, GPIO.LOW)

GPIO.output(38, GPIO.LOW)
GPIO.output(36, GPIO.HIGH)
sleep(0.25)
GPIO.output(38, GPIO.HIGH)
GPIO.output(36, GPIO.LOW)
sleep(0.25)

print("Waiting for Toggle Input")

input_state = GPIO.input(40)
input_state_strainG = GPIO.input(5)

while not(input_state == False and input_state_strainG == False):
	input_state = GPIO.input(40)
	input_state_strainG = GPIO.input(5)
	
	sleep(1)	
	

while True:
	input_state = GPIO.input(40)			# hall sen
	input_state_fire = GPIO.input(3)		# missle switch
	input_state_strainG = GPIO.input(5)		# strain gauge		#on switch too!
	
	
	if input_state_fire == False:		# if missle switch is down
		call("python3 hallSensors_dan_multi.py", shell=True)
	# TODO fix immediate shutdown on boot if the switches are in this position
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
		
	GPIO.output(38, GPIO.LOW)
	GPIO.output(36, GPIO.HIGH)
	sleep(0.25)
	GPIO.output(38, GPIO.HIGH)
	GPIO.output(36, GPIO.LOW)
	sleep(0.24)

#print("Shutting down.. lol jk, but it works")
shutdown()
