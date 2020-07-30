import os, sys
import shutil
import datetime
import time
import random
import StringIO
from functools import wraps
from flask import Flask, g, request, make_response, Response, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
import json
import fdb  
#import kinterbasdb
#from kinterbasdb import typeconv_backcompat


sys.path.append('/usr/local/lib/python2.7/site-packages')
thispath = str(os.path.abspath(__file__))
thispath = thispath[0:thispath.rindex("/")]

app = Flask(__name__)

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
	
def makePatternJob(db):
	rid = str(random.random())
	rid = rid.replace("0.","")
	f = open(thispath + '/mostoftenpattern_jobs/'+rid+'.txt','w')
	f.write(db)
	f.close()
	

@app.route('/')
def index():
	f = open(thispath + '/lotto.html','r')
	fs = f.read()
	f.close()
	return Response(fs,mimetype='text/html')
	
def getDbCon():
	#import kinterbasdb	
	#con = kinterbasdb.connect(dsn='localhost:/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	return con
	
@app.route('/getAllLottoNumbers')
def getAllLottoNumbers():
	db = request.args.get('db','lotto649')
	con = getDbCon()
	cur = con.cursor()
	cur.execute("select count(*) from "+db)
	r = cur.fetchone()
	cnt = r[0]
	cur.execute("select * from " + db + " order by drawdate desc")
	rs = cur.fetchallmap()
	arr=[]
	maxn = 6
	if db=='lottomax':
		maxn = 7
	for r in rs:
		ra = [r['id'],cnt,r['DRAWDATE']]
		for i in range(0,maxn):
			s='NUM'+str(i+1)
			ra.append(r[s])
		ra.append(r['USERENTERED'])
		ra.append("    ")
		arr.append(ra)
		cnt=cnt-1
	con.close()
	return Response(json.dumps(arr),mimetype='text/plain')
	
def getNumbersDrawnDates(fromdate=None,todate=None,db="lotto649"):
	con = getDbCon()
	cur = con.cursor()
	sql = "select * from " + db
	if (fromdate!=None):
		sql = sql + " where drawdate>='" + fromdate + "' and drawdate<='" + todate + "'"
	sql = sql + " order by drawdate desc"
	f = open(thispath + '/debug_getnumbersdrawndates.txt','w')
	f.write(sql+"\n")
	f.flush()
	cur.execute(sql)
	f.write('executed\n')
	f.flush()
	numflds = ['NUM1','NUM2','NUM3','NUM4','NUM5','NUM6']
	maxnum=49
	if db=='lottomax':
		numflds.append('NUM7')
		maxnum=50
	f.write(str(numflds)+'\n')
	f.flush()
	timesdrawn = {}
	d={}
	nmax = maxnum+1
	for i in range(1,nmax):
		d[i]=[]
		timesdrawn[i]=0
	rs = cur.fetchallmap()
	f.write('len rs: '+str(len(rs))+'\n')
	f.flush()
	for r in rs:
		f.write(str(r)+'\n')
		f.flush()
		dt = r['DRAWDATE']
		for nf in numflds:
			f.write('nf='+nf+'\n')
			f.flush()
			v = r[nf]
			f.write('v='+str(v)+'\n')
			f.flush()
			d[v].append(dt)
			timesdrawn[v] = timesdrawn[v] + 1
	con.close()
	return {'DATA':d,'TIMESDRAWN':timesdrawn}
	
@app.route('/getNumbersDrawnDates')
def getNumbersDrawnDatesW():
	dbf = request.args.get('db','lotto649')
	fromdt = request.args.get("fromdate","")
	todt = request.args.get("todate","")
	fromdt = fromdt.strip()
	todt = todt.strip()
	if (fromdt==""):
		t = getNumbersDrawnDates(db=dbf)
	else:
		t = getNumbersDrawnDates(fromdt,todt,db=dbf)
	return Response(json.dumps(t),mimetype='text/plain')
			
