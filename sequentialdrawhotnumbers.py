"""
This is a test program to test getting sequentially drawon numbers.
ie: draw 48 in 3 consecutive draws.
"""
import os, sys
import glob
import shutil
import datetime
import time
import random
import fdb
#import kinterbasdb
#from kinterbasdb import typeconv_backcompat
import sqlite3


sys.path.append('/usr/local/lib/python2.7/site-packages')
thispath = str(os.path.abspath(__file__))
thispath = thispath[0:thispath.rindex("/")]
 
def isInSequence(fromdate,todate,drawdates):
	try:
		x = drawdates.index(fromdate)
	except:
		return {'OK':False,'ERROR':True,'MSG':'fromdate ' + fromdate + ' not in drawdates'}
	try:
		y = drawdates.index(todate)
	except:
		return {'OK':False,'ERROR':True,'MSG':'todate ' + todate + ' not in drawdates'}
	if (y-x)==1:
		return {'OK':True}
	return {'OK':False,'ERROR':False}

def main():
	lastnums={}
	for i in range(0,49):
		n = str(i+1)
		lastnums[n] = {'FROMDATE':'','TODATE':'','SEQUENCECOUNT':0}
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	cur = con.cursor()
	cur.execute("select drawdate from lotto649 order by drawdate")
	drawdates=[]
	rs = cur.fetchallmap()
	for r in rs:
		drawdates.append(r['DRAWDATE'])
	cur.execute("select * from lotto649 order by drawdate")
	rs = cur.fetchallmap()
	for r in rs:
		for i in range(0,6):
			n = str(i+1)
			fld = 'NUM'+n
			xs = str(r[fld])
			t = lastnums[xs]
			fd = t['TODATE']
			if fd!="":
				q = isInSequence(fd,r['DRAWDATE'],drawdates)
				if (q['OK']==False):
					if (q['ERROR']==False):
						lastnums[xs]['SEQUENCECOUNT']=1
						lastnums[xs]['FROMDATE']=r['DRAWDATE']
						lastnums[xs]['TODATE']=r['DRAWDATE']
					else:
						print q['MSG']
				else:
					lastnums[xs]['SEQUENCECOUNT'] = lastnums[xs]['SEQUENCECOUNT'] + 1
					lastnums[xs]['TODATE']=r['DRAWDATE']
			else:
				lastnums[xs]['SEQUENCECOUNT']=1
				lastnums[xs]['FROMDATE']=r['DRAWDATE']
				lastnums[xs]['TODATE']=r['DRAWDATE']
	print "Done going through records"
	dbf = thispath+"/sqlite_sdhn_lotto649.db"
	existdb = os.path.exists(dbf)
	with sqlite3.connect(dbf) as conn:
		if not (existdb):
			schema = "create table sdhn (hotnum integer,sequencecount integer,fromdrawdate text,todrawdate text);"					
			conn.executescript(schema)			
			print "creating schema"
		else:
			conn.execute("delete from sdhn")
	for i in range(0,49):
		n = str(i+1)
		t = lastnums[n]
		if t['SEQUENCECOUNT']>1:
			conn.execute("insert into sdhn (hotnum,sequencecount,fromdrawdate,todrawdate) values ("+n+","+str(t['SEQUENCECOUNT'])+",'"+t['FROMDATE']+"','"+t['TODATE']+"')")
	cur = conn.cursor()
	cur.execute("select hotnum,sequencecount,fromdrawdate,todrawdate  from sdhn order by sequencecount desc,todrawdate desc")
	for row in cur.fetchall():
		hotnum,sequencecount,fromdrawdate,todrawdate = row
		print hotnum,":",sequencecount,"  "+fromdrawdate+" - "+todrawdate
	conn.close()
	print "Done"
	

if __name__ == '__main__':
	main()	
