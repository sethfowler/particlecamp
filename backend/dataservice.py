from threading import Thread 
from time import asctime,localtime,sleep
from uuid import uuid4
import sys
class sensorReader(Thread):
	"""serPort is a pyserial serial port object
	rateSec is the data polling rate the maximum rate that will be returned.
	db is a database object
	log is a file handle where data will be pushed to.
	timestamps will be rounded to the nearest minute."""
	def __init__(self,serPort,sensorName,rateSec=60,sessionID = None,db=None,log=None):
		Thread.__init__(self)
		self.setName(sensorName)

		self.serPort = serPort
		self.rateSec = rateSec
		self.db = db
		self.log = log
		self.dbTable = sensorName
		self.end = False
		if not sessionID:
			self.sessionID = uuid4()
		else:
			self.sessionID = sessionID

	def run(self):
		while(not self.end):
			readings = self.getReadings()
			readingsStr = ["\"%s\""%str(reading) for reading in readings]
			avg = self.avgReadings(readings)
			row = self.toRow(avg)
			timeStamp = asctime(localtime())
			logEntry = ",".join(
					[str(self.sessionID),timeStamp, "\"%s\""%str(row)] + readingsStr) +"\n"
			if self.log:
					  self.log.write(logEntry)
			sleep(self.rateSec)


	def startCollection(self):
		self.end = False
		self.initSensor()
		self.start()
	
	def stop(self):
		self.end = True
		self.join()
		self.stopSensor()
		if self.log:
			self.log.close()
	def initDB(self):
		#create table
		pass


	def initSensor(self):
		pass
	def stopSensor(self):
		pass

	def getReadings(self):
		return []
	def avgReadings(self, readings):
		return None
	def toRow(self,avg):
		return ()


		
if __name__ == "__main__":
	try:
		sr = sensorReader("COM1","Test",10,None,None,sys.stdout)
		sr.startCollection()
		sleep(10)
		sr.stop()
	except KeyboardInterrupt:
		print "Exiting"
	except Exception:
		print "Program Terminated Abnormally"
	sr.stop()