@app.route('/removeDraw')
def removeDraw():
	db = request.args.get('db','lotto649')
	rid = request.args.get('id','')
	if rid=='':
		return Response('No record specified',mimetype='text/plain')
	try:
		con = getDbCon()
		cur = con.cursor()
	except:
		return Response('Some problem getting connection to database.',mimetype='text/plain')
	sql = 'select * from ' + db + ' where id='+rid
	try:
		cur.execute(sql)
	except:
		return Response('Error, sql: ' + sql,mimetype='text/plain')
	r = cur.fetchonemap()
	dt = r['DRAWDATE']
	try:
		cur.execute('delete from ' + db + ' where id='+rid)
		cur.execute("delete from pattern_pair_" + db + " where drawdate='" + dt + "'")
		cur.execute("delete from pattern_triple_" + db + " where drawdate='" + dt + "'")
		con.commit()
	except:
		return Response('Some problem deleting from database.',mimetype='text/plain')
	con.close()
	return Response('OK',mimetype='text/plain')

 
@app.route('/getPairingSeries')
def getPairingSeries():
	db = request.args.get('db','lotto649')
	pat = request.args.get('pattern','pair') # pair or triple
	pp = request.args.get('prettyprint','0')
	con = con = getDbCon()
	cur = con.cursor()
	tbl = "pattern_"+pat+"_"+db
	cur.execute("SELECT pattern, drawdate from "+tbl+" order by pattern,drawdate")
	rs = cur.fetchallmap()
	dts={}
	for r in rs:
		dts[r['PATTERN']] = r['DRAWDATE']
	cur.execute("select pattern, count(*) as cnt from "+tbl+" group by pattern order by cnt desc")
	rs = cur.fetchallmap()
	arr=[]
	for r in rs:
		aa = [r['PATTERN'],r['CNT'],dts[r['PATTERN']]]
		arr.append(aa)
	con.close()
	if (pp=='0'):
		return Response(json.dumps(arr),mimetype='text/plain')
	else:
		s = ""
		for ar in arr:
			s = s + ar[0] + " " + str(ar[1]) + " " + ar[2] + "\n"
		return Response(s,mimetype='text/plain')

	
@app.route('/addNewDraw')
def addNewDraw():
	db = request.args.get('db','lotto649')
	f = open(thispath + '/debug_addnewdraw.txt','w')
	dt = request.args.get('date','')
	f.write('date='+dt+'\n')
	f.flush()
	arr=[]
	n={}
	maxn=7
	if db=='lottomax':
		maxn=8
	for i in range(1,8):
		s="num"+str(i)
		snum = request.args.get(s,'')
		if snum=='':
			return Response('Found a blank number, invalid.',mimetype='text/plain')
		n[i]=snum
		arr.append(int(snum))
	f.write('arr='+str(arr)+'\n')
	f.flush()
	try:
		con = getDbCon()
	except:
		return Response('Unable to get database connection.',mimetype='text/plain')
	cur = con.cursor()
	cur.execute("select * from " + db + " where drawdate='" + dt + "'")
	rs = cur.fetchallmap()
	if (len(rs)>0):
		con.close()
		return Response('That draw ( '+dt+' )is already in the system.',mimetype='text/plain')
	sql = "insert into " + db + " (drawdate,num1,num2,num3,num4,num5,num6,userentered,tempid) values ('" + dt + "',"
	if db=='lottomax':
		sql = sql.replace("num6,","num6,num7,")
	for i in range(1,maxn):
		sql = sql + str(n[i]) + ","
	rnd = str(random.random())
	rnd = rnd.replace("0.","")
	sql = sql + "1,'" + rnd + "')"
	f.write('sql='+sql+'\n')
	f.flush()
	try:
		cur.execute(sql)
	except:
		return Response('SQL error, sql = ' + sql,mimetype='text/plain')
	try:
		con.commit()
	except:
		return Response('Cannot commit record.',mimetype='text/plain')
	cur.execute("select count(*) from " + db)
	r = cur.fetchone()
	cnt = r[0]
	f.write('cnt='+str(cnt)+'\n')
	f.flush()
	cur.execute("select id from " + db + "  where tempid='" + rnd + "' and drawdate='" + dt + "'")
	r = cur.fetchonemap()
	rid = r['ID']
	f.write('rid='+str(rid)+'\n')
	f.flush()
	t = makePairsAndTriplesArr(arr)
	f.write('makePairsAndTriplesArr returned.\n')
	f.flush()
	d2arr = t['D2']
	d3arr = t['D3']
	lc=0
	for d in d2arr:
		sql = "insert into pattern_pair_" + db + " (pattern,drawdate) values ('" + d + "','" + dt + "')"
		print lc, sql
		f.write(str(lc)+': ' + sql + '\n')
		f.flush()
		lc += 1
		cur.execute(sql)
	for d in d3arr:
		sql = "insert into pattern_triple_" + db + " (pattern,drawdate) values ('" + d + "','" + dt + "')"
		print lc, sql
		f.write(str(lc)+': ' + sql + '\n')
		f.flush()
		lc += 1
		cur.execute(sql)
	con.commit()
	con.close()
	return Response('OK|'+str(rid)+'|'+str(cnt),mimetype='text/plain')
	
