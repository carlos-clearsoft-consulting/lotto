import sys, os

thispath = str(os.path.abspath(__file__))
thispath = thispath[0:thispath.rindex(os.path.sep)]


filename = sys.argv[1]
number = sys.argv[2]
f = open(thispath + os.path.sep + filename,'r')
s = f.read()
f.close()
s = s.replace("\r","")
sl = s.split("\n")
cnt=0
for sa in sl:
	sa = sa.strip()
	if sa=="":
		continue
	sc = sa.split(",")
	for i in range(4,len(sc)-1):
		c = sc[i]
		if c==number:
			cnt += 1
print cnt
