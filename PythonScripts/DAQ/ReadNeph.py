import serial
import time
import math
import os
# Initially based on ReadAlicat
# Neph output string: 4.460e-06  5.828e-04 1003 296 99 00
# Column idenity: bscat (m-1), calibrator coef (,-1), pressure (mb), temp (K), RH (%), relay status
DATADIR = os.path.join(os.path.curdir,"Collected")
INSTR = 'Neph'
ser = serial.Serial('COM12', 9600, timeout=None);

if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)
print "Data stored in:\'%s\'"%(os.path.abspath(DATADIR))
OutputName = time.strftime("Neph%Y%m%d_%H%M.csv");
OutputFile = open(os.path.join(DATADIR,OutputName), "w")
OutputFile.write("Instr,Time\n")

toAvg = []       
while 1:
    Line = ser.readline()
    LineArray = Line.split()
    values = (float(LineArray[0]),float(LineArray[1]))
    toAvg.append(values)
    if len(LineArray)<5:
        print "Error an invalid number of lines was sent."
    elif math.floor(time.time())%60 == 0:
        avgVal = (sum(zip(*toAvg)[0])/len(toAvg),sum(zip(*toAvg)[1])/len(toAvg))
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S") 
        toFile = ", ".join([INSTR,timeStr]+LineArray)
        display = ", ".join([INSTR,timeStr]+list(map(str,values)))
        print display
        #print zip(xrange(0,len(Line.split())),Line.split())
        OutputFile.write(toFile + "\n")
        OutputFile.flush()
        toAvg=[]
        time.sleep(1)
ser.close()
OutputFile.close()

#Attempt at modularizing the code, don't worry about this for now
class Neph(object):
    def __init__(self, port):
        #Verify instrument on port
        pass
    def configureNeph(self,frequencyS=60):
        pass
    def readNeph(self):
        pass
    def registerListener(self,handler):
        pass
    def startPolling(self):
        pass
    def stopPolling(self):
        pass

