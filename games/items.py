# -*- coding: UTF-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GamesItem(scrapy.Item):
    # define the fields for your item here like:
	name = scrapy.Field()
	link = scrapy.Field()
	category = scrapy.Field()
	version = scrapy.Field()
	icon = scrapy.Field()
	downloads = scrapy.Field()
	size = scrapy.Field()
	description = scrapy.Field()
	update = scrapy.Field()
	score = scrapy.Field()
	liking = scrapy.Field()
	pass
