import RPi.GPIO as g
from bajadaq.ShiftIn import ShiftIn
import logging as log

g.setmode(g.BOARD)
g.setwarnings(False)

log.basicConfig(level=log.DEBUG)

s = ShiftIn(37, 35, 33, 1)

s.read()

print("{:b}".format(s.state))
