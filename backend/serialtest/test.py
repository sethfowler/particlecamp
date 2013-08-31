import serial
import time
s = serial.Serial(port="COM21",baudrate=9600,timeout=10)

s.setDTR(True)
print "DTRTrue"
time.sleep(5)
s.setDTR(False)
print "DTRFalse"
time.sleep(5)

while s.inWaiting():
	print s.readline()

def send(val,wait=10):
	sending = "d%02d"%val
	print repr(sending)
	s.write(sending)
	print s.readline()
	while s.inWaiting():
		print s.readline()
	time.sleep(wait)
		
while True:
	for x in [0,10,20,30,40,50,60,70,80,90,99]:
		send(x)
s.close()
