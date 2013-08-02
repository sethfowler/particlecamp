import serial
import psycopg2
import time

ser = serial.Serial('COM9', 9600, timeout=None)
conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
cur = conn.cursor()

Insert = "INSERT INTO metone (metonetime,metone03,metone05,metone07,metone1,metone2,metone5) VALUES (%s,%s,%s,%s,%s,%s,%s)"

while 1:
    #Check to see if the instrument is logging data.  Command to send
    #is OP\r.  If the instrument is not logging, it will return OP S.
    #If the instrument is running, it will return OP R #.  I believe
    #the # is the number of seconds that the instrument has been running.
    ser.write("OP\r")
    
    line = ser.readline()   #It sends out extra info we don't need so call twice.
    line = ser.readline()   #This is the one we need.
    LineArray = line.split()
    
    #Check to see if the instrument is running
    if LineArray[1] == 'S':
        ser.write("S\r")
        time.sleep(1)
        continue
    
    line = ser.readline()

    LineArray = line.split(',')
    if len(LineArray) != 20:
        continue
        
    print "MetOne:" + line
    cur.execute(Insert, (time.strftime("%Y-%m-%d %H:%M:%S"),
        int(LineArray[2]),
        int(LineArray[4]),
        int(LineArray[6]),
        int(LineArray[8]),
        int(LineArray[10]),
        int(LineArray[12]))
    )
        
    conn.commit()
