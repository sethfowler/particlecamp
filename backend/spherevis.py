#!/usr/bin/env python
#Start globe service
import sqlalchemy as sq
from threading import Thread
import time
import serial
import numpy
import random
import os
import math
import sys
from ConfigParser import SafeConfigParser
#get last two minutes of data and pick latest

CFGFILE="spherevis.cfg"
class KonaSphere(Thread):
	def __init__(self,commConfig,delaySec,sensorName,sensorVariable,linfcn=((0,'d',0),(.5,'d',70),(1,'d',99)),dbTable=None):
		Thread.__init__(self,name=sensorName)
		self.commConfig = commConfig
		self.delaySec=delaySec
		self.sensorName = sensorName 
		self.sensorVariable = sensorVariable
		self.dbTable = dbTable
		self.linfcn = linfcn
		self.curStyle = linfcn[0][1]
		self.running=True
		self.serialP = None

	def connect(self):
		self.serialP = serial.Serial(**commConfig) 

	def disconnect(self):
		if self.serialP:
			self.serialP.close()
	def reset(self):
		self.serialP.setDTR(True)
		time.sleep(5)
		self.serialP.setDTR(False)

	def sendCommand(self,style,intensity):
		if style == self.curStyle:
			self.serialP.write(style)
		else:
			print "Changing style"
			self.serialP.setDTR(True)
			time.sleep(.25)
			#self.serialP.setDTR(False)
			time.sleep(.25)
			#self.serialP.setDTR(True)
			time.sleep(.5)
			#self.serialP.write(style)
			self.curStyle=style
		self.serialP.write("%02d"%intensity)
		#self.serialP.write("\r\n")

	def printResults(self):
		while self.serialP.inWaiting():
			print self.serialP.readline().strip(),

	def getStyleScale(self,rawvalue):
		rawVals,styles,scaledVals=zip(*self.linfcn)
		scaledval = int(math.floor(numpy.interp(rawvalue,rawVals,scaledVals)+.5))
		style = 'd'
		for rv,st,sv in self.linfcn:
			if rawvalue >= rv:
				style = st
			else:
				break
		return (style,scaledval)

	def setDisplayOff(self):
		self.sendCommand(self.curStyle,0) #assumes that curStyle has 0 as a valid shutoff value

	def run(self):
		self.connect()
		print "Reseting"
		self.reset()
		print "Shutting off display"
		self.setDisplayOff()
		time.sleep(5)
		self.printResults()
		while self.running:
			#sleep until delaySec  seconds after the minute
			nextTime = int(time.time()/60+1)*60+self.delaySec
			sleepTime = nextTime - time.time()
			print "sleeping:",sleepTime
			time.sleep(sleepTime)

			#get values from 10 minutes ago 
			ts = int(time.time())
			rawvalue = 0
			if dbTable != None:
				#rows = dbTable.select("time>=%d"%(ts-60*10),order_by="time").execute().fetchall()
				rows = dbTable.select(order_by="time").execute().fetchall()
				if rows != None and len(rows) > 1:
					print "row_0:",rows[-1],":"
					rawvalue = float(rows[-1][self.sensorVariable])
				else:
					print "No entry found. Shutting off."
					self.setDisplayOff()
			else:
				rawvalue = random.random()
			style,scaledvalue=self.getStyleScale(rawvalue)
			print "sensor:%s,variable:%s,rawvalue:%f,style:%s,scaledvalue:%d"%(self.sensorName,self.sensorVariable,rawvalue,style,scaledvalue)
			self.sendCommand(style,scaledvalue)
			self.printResults()
		self.disconnect()

if __name__ == "__main__":
	spheres = []
	try:
		if os.path.exists(CFGFILE):
			cfg=SafeConfigParser()
			cfg.read(CFGFILE)
		else:
			print "ConfigFile not found."
			exit()

		#get sphere list
		spherenames = sys.argv[1:] #cfg.get("global","spheres").split(",")
		if len(sys.argv) <= 1:
			print "Usage: %s"%(sys.argv[0]), "clustername1 [clustername2 ...]"
			print "Clusters are configured and specified in spherevis.cfg"
			exit()
		dbName = cfg.get("global","db")

		for name in spherenames:
			#read settings
			sensorName=cfg.get(name,"instrument")
			sensorVariable=cfg.get(name,"variable")
			#get the interp list
			linfcn=eval(cfg.get(name,"pwlinfcn"))
			port=cfg.get(name,"port")
			baud=cfg.get(name,"baud")
			delaySec=float(cfg.get(name,"delaySec"))
			commConfig = {"port":port,"baudrate":int(baud),"timeout":int(70)}
			dbTable = None
			if dbName == "None":
				pass
			else:
				db=sq.create_engine("sqlite:///%s"%dbName)
				metadata = sq.MetaData(bind=db)
				metadata.reflect(db)
				dbTable = metadata.tables[sensorName]
			spheres.append(KonaSphere(commConfig,delaySec,sensorName,sensorVariable,linfcn,dbTable))

		for sphere in spheres:
			sphere.start()
		while(True):
			pass
	except KeyboardInterrupt:
		for sphere in spheres:
			sphere.running = False
			sphere.disconnect()
		for sphere in spheres:
			sphere.join()





