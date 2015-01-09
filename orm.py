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
	def __init__(self,primary_key = False,auto_increment = False,null = True,default = None,maxsize = 0):
		self.type = int
		super(FieldInt,self).__init__(primary_key,auto_increment,null,default,maxsize)

class FieldChar(Field):
	def __init__(self,primary_key = False,auto_increment = False,null = True,default = None,maxsize = 0):
		self.type = str
		super(FieldChar,self).__init__(primary_key,auto_increment,null,default,maxsize)


class Objects(object):
	
	def __init__(self,table = '',attrs = None):
		self.pool = MySQLConnectionPool()
		self.table = table
		self.attrs = attrs
		self.sql = ''
		self.conn = None
		self.cursor = None


	def __iter__(self):
		if self.sql:
			conn = self.pool.conn_get()
			cursor = conn.cursor()
			print 'sql : ',self.sql
			cursor.execute(self.sql)
			self.cursor = cursor
			self.conn = conn
		return self

	def next(self):
		if not self.cursor:
			raise StopIteration
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
		if not filters:	return self
		self.sql = 'select * from '+self.table+' where ' if not self.sql else self.sql+' and '
		for key in filters:
			if self.attrs and self.attrs.get(key,False) and isinstance(filters[key],self.attrs[key].type):
				if isinstance(filters[key],basestring):
					self.sql = self.sql + key+'="'+str(filters[key])+'" and '
				else:
					self.sql = self.sql + key+'='+str(filters[key])+' and '
			else:
				self.sql = ''
				print 'type is error'
				break
		if self.sql:
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
		print 'attrs : ',attrs
		cls._table_ = name.lower()
		cls.objects = Objects(name.lower(),attrs)
		return type.__new__(cls,name,bases,attrs)


class Model(object):

	__metaclass__ = MyModelMetaclass


