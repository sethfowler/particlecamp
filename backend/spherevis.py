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
	def __init__(self,commConfig,updateRate,sensorName,sensorVariable,linfcn=((0,'d',0),(.5,'d',70),(1,'d',99)),dbTable=None):
		Thread.__init__(self,name=sensorName)
		self.commConfig = commConfig
		self.updateRate=updateRate
		self.sensorName = sensorName 
		self.sensorVariable = sensorVariable
		self.dbTable = dbTable
		self.linfcn = linfcn
		self.curStyle = linfcn[0][1]
		self.running=True

	def connect(self):
		#TODO need to initialize style
		#self.serialP = serial.Serial(**commConfig) 
		pass

	def disconnect(self):
		#self.serialP.close()
		pass

	def sendCommand(self,style,intensity):
		if style == self.curStyle:
			#self.serialP.write(style)
			pass
		else:
			print "Changing style"
			#self.serialP.setDTR(True)
			time.sleep(.25)
			#self.serialP.setDTR(False)
			time.sleep(.25)
			#self.serialP.setDTR(True)
			time.sleep(.5)
			#self.serialP.write(style)
			self.curStyle=style
		#self.serialP.write(str(intensity))
		#self.serialP.write("\r")

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
		while self.running:
			#get current time
			ts = int(time.time())
			rawvalue = 0
			if dbTable != None:
				#get last 10 minutes of entries
				#TODO 10 hours
				#"%d<=time and time<=%d"%(ts,ts+60*10*60)
				rows = dbTable.select(order_by="time").execute().fetchall()
				print self.dbTable.columns
				if rows != None and len(rows) > 1:
					print "row_0:",rows[-1],":"
					rawvalue = float(rows[-1][self.sensorVariable])
				else:
					#shut it off
					print "No entry found. Shutting off."
					self.setDisplayOff()
			else:
				rawvalue = random.random()
			style,scaledvalue=self.getStyleScale(rawvalue)
			print "sensor:%s,variable:%s,rawvalue:%f,style:%s,scaledvalue:%d"%(self.sensorName,self.sensorVariable,rawvalue,style,scaledvalue)
			self.sendCommand(style,scaledvalue)
			time.sleep(self.updateRate)

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
		dbName = cfg.get("global","db")

		for name in spherenames:
			#read settings
			sensorName=cfg.get(name,"instrument")
			sensorVariable=cfg.get(name,"variable")
			#get the interp list
			linfcn=eval(cfg.get(name,"pwlinfcn"))
			port=cfg.get(name,"port")
			baud=cfg.get(name,"baud")
			updateRate=float(cfg.get(name,"rateSec"))
			commConfig = {"port":port,"baud":int(baud),"timeout":int(updateRate)+10}
			dbTable = None
			if dbName == "None":
				pass
			else:
				db=sq.create_engine("sqlite:///%s"%dbName)
				metadata = sq.MetaData(bind=db)
				metadata.reflect(db)
				dbTable = metadata.tables[sensorName]
			spheres.append(KonaSphere(commConfig,updateRate,sensorName,sensorVariable,linfcn,dbTable))

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





