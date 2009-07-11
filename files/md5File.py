from hashlib import md5

class md5File:
	block_size = 0x10000
	def upd(self,m, data):
		m.update(data)
		return m

	def calculate(self,fname):
		fd = open(fname, "rb")
		contents = iter(lambda: fd.read(self.block_size), "")
		m = reduce(self.upd, contents, md5())
		fd.close()
		return m.hexdigest()

