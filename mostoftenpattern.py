"""
This program creates the counts of pattern matches for both pairs and triples.
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

def doCalc(rs):
	print "doCalc start"
	d={}
	for r in rs:
		s = r['PATTERN']
		if s in d.keys():
			t = d[s]
		else:
			t={'COUNT':0}
		t['COUNT']=t['COUNT']+1
		t['DATE']=r['DRAWDATE']
		d[s] = t
	dk = d.keys()
	print "doCalc end with ",len(dk)," keys"
	return d
	
def showCalc(d,f):
	maxc = 0
	maxdt = ""
	maxk = ""
	maxes={}
	kys = d.keys()
	for k in kys:
		c = d[k]['COUNT']
		dt = d[k]['DATE']
		#print k,"COUNT=",c,"DATE=",dt
		if c>maxc:
			maxc = c
			maxdt = dt
			maxk = k
		if c in maxes.keys():
			arr = maxes[c]
		else:
			arr = []
		arr.append({'PATTERN':k,'DATE':dt})
		maxes[c] = arr
	ckys = maxes.keys()
	ckys.sort()
	ckys.reverse()
	for c in ckys:
		arr = maxes[c]
		for r in arr:
			f.write(str(c)+","+r['PATTERN']+","+r['DATE']+"\n")
			f.flush()
	return
	
def showCalc2(pattern,lottodb,d,f):
	dbf = thispath+"/sqlite_"+pattern+"_"+lottodb+".db"
	print "showCalc2, dbf=",dbf
	existdb = os.path.exists(dbf)
	with sqlite3.connect(dbf) as conn:
		if not (existdb):
			schema = "create table pattern (pat text,count integer,drawdate text);"					
			conn.executescript(schema)			
			print "creating schema"
		else:
			conn.execute("delete from pattern")
	dkeys = d.keys()
	for k in dkeys:
		r = d[k]
		count = r['COUNT']
		ddate = r['DATE']
		conn.execute("insert into pattern (pat,count,drawdate) values ('" + k + "'," + str(count) + ",'" + ddate + "')")
	cur = conn.cursor()
	cur.execute("select pat,count,drawdate from pattern order by count desc, drawdate desc")		
	for row in cur.fetchall():
		pat,count,drawdate = row
		print "fetched ",pat,count,drawdate
		f.write(str(count)+","+pat+","+drawdate+"\n")
		f.flush()	
	conn.close()						
	print "done showCalc2"							
	return
	
def doRun(s):
	print "doRun, s=",s
	f = open(thispath + '/mostoftenpattern_'+s+'.job','w')
	f.write("")
	f.close()
	f = open(thispath + '/mostoftenpattern_'+s+'.txt','w')
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	#con = kinterbasdb.connect(dsn='localhost:/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	cur = con.cursor()
	cur.execute("select * from pattern_pair_" + s)
	rs = cur.fetchallmap()
	t1=doCalc(rs)
	showCalc2("pair",s,t1,f)
	cur.execute("select * from pattern_triple_" + s)
	rs = cur.fetchallmap()
	t2=doCalc(rs)
	f.write("-----\n")
	f.flush()
	showCalc2("triple",s,t2,f)
	f.close()
	con.close() 
	os.remove(thispath + '/mostoftenpattern_'+s+'.job')
	print "Done"
	
def main():
	while True:
		ld = glob.glob(thispath + '/mostoftenpattern_jobs/*.*')
		ld.sort(key=os.path.getmtime)
		if (len(ld)>0):
			f = open(ld[0],'r')
			s = f.read()
			f.close()
			os.remove(ld[0])
			s = s.replace("\r","").replace("\n","").replace(" ","")
			doRun(s)
		time.sleep(0.5)  # keep this a tight loop because a request is made by browser for the resulting pattern match immediately after the server side returns to it, so the browser must see a "job" file to signify it is busy.
	
				
		

if __name__ == '__main__':
	main()	
