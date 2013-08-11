from threading import Thread 
from time import asctime,localtime,sleep,time,mktime,strptime
from uuid import uuid4
from sys import stdout
import sqlalchemy as sq
from exceptions import ValueError
import sqlite3
class SensorReader(Thread):
	"""serPort is a pyserial serial port object
	rowType is a tuple of columnName,type pairs. Implicitly the first entry is "time",int and so avgRow is required to return a type of (int,) + rowType. Valid types are float,int,str,bytes. For strings using a db without arbitrary length strings use bytes.
	rateSec is the data polling rate the maximum rate that will be returned.
	log is a file handle where data will be pushed to.
	db is an sqlalchemy database engine connection. See: http://docs.sqlalchemy.org/en/rel_0_5/sqlexpression.html and http://docs.sqlalchemy.org/en/rel_0_8/core/connections.html
	"""
	def __init__(self,commParms,sensorName,rowType = (),rateSec=60,sessionID = None,db=None,log=None):
		Thread.__init__(self)
		self.setName(sensorName)
		self.commParms = commParms 
		self.rateSec = rateSec
		self.db = db
		self.log = log
		self.sensorName = sensorName
		self.end = False
		self.rowType = (("time",int),) + rowType
		if not sessionID:
			self.sessionID = uuid4()
		else:
			self.sessionID = sessionID

	def run(self):
		while(not self.end):
			if localtime().tm_sec%self.rateSec == 0:
				readings = self.getReadings()
				readingsStr = ["\"%s\""%repr(reading) for reading in readings]
				rows = [self.toRow(reading) for reading in readings]
				avgRows = self.avgRows(rows)
				timeStamp = asctime(localtime())
				logEntry = ",".join(
						[str(self.sessionID),timeStamp, "\"%s\""%repr(avgRows)] + readingsStr) +"\n"
				if self.log:
						  self.log.write(logEntry)
				stdout.flush()
				for row in avgRows:
					self.dbTable.insert().values(*zip(row,zip(*self.rowType)[0]))
				wait = self.rateSec - time()%self.rateSec
				sleep(wait)
			sleep(.1)

	"""Initialized the sensor using initSensor and starts the data collection loop."""
	def startCollection(self):
		self.initDB()
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

	def toDBType(self,ty):
		if ty == int:
			return sq.Integer
		if ty == float:
			return sq.Float
		if ty == str:
			return sq.String
		if ty == bytes or ty == bytearray:
			return sq.Binary
		raise ValueError("Does not map to a database type.")
	def initDB(self):
		if not self.db: return
		cols = []
		cols.append(sq.Column('time',self.toDBType(int),primary_key = True))
		print self.rowType
		for name,ty in self.rowType[1:]:
			cols.append(sq.Column(name,self.toDBType(ty)))
		metadata = sq.MetaData(bind=self.db)
		
		self.dbTable = sq.Table(self.sensorName,metadata,*cols)
		self.dbTable.create()

	"""Called by startCollection to initialize the sensor and communcations."""
	def initSensor(self):
		pass
	"""Called by stop after collection has ended."""
	def stopSensor(self):
		pass
	"""Returns raw readings gather from sensor. Later on will be converted to rows by a call to toRow. Must return a list of readings."""
	def getReadings(self):
		return [asctime(localtime())]
	"""Must return a tuple following the type of rowType in __init__"""
	def avgRows(self, rows):
		if len(rows) > 0:
			return [rows[0]]
 		else:
			return None
	"""Takes the raw sensor output and converts it to a row. A collection of these will be sent to avgRows."""
	def toRow(self,reading):
		row = strptime(reading)
		return (int(mktime(row)),)
		
class SerialSensorReader(SensorReader):
	def __init__(self,commParms,sensorName,rowType = (),rateSec=60,sessionID = None,db=None,log=None):
		SensorReader.__init__(self,commParms,sensorName,rowType,rateSec,sessionID,db,log)
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
		db = sq.create_engine('sqlite:///:memory:', echo=True)
		sr = SensorReader("COM1","Test2",(),1,None,db,stdout)
		sr.startCollection()
		sleep(100)
		sr.stop()
	except KeyboardInterrupt:
		print "Exiting"
	sr.stop()

#todo
#add database query
#fix it so that avgRow only deals with one averaged collection of readings per time interval
#getReadings returns all readings with a timestamp for each?
#then we only return the readings for one time interval?
