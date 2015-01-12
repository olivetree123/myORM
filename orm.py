#coding:utf-8
import json
import redis
import hashlib
import memcache
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
		self.result = None
		self.i = 0
		#self.mc = memcache.Client(['127.0.0.1:11211'],debug = 1)
		self.redis = redis.Redis(host = 'localhost',port = 6379)



	def __iter__(self):
		if self.sql:
			print 'iter sql : ',self.sql
			conn = self.pool.conn_get()
			cursor = conn.cursor()
			key = self.table
			field = hashlib.md5(self.sql).hexdigest()
			self.result = self.redis.hget(key,field)
			if not self.result:
				print 'no cache'
				cursor.execute(self.sql)
				self.result = cursor.fetchall()
				self.redis.hset(key,field,json.dumps(self.result))
			else:
				self.result = json.loads(self.result)
				print 'yes,there is'

			#self.cursor = cursor
			#self.conn = conn
			cursor.close()
			self.pool.conn_close(conn)
			self.finish(clr_res = 0)
		return self

	def next(self):
		if len(self.result)>self.i:
			self.i = self.i + 1
			return self.result[self.i-1]
		else:
			self.finish()
			raise StopIteration


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
		self.del_cache()
		self.finish()

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
			self.del_cache()
		self.finish()

	def finish(self,clr_res = 1):
		self.i = 0
		self.sql = ''
		if clr_res:
			self.result = None

	def del_cache(self,table = ''):
		table = self.table if not table else table
		keys = self.redis.hkeys(self.table)
		print keys
		for key in keys:
			self.redis.hdel(self.table,key)



class MyModelMetaclass(type):
	def __new__(cls,name,bases,attrs):
		print 'attrs : ',attrs
		cls._table_ = name.lower()
		cls.objects = Objects(name.lower(),attrs)
		return type.__new__(cls,name,bases,attrs)


class Model(object):

	__metaclass__ = MyModelMetaclass


