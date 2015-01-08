#coding:utf-8
from db import MySQLConnectionPool

class Field(object):
	def __init__(self,primary_key = False,auto_increment = False,null = True,default = None,maxsize = 0):
		self.primary_key = primary_key
		self.auto_increment = auto_increment
		self.null = null
		self.default = default
		self.maxsize = maxsize

class FieldInt(Field):
	pass

class FieldChar(Field):
	pass


class Objects(object):
	
	def __init__(self,table = ''):
		self.pool = MySQLConnectionPool()
		self.table = table
		pass

	def all(self,**filters):
		conn = self.pool.conn_get()
		cursor = conn.cursor()
		sql = 'select * from %s' % self.table
		print 'sql : ',sql
		try:
			cursor.execute(sql)
		except Exception,e:
			print e
		cursor.close()
		self.pool.conn_close(conn)

	def filer(self,**filters):
		conn = self.pool.conn_get()
		cursor = conn.cursor()
		sql = 'select * from '+self.table+' where '
		for key in filters:
			sql = sql + key+'='+filters[key]+' and '
		sql = sql[:-4]
		print 'sql : ',sql
		try:
			cursor.execute(sql)
		except Exception,e:
			print e
		cursor.close()
		self.pool.conn_close(conn)

	def insert(self,**filters):
		conn = self.pool.conn_get()
		cursor = conn.cursor()
		keys = tuple(filters.keys())
		values = tuple([filters[key] for key in keys])
		sql = 'insert into '+self.table+' %s values %s' % (str(keys),str(values))
		print 'sql : ',sql
		try:
			cursor.execute(sql)
		except Exception,e:
			print e
		conn.commit()
		cursor.close()
		self.pool.conn_close(conn)




class Model(object):

	_table_ = ''
	print '_table_ : ',_table_
	objects = Objects(_table_)

	def __init__(self):
		name = self.__class__.__name__
		self.table = name.lower()


	