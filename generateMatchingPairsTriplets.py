"""
This program generates the matching pairs and triplets data.  It should only be run once, when the government draw data is imported for all the lottery types.
A pair is any combination of 2 numbers in one draw and it matches when that same combination exists in another draw.
A pair is unordered, ie: 5-10 is the same as 10-5, but is "keyed" by one of them only. I choose to key by ascending order, so it is keyed by "5-10".
A triplet is the same thing but involves 3 numbers.
It creates two files which contain all possible patterns of pairs and triplets.  These files are matches_2.txt and matches_3.txt.
It also empties the pattern_pair and pattern_triple tables and inserts them with data.
The data in these tables come from examining each record in the lotto649 table and recording the doubles and triples patterns.
"""
import os, sys
import shutil
import datetime
import time
import random
import fdb
#import kinterbasdb
#from kinterbasdb import typeconv_backcompat


sys.path.append('/usr/local/lib/python2.7/site-packages')
thispath = str(os.path.abspath(__file__))
thispath = thispath[0:thispath.rindex("/")]

def writeOut(dat,fn):
	print "writeOut, fn=",fn
	f = open(thispath + '/' + fn,'w')
	kx = dat.keys()
	kx.sort()
	for k in kx:
		r = dat[k]
		cnt = str(r['COUNT'])
		dt = r['DATE']
		f.write(k+":{COUNT:"+cnt+",DATE:"+dt+"},\n")
		f.flush()
		print k,": COUNT:",cnt,", DATE:",dt
	f.close()
	return
	
def writeOutMatches(arr,fn):
	print "writeOutMatches, fn=",fn
	f = open(thispath + '/' + fn,'w')
	for s in arr:
		f.write(s+'\n')
		f.flush()
	f.close()
	
def makePairsAndTriplesArr(arr):
	arr.sort()
	d2=[]
	d3=[]
	oi=0
	while oi<len(arr):
		x = arr[oi]
		oj = oi+1
		while (oj<len(arr)):
			y = arr[oj]
			s = str(x)+"-"+str(y)
			if not (s in d2):
				d2.append(s)
				#print "v2,",s
			oj = oj + 1
		oi = oi + 1
	for s in d2:
		sl = s.split("-")
		for i in range(0,len(arr)):
			tarr = [int(sl[0]),int(sl[1])]
			v = arr[i]
			if not (v in tarr):
				tarr.append(v)
				tarr.sort()
				s3 = str(tarr[0])+"-"+str(tarr[1])+"-"+str(tarr[2]) 
				if not (s3 in d3):
					d3.append(s3)
					#print "v2,",s3
	return {'D2':d2,'D3':d3}
	
def makePairsAndTriples():  # this function was the "prototype" upon which the more generic function makePairsAndTriplesArr() was created.
	d2=[]
	d3=[]
	arr=[]
	for i in range(1,50):
		arr.append(i)
	oi=0
	while oi<49:
		x = arr[oi]
		oj = oi+1
		while (oj<49):
			y = arr[oj]
			s = str(x)+"-"+str(y)
			if not (s in d2):
				d2.append(s)
				print s
			oj=oj+1
		oi=oi+1
	for s in d2:
		sl = s.split("-")
		for i in range(1,50):
			tarr = [int(sl[0]),int(sl[1])]
			if not (i in tarr):
				tarr.append(i)
				tarr.sort()
				s3 = str(tarr[0])+"-"+str(tarr[1])+"-"+str(tarr[2]) 
				if not (s3 in d3):
					d3.append(s3)
					print s3
	return {'D2':d2,'D3':d3} 
	
def main():
	arr=[]
	for i in range(0,49):
		arr.append(i+1)
	t49 = makePairsAndTriplesArr(arr)
	nd2_49 = t49['D2']
	nd3_49 = t49['D3']
	writeOutMatches(nd2_49,'matches_2_49.txt')
	writeOutMatches(nd3_49,'matches_3_49.txt')
	arr.append(50)
	t50 = makePairsAndTriplesArr(arr)
	nd2_50 = t50['D2']
	nd3_50 = t50['D3']
	writeOutMatches(nd2_50,'matches_2_50.txt')
	writeOutMatches(nd3_50,'matches_3_50.txt')
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	#con = kinterbasdb.connect(dsn='localhost:/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	cur = con.cursor()
	dbs = ['lotto649','lottomax','bc49']
	for db in dbs:
		print "doing db=",db
		try:
			cur.execute("delete from pattern_pair_" + db)
		except:
			continue # it is because this table doesn't exist yet, as this program was changed over time to accomodate new lottery types
		cur.execute("delete from pattern_triple_" + db)
		con.commit()
		cur.execute("select * from " + db + " order by drawdate asc")
		rs = cur.fetchallmap()
		lc=0
		for r in rs:
			arr=[]
			cn = 7
			if db=='lottomax':
				cn = 8
			for i in range(1,cn):
				nf = 'NUM'+str(i)
				nv = r[nf]
				arr.append(nv)
			dt = r['DRAWDATE']
			print r['DRAWDATE'],': ',str(arr)
			t = makePairsAndTriplesArr(arr)
			d2arr = t['D2']
			d3arr = t['D3']
			for d in d2arr:
				sql = "insert into pattern_pair_" + db + " (pattern,drawdate) values ('" + d + "','" + dt + "')"
				print lc, sql
				lc += 1
				cur.execute(sql)
			for d in d3arr:
				sql = "insert into pattern_triple_" + db + " (pattern,drawdate) values ('" + d + "','" + dt + "')"
				print lc, sql
				lc += 1
				cur.execute(sql)
			con.commit()
	con.close() 
	print "Done"
				
		

if __name__ == '__main__':
	main()	