@app.route('/authenticateUser')
def authenticateUser():	
	u = request.args.get('u','')
	u = u.strip().upper()
	p = request.args.get('p','')
	p = p.strip().upper()
	f = open(thispath + '/users.cfg','r')
	s = f.read()
	f.close()
	sl = s.split("\n")
	for sa in sl:
		sa = sa.strip().upper()
		if sa=="" or sa[0]=="#":
			continue
		se = sa.split("=")
		su = se[0].strip()
		sp = se[1].strip()
		if su==u and sp==p:
			return  Response('OK',mimetype='text/plain')
	return Response('FAIL',mimetype='text/plain')
	
def getOddsEvens(fromdt="",todt="",db='lotto649'):
	sql = "select * from " + db + " "
	if (fromdt!=""):
		sql = sql + "where drawdate>'" + fromdt + "' and drawdate<'" + todt + "' "
	sql = sql + " order by drawdate desc"
	con = getDbCon()
	cur = con.cursor()
	cur.execute(sql)
	rs = cur.fetchallmap()
	evens={}
	odds={}
	maxn=7
	if db=='lottomax':
		maxn=8
	for r in rs:
		dt = r['DRAWDATE']
		evens[dt]=0
		odds[dt]=0
		for n in range(1,maxn):
			x = r['NUM'+str(n)]
			if (x % 2)==0:
				evens[dt] = evens[dt]+1
			else:
				odds[dt] = odds[dt]+1
	con.close()
	return {'EVENS':evens,'ODDS':odds}

