import serial
import time
import psycopg2

conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
cur = conn.cursor()
Insert = "INSERT INTO ucpc (cpctime,Record,Mode,Flags,CN,ST,LT,CNT,PM,RP) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

ser = serial.Serial('COM11', 115200, timeout=None);

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
while 1:
    Line = ""
    while ser.inWaiting() > 0:
        Line += ser.read();
    Line = Line.strip();

    if not Line:
        continue

    LineArray = Line.split(",")
    if len(LineArray) < 9:
        continue
    elif LineArray[0] != 'D':
        continue
    
    Count = 0
    for Item in LineArray:
        if Count == 0:
            Count += 1
        
        if is_number(Item):
            Count += 1
            
    if LineArray[0] == 'D' and Count == 9:
        Line = time.strftime("%Y-%m-%d %H:%M:%S") + "," + ",".join(LineArray)
        print "CPC: " + Line
        cur.execute(Insert, (time.strftime("%Y-%m-%d %H:%M:%S"),
            str(LineArray[0]),
            LineArray[1],
            LineArray[2],
            LineArray[3],
            LineArray[4],
            LineArray[5],
            LineArray[6],
            LineArray[7],
            LineArray[8])
            )
    conn.commit()
