#!/usr/bin/env python
from ConfigParser import SafeConfigParser
from os import path,mkdir
import time
import sqlalchemy
#In configuration file have sensors and associate log filenames
#Have list of active sensors and directories for reading files.
#After reading a sensor file move it to a backup directory
CFGFILE="./backend.cfg"

logdir="./logs"
session_id="noid"

def gettimestamp():
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
def mklogfile(sensorname):
	return file(path.join(logdir,sensorname+gettimestamp()+".csv"))
def main():
	if path.exists(CFGFILE):
		cfg=SafeConfigParser()
		cfg.read(CFGFILE)
	else:
		print "ConfigFile not found."
		exit()
	logdir = cfg.get("global","logdir")
	makedirs(logdir)
	session_id = cfg.get("global","session_id")
	sensors_present = dict([(name,bool(x)) for name,x in cfg.items("sensors_present")])
	sensors_present.setdefault(False)
	db = sqlalchemy.create_engine("sqlite:///%s"%session_id,echo=True)
	sensors = {}

	curSensor = 'aeth'
	if sensors_present.get(curSensor):
		commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
				'bytesize':7,'parity':'N'}
		logFile = mklogfile(curSensor)
		rowType = ('aeth_date':str,'aeth_time':str,'black_carbon':int,'a':float,'b':float,'c':float,'d':float,'e':float,'f':float,'g':float)
		sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=60,db=None,log=logFile)
		print '%s online'%curSensor
	if sensors_present.get('dustrack'):
		print 'dustrack online'
	curSensor ='neph' 
	if sensors_present.get(curSensor):
		commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout')}
		logFile = mklogfile(curSensor)
		rowType = ('bscat_m_1':float,'calibcoef':float,'preassure_mb':int,'temp_K':int,'RH_percent':int,'relay_status':int)
		sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=cursensor,rowType=rowType,rateSec=60,db=None,log=logFile)
		print '%s online'%curSensor
	if sensors_present.get('metone'):
		print 'metone online'
	if sensors_present.get('ucpc'):
		print 'ucpc online'
	if sensors_present.get('vueiss'):
		print 'vueiss online'

if __name__ == "__main__":
	main()
