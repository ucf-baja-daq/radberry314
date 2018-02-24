#!/usr/bin/python

from LIS3DH import LIS3DH
import time

sensor = LIS3DH(debug=True)
sensor.setRange(LIS3DH.RANGE_8G)

localtime = time.asctime( time.localtime(time.time()))
localtimeStr = str(localtime).replace(" ", "_")
file_str = "/home/pi/Desktop/data/Acceleration/acc_data_" + str.replace(localtimeStr, ':', '-') + ".csv"

print("writing to {}".format(file_str))

with open(file_str, 'w') as f:
	f.write('Time (s),X (g),Y (g), Z (g)\n')

startTime = time.time()

# open file for writing
f = open(file_str, 'a')

try:
	while True:
		f.write("{},{},{},{}\n".format(time.time() - startTime, sensor.getX(), sensor.getY(), sensor.getZ()))

except KeyboardInterrupt:
	f.close()
