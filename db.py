#coding:utf-8

import time
import Queue
import MySQLdb

#需要写成单例模式
class MySQLConnectionPool(object):

	def __init__(self,host = '127.0.0.1',port = 3306,user = 'root',passwd = 'zhy',db = 'test',size = 3):
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		self.db = db
		self.size = size
		self.mysql_pool = Queue.Queue(maxsize = size)
		for i in range(size):
			conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,port=port)
			self.mysql_pool.put(conn)

	def conn_get(self):
		try:
			conn = self.mysql_pool.get(block = False)
		except Queue.Empty:
			conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db,port=self.port)
		return conn

	def conn_close(self,conn):
		if self.mysql_pool.qsize()<self.size:
			self.mysql_pool.put(conn)
		else:
			conn.close()


