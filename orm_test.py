#coding:utf-8
from orm import *

class User(Model):
	_table_ = 'user'
	id = FieldInt(primary_key = True,auto_increment = True)
	name = FieldChar(maxsize = 100,null = False)
	age = FieldInt(default = 20)

s = User.objects.all()
print s