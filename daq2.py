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
print("Done.\n")

exitFlag = 0
hallLedPins = [led_2_pin_number, led_1_pin_number]

segments = [7,21,13,23,15,18,31,32]
digits = [33,29,22,16]

baja_string     = "BAJA"
clear_character = 'C'

speedNumber = 4444

ON = 0
OFF = 1

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

        if hall_input and switchFlag == 0:
            switchFlag = 1
            counter += 1

            print("\nSwitch On.\n")

            hall1 = HallThread(1, "hall1", counter, hall_1_pin_number, 1, 23,11.1,0)
            hall2 = HallThread(2, "hall2", counter, hall_2_pin_number, 2, 23,11.1,1)

            print("hall1")
            hall1Process = Process(target=hall1.run, args=(queue, True))
            hall1Process_active = True

            print("hall2")
            hall2Process = Process(target=hall2.run, args=(queue, False))
            hall2Process_active = True

            hall1Process.daemon = True
            hall2Process.daemon = True

            hall1Process.start()
            hall2Process.start()

            time.sleep(0.5)

        elif not(hall_input) and switchFlag == 1:
            switchFlag = 0
            queue.put(baja_string)
            print("\nSwitch Off.\n")

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
        startDAQ()

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
