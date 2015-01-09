#coding:utf-8
from orm import *


class User(Model):
	id = FieldInt(primary_key = True,auto_increment = True)
	name = FieldChar(maxsize = 100,null = False)
	age = FieldInt(default = 20)

#User.objects.insert(name = 'olivetree',age = 24)

#User.objects.filter(name = 'gaojian').update(name = 'gao')

results = User.objects.filter(name = 'gao').filter(age = 24)
for r in results:
	print r

