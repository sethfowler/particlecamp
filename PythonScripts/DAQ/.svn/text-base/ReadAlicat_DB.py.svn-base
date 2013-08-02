import serial
import time
import psycopg2

conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
cur = conn.cursor()

Insert = "INSERT INTO gas (gastime,gasflow) VALUES (%s,%s)"

ser = serial.Serial('COM7', 19200, timeout=None);

while 1:
    ser.write("A\r")
    time.sleep(1)

        
    Line = ""
    while ser.inWaiting() > 0:
        Line = Line + ser.read()
    
    LineArray = Line.split()
    print "CH4: {},{}LPM".format(time.strftime("%Y-%m-%d %H:%M:%S"), float(LineArray[4]))

    cur.execute(Insert, (time.strftime("%Y-%m-%d %H:%M:%S"), float(LineArray[4])))
    conn.commit()
