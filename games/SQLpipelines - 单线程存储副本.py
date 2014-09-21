# -*- coding: UTF-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
from scrapy.contrib.pipeline.images import ImagesPipeline  
from games.items import GamesItem
import time  
import MySQLdb  
import MySQLdb.cursors
import socket
import select
import sys
import os
import errno

class GamesPipeline(object):
	def __init__(self):
		#db = MySQLdb.connect("127.0.0.1","testuser","test123","gamesdb",charset='utf8' )
		#self = db.cursor()
		#sql="delete from appchina"
		#try:
		#	self.execute(sql)
		#	db.commit()
		#except:
		#	log.msg("faild to empty database appchina")
		#	db.rollback()
		#db.close()
		log.msg("init_database",level='INFO')

	def process_item(self, item, spider):
		db = MySQLdb.connect("127.0.0.1","testuser","test123","gamesdb",charset='utf8' )
		self = db.cursor()
		sql= """insert into appchina(name,category,size,downloads,updates,score,liking,icon,description,link) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" %(item['name'][0],item['category'][0],item['size'][0],item['downloads'],item['update'],item['score'],item['liking'],item['icon'][0],item['description'][0],item['link'][0])
		try:
			self.execute(sql)
			db.commit()
			log.msg("item_insert_to_table",level='INFO')
		except:
			log.msg("faild to insert")
			db.rollback()
		db.close()
		#return item
