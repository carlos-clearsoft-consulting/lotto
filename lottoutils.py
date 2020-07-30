import fdb
import datetime

def getDbCon():
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/database1.fdb',user='sysdba',password='car5710')
	return con
	
def getFieldNames(cur):
	flds = {}
	attb = cur.description 
	for i in range(0,len(attb)):
		b = attb[i]
		fname = b[0]
		flds[fname]=i
	return flds
	
def getMostCommonNumberDrawn(datefrom,dateto,pcon=None):
	if pcon==None:
		con = getDbCon()
	else:
		con = pcon
	cur = con.cursor()
	cur.execute("select * from lotto649 where drawdate>='" + datefrom + "' and drawdate<='" + dateto + "'")
	rs = cur.fetchall()
	flds = getFieldNames(cur)
	print "flds=",str(flds)
	d={}
	for i in range(1,50):
		d[i]=0
	for r in rs:
		for j in range(1,7):
			fn = 'NUM'+str(j)
			num = r[flds[fn]]
			d[num] = d[num]+1
	selected_x=0
	selected_count=0
	for i in range(1,50):
		print i, d[i]
		if d[i]>selected_count:
			selected_count=d[i]
			selected_x = i
	counts = {}
	for x in range(0,selected_count+1):
		dk = d.keys()
		arr=[]
		for num in dk:
			c = d[num]
			if c==x:
				arr.append(num)
		counts[x]=arr
		print "drawn",x,"times nums are:",arr
	print "highest # is",selected_x," drawn",selected_count,"times"
	if pcon==None:
		con.close()
	return {'NUM':selected_x,'COUNT':selected_count,'DRAWNCOUNTS':counts}
	
def getDatesNumberDrawn(num,pcon=None):
	if pcon==None:
		con = getDbCon()
	else:
		con = pcon
	cur = con.cursor()
	sql = "select drawdate from lotto649 where "
	for i in range(1,7):
		sql = sql + "num"+str(i) + "="+str(num)+" or "
	sql = sql.strip()
	sql = sql[0:-2] + " order by drawdate desc"
	cur.execute(sql)
	rs = cur.fetchall()
	arr=[]
	for r in rs:
		arr.append(r[0])
	if pcon==None:
		con.close()
	return arr
	
	
	
