#!/usr/bin/env python
from ConfigParser import SafeConfigParser
from os import path,mkdir,makedirs
import time
import sqlalchemy
from sys import stdout
from dataservice import SerialSensorReader
#In configuration file have sensors and associate log filenames
#Have list of active sensors and directories for reading files.
#After reading a sensor file move it to a backup directory
CFGFILE="backend.cfg"

logdir="logs"
session_id="noid"

def gettimestamp():
	return time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime())
def mklogfile(sensorname):
	logpath = path.join(logdir,sensorname+gettimestamp()+".csv")
	return open(logpath,'w+')
def main():
	global logdir
	if path.exists(CFGFILE):
		cfg=SafeConfigParser()
		cfg.read(CFGFILE)
	else:
		print "ConfigFile not found."
		exit()
	logdir = cfg.get("global","logdir")
	if not path.exists(logdir):
		print "Creating: \'%s\'"%logdir
		makedirs(logdir)
	session_id = cfg.get("global","session_id")
	print cfg.items("sensors_present")
	sensors_present = {}
	sensors_present.setdefault(False)
	for name,x in cfg.items("sensors_present"):
		sensors_present[name]=x in ('true','True')
	db = sqlalchemy.create_engine("sqlite:///%s"%session_id,echo=True)
	sensors = {}

	curSensor = 'aeth'
	print sensors_present
	if sensors_present.get(curSensor):
		commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
				'bytesize':7,'parity':'N'}
		logFile = mklogfile(curSensor)
		rowType = (('aeth_date',str),
				('aeth_time',str),
				('black_carbon',int),
				('a',float),
				('b',float),
				('c',float),
				('d',float),
				('e',float),
				('f',float),
				('g',float))
		sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=60,db=None,log=logFile)
		print '%s online'%curSensor
	if sensors_present.get('dustrack'):
		print 'dustrack online'
	curSensor ='neph' 
	if sensors_present.get(curSensor):
		commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout')}
		logFile = mklogfile(curSensor)
		rowType = (('bscat_m_1',float),('calibcoef',float),('preassure_mb',int),('temp_K',int),('RH_percent',int),('relay_status',int))
		sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=5,db=None,log=logFile)
		print '%s online'%curSensor
	if sensors_present.get('metone'):
		print 'metone online'
	if sensors_present.get('ucpc'):
		print 'ucpc online'
	if sensors_present.get('vueiss'):
		print 'vueiss online'

	print sensors
	for name,sensor in sensors.iteritems():
		sensor.startCollection()
	time.sleep(10)

	for name,sensor in sensors.iteritems():
		sensor.stop()

if __name__ == "__main__":
	main()
