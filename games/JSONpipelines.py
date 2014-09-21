# -*- coding: UTF-8 -*-
import json
import codecs
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
		self.file = codecs.open('AppChina_data.json', mode='wb', encoding='utf-8')

	def process_item(self, item, spider):
		line = json.dumps(dict(item)) + '\n'
		self.file.write(line.decode("unicode_escape"))

		return item
