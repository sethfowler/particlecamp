import serial
import time
import psycopg2

conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
cur = conn.cursor()
Insert = "INSERT INTO temperature (temperaturetime,ambientt,hoodt,hoodstate) VALUES (%s,%s,%s,%s)"

ser = serial.Serial('COM10', 9600, timeout=None);

while 1:
    Line = ser.readline();
    Line = Line.strip();
    
    LineArray = Line.split(",")
    Line = time.strftime("%Y-%m-%d %H:%M:%S") + "," + ",".join(LineArray)
    print "Temp: " + Line
    cur.execute(Insert, (time.strftime("%Y-%m-%d %H:%M:%S"),
        float(LineArray[0]),
        float(LineArray[1]),
        float(LineArray[2]))
    )
        
    conn.commit()
