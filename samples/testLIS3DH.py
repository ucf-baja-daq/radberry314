#!/usr/bin/python

from .dependencies.LIS3DH import LIS3DH
from time import sleep

def clickcallback(channel):
	# interrupt handler callback
	print ("Interrupt detected")
	click = sensor.getClick()
	print ("Click detected (0x{:2X})".format(click))
	if (click & 0x10): print (" single click")
	if (click & 0x20): print (" double click")


if __name__ == '__main__':
	sensor = LIS3DH(debug=True)
	sensor.setRange(LIS3DH.RANGE_2G)
	sensor.setClick(LIS3DH.CLK_SINGLE,80,mycallback=clickcallback)

	print ("Starting stream")
	while True:

		x = sensor.getX()
		y = sensor.getY()
		z = sensor.getZ()

# raw values
		print ("\rX: {:.6f}\tY: {:.6f}\tZ: {:.6f}".format(x,y,z))
		sleep(0.1)

# click sensor if polling & not using interrupt
		# click = sensor.getClick()
		# if (click & 0x30) :
		# 	print ("Click detected (0x{:2X})".format(click))
		# 	if (click & 0x10): print (" single click")
		# 	if (click & 0x20): print (" double click")
