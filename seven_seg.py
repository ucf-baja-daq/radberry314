class SevenSeg():
	def __init__(self, threadID, name, segments, digits):
		#hreading.Thread.__init__(self)
		print("Initializing Seven Segment Display.")
		self.threadID = threadID
		self.name = name
		
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
						 
		self.numKeys = [' ','0','1','2','3','4','5','6','7','8','9','B', 'A', 'J', 'C']
		
		for seg in segments:
			GPIO.setup(seg, GPIO.OUT)
			GPIO.output(seg, False);
			
		for dig in digits:
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
			self.actualDigits[i] = digits[self.k]
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
				self.actualDigits[i] = digits[self.k]
				self.k = self.k - 1

			i = 0
			for dig in self.actualDigits:
					
				onOFF_value = self.numbers[self.display[i]]

				j = 0
				for val in onOFF_value:
					GPIO.output( segments[j], val )
					j = j + 1

				GPIO.output(dig, True)
				time.sleep(0.0005)
				GPIO.output(dig, False)

				i = i + 1