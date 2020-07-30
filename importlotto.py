import os, sys
import fdb
#import kinterbasdb
#from kinterbasdb import typeconv_backcompat

def loadConfig(cfgfilename):
	f = open(cfgfilename,'r')
	s = f.read()
	f.close()
	s = s.strip()
	s = s.replace("\r","")
	sl = s.split("\n")
	d={}
	for sa in sl:
		sa = sa.strip()
		if sa=="" or sa[0]=="#":
			continue
		se = sa.split("=")
		k = se[0].strip().upper()
		v = se[1].strip()
		d[k]=v
	return d

def main():
	db = sys.argv[1]
	cfg = loadConfig(db+'.cfg')
	con = fdb.connect(host='127.0.0.1',database='/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	#con = kinterbasdb.connect(dsn='localhost:/opt/firebird/lotto.fdb',user='sysdba',password='car5710')
	cur = con.cursor()
	cur.execute('delete from '+db)
	f = open(db+'.csv','r')
	s = f.read()
	f.close()
	s = s.replace("\r","")
	sl = s.split("\n")
	maxnum=6
	if (db=='lottomax'):
		maxnum=7
	startline = int(cfg['STARTLINE']) - 1
	datecol = int(cfg['DATECOL']) - 1
	numbercolstart = int(cfg['NUMCOLSTART'])-1
	for lno in range(startline,len(sl)):
		sa = sl[lno].strip()
		if sa=="":
			continue
		sc = sa.split(",")
		dt = sc[datecol].strip()
		if dt[0]=='"':
			dt = dt[1:-1]
		d={}
		for i in range(0,maxnum):
			fld = "NUM"+str(i+1)
			pik = sc[numbercolstart+i]
			try:
				pikn = int(pik)
			except:
				print "could not make int from " + pik
				pik=-1
			d[fld] = pik
		sql = "insert into " + db + " (drawdate,"
		dkeys = d.keys()
		dkeys.sort()
		sqlv = "'" + dt + "',"
		for k in dkeys:
			x = d[k]
			sql = sql + k + ","
			sqlv = sqlv + str(x) + ","
		sqlv = sqlv[0:-1]
		sql = sql[0:-1] + ") values (" + sqlv + ")" 
		print sql
		cur.execute(sql)
	con.commit()
	print "Done"
		
if __name__ == '__main__':
	main()	