@app.route('/sequentialDrawHotNumbers')
def sequentialDrawHotNumbers():
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
	import sqlite3
	db = request.args.get('db','lotto649')
	lastnums={}
	for i in range(0,49):
		n = str(i+1)
		lastnums[n] = {'FROMDATE':'','TODATE':'','SEQUENCECOUNT':0}
	#con = fdb.connect(host='127.0.0.1',database='/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	con = getDbCon()
	cur = con.cursor()
	cur.execute("select drawdate from "+db+" order by drawdate")
	drawdates=[]
	rs = cur.fetchallmap()
	for r in rs:
		drawdates.append(r['DRAWDATE'])
	cur.execute("select * from "+db+" order by drawdate")
	rs = cur.fetchallmap()
	maxn=6
	if db=='lottomax':
		maxn=7
	for r in rs:
		for i in range(0,maxn):
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
						#print q['MSG']
						Response(json.dumps({'OK':False,'MSG':q['MSG']}),mimetype='text/plain')
				else:
					lastnums[xs]['SEQUENCECOUNT'] = lastnums[xs]['SEQUENCECOUNT'] + 1
					lastnums[xs]['TODATE']=r['DRAWDATE']
			else:
				lastnums[xs]['SEQUENCECOUNT']=1
				lastnums[xs]['FROMDATE']=r['DRAWDATE']
				lastnums[xs]['TODATE']=r['DRAWDATE']
	#print "Done going through records"
	dbf = thispath+"/sqlite_sdhn_"+db+".db"
	existdb = os.path.exists(dbf)
	with sqlite3.connect(dbf) as conn:
		if not (existdb):
			schema = "create table sdhn (hotnum integer,sequencecount integer,fromdrawdate text,todrawdate text);"					
			conn.executescript(schema)			
			#print "creating schema"
		else:
			conn.execute("delete from sdhn")
	for i in range(0,49):
		n = str(i+1)
		t = lastnums[n]
		if t['SEQUENCECOUNT']>1:
			conn.execute("insert into sdhn (hotnum,sequencecount,fromdrawdate,todrawdate) values ("+n+","+str(t['SEQUENCECOUNT'])+",'"+t['FROMDATE']+"','"+t['TODATE']+"')")
	cur = conn.cursor()
	cur.execute("select hotnum,sequencecount,fromdrawdate,todrawdate  from sdhn order by sequencecount desc,todrawdate desc")
	arr=[]
	for row in cur.fetchall():
		hotnum,sequencecount,fromdrawdate,todrawdate = row
		arr.append([hotnum,sequencecount,fromdrawdate,todrawdate])
	conn.close()
	return Response(json.dumps({'OK':True,'DATA':arr}),mimetype='text/plain')
	
@app.route('/getOddsEvens')
def getOddsEvensW():
	def getCounts(sql,cur):
		#f = open(thispath + '/debug_getc.txt','w')
		#f.write(sql+'\n')
		#f.flush()
		cur.execute(sql)
		rows = cur.fetchall()
		cnts = {}
		curnum=rows[0][1]
		cnts[curnum]=[]
		for r in rows:
			#f.write(str(r)+'\n')
			#f.flush()
			if curnum==r[1]:
				arr = cnts[curnum]
				arr.append(r[0])
			else:
				arr = cnts[curnum]
				arr.sort()
				arr.reverse()
				cnts[curnum] = arr
				curnum = r[1]
				cnts[curnum] = [r[0]]
		arr = cnts[curnum]
		arr.sort()
		arr.reverse()
		cnts[curnum]=arr
		return cnts
	import sqlite3
	db = request.args.get('db','lotto649')
	fromdt = request.args.get('fromdt','')
	todt = request.args.get('todt','')
	t = getOddsEvens(fromdt,todt)
	dbf = thispath+"/sqlite_oddeven_" + db + ".db"
	existdb = os.path.exists(dbf)
	with sqlite3.connect(dbf) as conn:
		if not (existdb):
			schema = "create table oddeven (drawdate text,oddcount integer,evencount integer);"					
			conn.executescript(schema)			
		else:
			conn.execute("delete from oddeven")
	evens = t['EVENS']
	odds = t['ODDS']
	kys = evens.keys()
	for dt in kys:
		ec = evens[dt]
		oc = odds[dt]
		conn.execute("insert into oddeven (drawdate,oddcount,evencount) values ('" + dt + "'," + str(oc) + "," + str(ec) + ")")
	cur = conn.cursor()
	odds = getCounts("select drawdate,oddcount from oddeven order by oddcount desc",cur)
	evens = getCounts("select drawdate,evencount from oddeven order by evencount desc",cur)
	x = {'EVENS':evens,'ODDS':odds}
	return Response(json.dumps(x),mimetype='text/plain')
	
if __name__ == "__main__":
    app.run(debug=True)
