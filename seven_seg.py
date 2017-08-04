import RPi.GPIO as GPIO
import time
from timeit import default_timer as timer 

class SevenSeg():
	def __init__(self, segments, digits):
		#hreading.Thread.__init__(self)
		print("Initializing Seven Segment Display.")
		
		self.segments = segments
		self.digits = digits
		
		self.ON = 0
		self.OFF = 1
		
		#					  e    d    dp   c    g    b    f    a
		self.numbers = { ' ':[self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF],
						 '0':[self.ON , self.ON , self.OFF, self.ON , self.OFF, self.ON , self.ON , self.ON ],
						 '1':[self.OFF, self.OFF, self.OFF, self.ON , self.OFF, self.ON , self.OFF, self.OFF],
						 '2':[self.ON , self.ON , self.OFF, self.OFF,  self.ON, self.ON , self.OFF, self.ON ],
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
						 
		self.numKeys = [' ','0','1','2','3','4','5','6','7','8','9','B', 'A', 'J', 'C']
		
		for seg in self.segments:
			GPIO.setup(seg, GPIO.OUT)
			GPIO.output(seg, False);
			
		for dig in self.digits:
			GPIO.setup(dig, GPIO.OUT)
			GPIO.output(dig, False)
			
		self.num = 0
		self.length = 0
		
		self.inputStr = str( int(self.num) )
		
		self.length = len(self.inputStr)
		self.display = [0]*self.length
		self.actualDigits = [0]*self.length
		
		for i in range (0, self.length):
			self.display[i] = self.inputStr[i]
			
		self.k = 3
		for i in range(self.length - 1, -1, -1):
			self.actualDigits[i] = self.digits[self.k]
			self.k = self.k - 1
					
		print("Seven Seg SetUp: Done.\n")	
		
	def run(self, q):
		
		global speedNumber
		
		prevNum = 0
		
		stTime = timer()
		
		while True:
			if not q.empty():
				temp = q.get()
				if temp == "BAJA" or temp == 'C':
					self.num = temp
				elif temp % 2 == 0:
					self.num = temp
				prevNum = self.num
				stTime = timer()
			elif q.empty() and timer()-stTime > 2 and not(self.num == "BAJA") and not(self.num == "C"):
				self.num = 0
				prevNum = self.num
				stTime = timer()

			self.inputStr = str( self.num )

			self.length = len(self.inputStr)
			self.display = [0]*self.length
			self.actualDigits = [0]*self.length

			for i in range (0,self.length):
				self.display[i] = self.inputStr[i]           # putting input Number into display array

			self.k = 3
			for i in range (self.length - 1, -1, -1):
				self.actualDigits[i] = self.digits[self.k]
				self.k = self.k - 1

			i = 0
			for dig in self.actualDigits:
					
				onOFF_value = self.numbers[self.display[i]]

				j = 0
				for val in onOFF_value:
					GPIO.output( self.segments[j], val )
					j = j + 1

				GPIO.output(dig, True)
				time.sleep(0.0005)
				GPIO.output(dig, False)

				i = i + 1
