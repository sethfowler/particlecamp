from threading import Thread 
from time import asctime,localtime,sleep,time
from uuid import uuid4
import csv
import sys
class SensorReader(Thread):
	"""serPort is a pyserial serial port object
	rateSec is the data polling rate the maximum rate that will be returned.
	db is a database object
	log is a file handle where data will be pushed to.
	timestamps will be rounded to the nearest minute."""
	def __init__(self,commParms,sensorName,rowType = (), rateSec=60,sessionID = None,db=None,log=None):
		Thread.__init__(self)
		self.setName(sensorName)
		self.commParms = commParms 
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
			if localtime().tm_sec%self.rateSec == 0:
				readings = self.getReadings()
				readingsStr = ["\"%s\""%str(reading) for reading in readings]
				rows = [self.toRow(reading) for reading in readings]
				avgRow = self.avgRows(rows)
				timeStamp = asctime(localtime())
				logEntry = ",".join(
						[str(self.sessionID),timeStamp, "\"%s\""%str(avgRow)] + readingsStr) +"\n"
				if self.log:
						  self.log.write(logEntry)
				wait = self.rateSec - time()%self.rateSec
				sleep(wait)
			sleep(.1)

	"""Initialized the sensor using initSensor and starts the data collection loop"""
	def startCollection(self):
		self.end = False
		self.initSensor()
		self.start()
	
	""" Closes all handles and synchronizes the collection end"""
	def stop(self):
		self.end = True
		self.join()
		self.stopSensor()
		if self.log:
			self.log.close()

	def initDB(self):
		#create table
		pass

	"""Called by startCollection to initialize the sensor and communcations."""
	def initSensor(self):
		pass
	"""Called by stop after collection has ended."""
	def stopSensor(self):
		pass
	"""Returns raw readings gather from sensor. Later on will be converted to rows by a call to toRow."""
	def getReadings(self):
		return []
	"""Must return a tuple following the type of rowType in __init__"""
	def avgRows(self, rows):
		if len(rows) > 0:
			return rows[0]
 		else:
			return None
	"""Takes the raw sensor output and converts it to a row. A collection of these will be sent to avgRows."""
	def toRow(self,reading):
		return ()
		
class SerialSensorReader(SensorReader):
	def __init__(self,rowType = ()):
		SensorReader.__init__(self)
	def initSensor(self):
		from serial import Serial
		self.serialP = Serial(**self.commParms) 
		self.serialP.flushInput()
	def stopSensor(self):
		self.serialP.close()
	def getReadings(self,eol="\n"):
		readings = []
		while self.serialP.inWaiting():
			readings.append(self.serialP.readline(eol=eol))
		return readings
	def toRow(self, reading):
		pass

if __name__ == "__main__":
	try:
		sr = SensorReader("COM1","Test",(),1,None,None,sys.stdout)
		sr.startCollection()
		sleep(100)
		sr.stop()
	except KeyboardInterrupt:
		print "Exiting"
	sr.stop()

#todo
#add database query
#add tuples to define row
#automate avg function?
