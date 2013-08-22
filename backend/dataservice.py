from threading import Thread 
from time import asctime,localtime,sleep,time,mktime,strptime
from uuid import uuid4
from sys import stdout
import sqlalchemy as sq
from exceptions import ValueError
import sqlite3
import re
import pandas
#TODO the delimter patterns are odd in that they reject empty comma separated values

def readlineR(ser,delim):
	line = ""
	start = time()
	waiting = True
	while(waiting):
		if ser.inWaiting():
			c = ser.read(1)
			line = line + c
			waiting = not line.endswith(delim)
			start = time()
		else:
			sleep(1.0/ser.baudrate)
			waiting = time()-start < ser.timeout
			if not waiting: line = None
	return line

class SensorReader(Thread):
	"""serPort is a pyserial serial port object
	rowType is a tuple of columnName,type pairs. Implicitly the first entry is "time",int and so avgRow is required to return a type of (int,) + rowType. Valid types are float,int,str,bytes. For strings using a db without arbitrary length strings use bytes.
	rateSec is the data polling rate the maximum rate that will be returned.
	log is a file handle where data will be logged to.
	db is an sqlalchemy database engine connection. See: http://docs.sqlalchemy.org/en/rel_0_5/sqlexpression.html and http://docs.sqlalchemy.org/en/rel_0_8/core/connections.html
	"""
	def __init__(self,commConfig,sensorName,rowType = (),rateSec=60,db=None,log=None):
		Thread.__init__(self)
		self.setName(sensorName)
		self.commConfig = commConfig 
		self.rateSec = rateSec
		self.db = db
		self.sensorName = sensorName
		self.rowType = (("time",int),) + rowType
		self.log = log
		self.end = False

	def run(self):
		while(not self.end):
			if localtime().tm_sec%self.rateSec == 0:
				readings = self.getReadings()
				readingsStr = ["%s"%repr(reading) for reading in readings]
				rows = [self.toRow(reading) for reading in readings]
				#ADD typecheck here and reset if there is a problem
				avgRows = self.avgRows(rows)
				timeStamp = asctime(localtime())
				logEntry = ",".join(
						[timeStamp,self.sensorName,"%s"%repr(avgRows)] + readingsStr) +"\n"
				if self.log:
						  self.log.write(logEntry)
						  self.log.flush()
				if self.db:
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
			self.log.flush()

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
	"""Returns raw readings gather from sensor. Later on will be converted to rows by a call to toRow. Must return a list of readings. This function should be responsible for synchronizing with the sensor. The rate value really just indicates how frequently to call this function and attempt at retriving a value."""
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
	def resetSensor(self):
		return None
		
#might want to make this a threadsafe interrupt driven reader
class SerialSensorReader(SensorReader):
	def __init__(self,commConfig,sensorName,rowType=(),rateSec=60,db=None,log=None):
		SensorReader.__init__(self,commConfig,sensorName,rowType,rateSec,db,log)
		self.eol = "\n"
		self.delimiterPattern = "\\S+"
		self.delimiter = " "
	def initSensor(self):
		from serial import Serial
		self.serialP = Serial(**self.commConfig) 
		self.resetSensor()
	def stopSensor(self):
		self.serialP.close()
	def getReadings(self):
		readings = []
		ts = str((int(time())/self.rateSec)*self.rateSec)
		while self.serialP.inWaiting():
			line = readlineR(self.serialP,self.eol)
			readings.append(self.delimiter.join([ts, line]))
		readings = [x for x in readings if x != None]
		return readings

	def avgRows(self, readings):
		readings = [r for r in readings if r != None and len(r) == len(self.rowType)]
		readingsTyped=[]
		print readings
		for r in readings:
			try:	
				typed =[t(c) for t,c in zip(zip(*self.rowType)[1],r)] 
				readingsTyped.append(typed)
			except ValueError:
				print "Conversion error in line:",repr(r)
		readings = readingsTyped
		if not readings: 
			return None
		else:
			strings = readings[0]
			avg = list(pandas.DataFrame(readings,columns=zip(*self.rowType)[0]).mean())
			output = []
			numCol = 0
			for col in xrange(0,len(strings)):
				if type(strings[col]) == str:
					output.append(strings[col])
				else:
					output.append(avg[numCol])
					numCol = numCol + 1
			return output

	def toRow(self, reading):
		row = re.findall(self.delimiterPattern,reading.strip())
		row = [x.strip() for x in row]
		return row
	def resetSensor(self):
		print "Reseting Sensor:" + self.sensorName
		return readlineR(self.serialP,self.eol)

class MetOneSensorReader(SerialSensorReader):
	def __init__(self,commConfig,sensorName,rowType=(),rateSec=60,db=None,log=None):
		SerialSensorReader.__init__(self,commConfig,sensorName,rowType,rateSec,db,log)
	def toRow(self,reading):
		gets = [0,1,3,5,7,9,11,13,14,15,16]

		row = SerialSensorReader.toRow(self,reading)
		print "toRow:",len(row),":",repr(row)
		if len(row) != 17:
			return None
		row = [row[i] for i in gets]	
		print "aftercut:",len(row),":",row
		return row
	def resetSensor(self):
		SerialSensorReader.resetSensor(self)
		self.serialP.flushInput()
		seenOP = False
		self.serialP.write("OP\r")
		line = readlineR(self.serialP,self.eol)
		while not seenOP:
			print repr(line)
			if line == "OP\r\n":
				seenOP = True
			line = readlineR(self.serialP,self.eol)
		line2 = readlineR(self.serialP,self.eol).split()    #Status
		print repr(line2)
		if len(line2)>2 and line2[1] =='S':
			self.serialP.write("S\r")
		line3 = readlineR(self.serialP,self.eol).split()    #data
		print repr(line3)
		print "End Reset"
		return line




	

#Since time is the primary key, I need a sensor ID to identify each sensor. 
#That can be the sensorname, but in that case the calling program, which will be giving out pointers
#will have to be aware of sensor ids. That makes sense since why should a data management program worry about metadata
#The sensor id can be unique and another table should be the one managing the type and name of the sensor.
#Since I'll likely be reading redundant data I'll need to not update if the primary key, time, is already in the table.
class FileSensorReader(SensorReader):
	def __init__(self):
		pass
	def initSensor(self):
		pass
	def stopSensor(self):
		pass
	def getReadings(self):
		pass
	def toRow(self,reading):
		pass

if __name__ == "__main__":
	try:
		db = sq.create_engine('sqlite:///:memory:', echo=True)
		sr = SensorReader("COM1","Test2",(),1,db,stdout)
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
#todo create metadatatable with sensor id, type, and name.
