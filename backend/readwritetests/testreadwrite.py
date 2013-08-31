import sqlalchemy as sq
import os
from threading import Thread
import time
import random
import sys

#create conection to db 
db = sq.create_engine("sqlite:///%s"%"testdb")

procid = int(sys.argv[1])

#create table
metadata = sq.MetaData(bind=db)
dbTable = sq.Table("testtable",metadata,sq.Column("v1",sq.Integer,primary_key=True),sq.Column("v2",sq.String))
dbTable.create(checkfirst=True)

#using same connection
#start thread reading table

#add row into table
if procid != 0:
	def wing():
		for x in range(1,200):
			rand = random.random()
			dbTable.insert().execute({"v1":x*procid,"v2":str(rand)})
	#start thread writing furiously to table
	tw = Thread()
	tw.run = wing
	tw.start()

def ring():
	for x in range(1,200):
		print type(dbTable.select())
		print len(dbTable.select("v1").execute().fetchall())
tr = Thread()
tr.run = ring
tr.start()
tr.join()

#create a separate connection and do the same
