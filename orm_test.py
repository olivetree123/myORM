#coding:utf-8
from orm import *


class User(Model):
	id = FieldInt(primary_key = True,auto_increment = True)
	name = FieldChar(maxsize = 100,null = False)
	age = FieldInt(default = 20)

#User.objects.insert(name = 'olivetree',age = 24)

#User.objects.filter(name = 'gao').update(name = 'gaou')

results = User.objects.filter(name = 'gaou').filter(age = 24)
for r in results:
	print r

