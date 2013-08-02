import serial
import time
import psycopg2

"""
The database has 4 columns:
apitime
no
no2
nox

Store data from each read into the database so that we can query it
later.
"""
conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
cur = conn.cursor()
Insert = "INSERT INTO api (apitime,no,no2,nox) VALUES (%s,%s,%s,%s)"

ser = serial.Serial('COM3', 9600, timeout=None);

Compounds = ['NO', 'NO2', 'NOX']
Results = []
while 1:
    ser.write("\x03\n")
    
    for Compound in Compounds:
        ser.write("T {}\n".format(Compound))
        Line = ser.readline()
        LineArray = Line.split()
        LineArray = LineArray[3].split('=')
        Results.append(LineArray[1])
        
        
    print "API:{},{},{},{}".format(time.strftime("%Y-%m-%d %H:%M:%S"),Results[0],Results[1], Results[2])
    cur.execute(Insert, (
        time.strftime("%Y-%m-%d %H:%M:%S"), 
        float(Results[0]), float(Results[1]), 
        float(Results[2]))
        )
    conn.commit()

    Results = []
    time.sleep(1)
