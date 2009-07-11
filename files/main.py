rom hashlib import md5
import os

def upd(m, data):
       m.update(data)
       return m

def calculate(fname, block_size):
       fd = open(fname, "rb")
       contents = iter(lambda: fd.read(block_size), "")
       m = reduce(upd, contents, md5())
       fd.close()
       return m.hexdigest()


block_size = 0x10000
filesDir = "files//"
for i in os.listdir(filesDir):
	if not os.path.isdir(os.path.join(filesDir, i)):
		print i , calculate(i, block_size)
