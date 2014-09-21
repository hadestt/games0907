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
		self.dbpool = adbapi.ConnectionPool('MySQLdb', db='gamesdb',host='127.0.0.1',port=3306,user='testuser', passwd='test123', cursorclass=MySQLdb.cursors.DictCursor,
                charset='utf8', use_unicode=True)
		# try:
			# c_name = datetime.date.today()
			# col_name = "d" + c_name.strftime("%Y%m%d")
			# sql = "ALTER TABLE appchina_down_records ADD " + col_name+ " float"
			# self.dbpool.runOperation(sql)
			# sql2 = "ALTER TABLE appchina_score_records ADD " + col_name+ " float"
			# self.dbpool.runOperation(sql2)
			# sql3 = "ALTER TABLE appchina_like_records ADD " + col_name+ " float"
			# self.dbpool.runOperation(sql3)
			# log.msg("new column %s is successfully established.", level=log.DEBUG)
		# except OperationalError:
			# log.msg("new column %s is already existed.", level=log.DEBUG)

	def process_item(self, item, spider):
		# run db query in thread pool
		log.msg("process_item",level='INFO')
		query = self.dbpool.runInteraction(self._conditional_insert, item)
		query.addErrback(self.handle_error,item)
		
		return item


	def _conditional_insert(self, tx, item):
		# create record if doesn't exist. 
		# all this block run on it's own thread
		c_name = datetime.date.today()
		col_name = "d" + c_name.strftime("%Y%m%d")
		log.msg("_conditional_insert",level='INFO')
		tx.execute("select * from appchina3 where link = %s", (item['link'], ))
		result = tx.fetchall()
		ids = 0  #this item`s unique id
		if result:
			ids = result[0]['id']  #item`s unique id
			re = result[0]['version']
			if str(re) == item['version'] :
				log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
			else:
				sql = "update appchina3 set version=%s, size=%s, downloads=%s, updates=%s, score=%s, liking=%s where link=%s"
				tx.execute(sql,(item['version'], item['size'], item['downloads'],item['update'],item['score'],item['liking'],item['link']))
				log.msg("Item updated in db: %s" % item, level='INFO')
		else:
			ids = -1
			sql = "insert into appchina3(name,category,version,size,downloads,updates,score,liking,icon,description,link) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			tx.execute(sql,(item["name"],item["category"],item["version"],item["size"],item["downloads"],item["update"],item["score"],item["liking"],item["icon"],item["description"],item["link"]))  
			log.msg("Item stored in db: %s" % item, level=log.DEBUG)

		#update the table_down_records
		if ids==-1:
			tx.execute("select * from appchina3 where link = %s",(item["link"]))
			re = tx.fetchone()
			ids = re['id']
		tx.execute("select * from appchina_down_records where id = %s",(ids))
		if tx.fetchall():
			sql = "update appchina_down_records set %s = %s where id = %s" % (col_name, item['downloads'], ids)
			tx.execute(sql)
			log.msg("Item updated in records_db.", level='INFO')
		else:
			_sql = "insert into appchina_down_records(id, %s) values (%s,  %s)" % (col_name, ids, item['downloads'],)
			tx.execute(_sql)

		#update the table_score_records
		tx.execute("select * from appchina_score_records where id = %s",(ids))
		if tx.fetchall():
			sql = "update appchina_score_records set %s = %s where id = %s" % (col_name, item['score'], ids)
			tx.execute(sql)
			log.msg("Item updated in records_db.", level='INFO')
		else:
			_sql = "insert into appchina_score_records(id, %s) values (%s,  %s)" % (col_name, ids, item['score'],)
			tx.execute(_sql)

		#update the table_liking_records
		tx.execute("select * from appchina_like_records where id = %s",(ids))
		if tx.fetchall():
			sql = "update appchina_like_records set %s = %s where id = %s" % (col_name, item['liking'], ids)
			tx.execute(sql)
			log.msg("Item updated in records_db.", level='INFO')
		else:
			_sql = "insert into appchina_like_records(id, %s) values (%s,  %s)" % (col_name, ids, item['liking'],)
			tx.execute(_sql)


	def handle_error(self, e,item):
		log.err(e)
		log.msg("Mistakes!!!!!!!! %s" % item ,level=log.ERROR)
