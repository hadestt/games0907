# -*- coding: UTF-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log 
from twisted.enterprise import adbapi
import datetime
import time  
import MySQLdb  
import MySQLdb.cursors
from games.items import GamesItem
import socket
import select
import sys
import os
import errno

class DuplicatesPipeline(object):
	def __init__(self):
		self.ids_seen = set()

	def process_item(self, item, spider):
		if item['link'] in self.ids_seen:
			raise DropItem("Duplicate item found: %s" % item)
		else:
			self.ids_seen.add(item['link'])
			return item


class GamesPipeline(object):
	def __init__(self):
		self.dbpool = adbapi.ConnectionPool('MySQLdb', db='gamesdb',host='127.0.0.1',port=3306,
                user='testuser', passwd='test123', cursorclass=MySQLdb.cursors.DictCursor,
                charset='utf8', use_unicode=True)
		log.msg("init_database",level='INFO')

	def process_item(self, item, spider):
		# run db query in thread pool
		log.msg("process_item",level='INFO')
		query = self.dbpool.runInteraction(self._conditional_insert, item)
		query.addErrback(self.handle_error)
		
		return item


	def _conditional_insert(self, tx, item):
		# create record if doesn't exist. 
		# all this block run on it's own thread
		log.msg("_conditional_insert",level='INFO')
		tx.execute("select * from appchina2 where link = %s", (item['link'][0], ))
		result = tx.fetchone()
		if result:
			log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
		else:
			sql = "insert into appchina2(name,category,size,downloads,updates,score,liking,icon,description,link) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			tx.execute(sql,(item["name"][0],item["category"][0],item["size"][0],item["downloads"],item["update"],item["score"],item["liking"],item["icon"][0],item["description"][0],item["link"][0]))  #datetime.datetime.now()))
			log.msg("Item stored in db: %s" % item, level=log.DEBUG)

	def handle_error(self, e):
		log.err(e)
