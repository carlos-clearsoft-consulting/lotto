"""
This program generates the matching pairs and triplets data.
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

sys.path.append('/usr/local/lib/python2.7/site-packages')
thispath = str(os.path.abspath(__file__))
thispath = thispath[0:thispath.rindex("/")]

def doCalc(rs):
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
	
def main():
	f = open(thispath + '/mostoftenpattern.job','w')
	f.write("")
	f.close()
	f = open(thispath + '/mostoftenpattern.txt','w')
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/database1.fdb',user='sysdba',password='car5710')
	cur = con.cursor()
	cur.execute("select * from pattern_pair order by drawdate")
	rs = cur.fetchallmap()
	t1=doCalc(rs)
	showCalc(t1,f)
	cur.execute("select * from pattern_triple order by drawdate")
	rs = cur.fetchallmap()
	t2=doCalc(rs)
	f.write("-----\n")
	f.flush()
	showCalc(t2,f)
	con.close() 
	os.remove(thispath + '/mostoftenpattern.job')
	print "Done"
				
		

if __name__ == '__main__':
	main()	
