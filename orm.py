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
		self.sql = ''
		self.conn = None
		self.cursor = None

	def __iter__(self):
		conn = self.pool.conn_get()
		cursor = conn.cursor()
		print 'sql : ',self.sql
		cursor.execute(self.sql)
		self.cursor = cursor
		self.conn = conn
		return self

	def next(self):
		result = self.cursor.fetchone()
		if not result:
			self.cursor.close()
			self.pool.conn_close(self.conn)
			raise StopIteration
		return result

	def all(self,**filters):
		conn = self.pool.conn_get()
		cursor = conn.cursor()
		sql = 'select * from %s' % self.table
		print 'sql : ',sql
		results = []
		try:
			cursor.execute(sql)
			results = cursor.fetchall()
		except Exception,e:
			print e
		cursor.close()
		self.pool.conn_close(conn)
		return results

	def filter(self,**filters):
		if not self.sql:
			self.sql = 'select * from '+self.table+' where '
		else:
			self.sql = self.sql+' and '
		for key in filters:
			if isinstance(filters[key],basestring):
				self.sql = self.sql + key+'="'+str(filters[key])+'" and '
			else:
				self.sql = self.sql + key+'='+str(filters[key])+' and '
		self.sql = self.sql[:-4]
		return self

	def limit(self,num = 0):
		if num>0:
			self.sql = self.sql+' limit '+str(num)
		return self

	def insert(self,**filters):
		conn = self.pool.conn_get()
		cursor = conn.cursor()
		keys = '('+','.join(filters.keys())+')'
		values = tuple([filters[key] for key in filters.keys()])
		sql = 'insert into '+self.table+'%s values %s' % (keys,str(values))
		print 'sql : ',sql
		try:
			cursor.execute(sql)
		except Exception,e:
			print e
		conn.commit()
		cursor.close()
		self.pool.conn_close(conn)

	def update(self,**filters):
		sql = ''
		if self.sql:
			sql = 'update '+self.table+' set '
			condition = ' where ' + self.sql.split('where')[1].strip()
			for key in filters:
				sql = sql+key+'="'+filters[key]+'",'
			sql = sql[:-1]+condition
			print 'sql : ',sql
			conn = self.pool.conn_get()
			cursor = conn.cursor()
			cursor.execute(sql)
			conn.commit()
			cursor.close()
			self.pool.conn_close(conn)
		self.finish()

	def finish(self):
		self.sql = ''



class MyModelMetaclass(type):
	def __new__(cls,name,bases,attrs):
		cls._table_ = name.lower()
		cls.objects = Objects(name.lower())
		return type.__new__(cls,name,bases,attrs)


class Model(object):

	__metaclass__ = MyModelMetaclass


