# -*- coding: UTF-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import urllib
import datetime
import json
import re
import os
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request 
from scrapy import log
from games.items import GamesItem


class GamesSpider(Spider):
	"""爬取AppChinaSpider"""
	name = "appchina"

	#download_delay = 1 #delay
	allowed_domains = ["appchina.com"]
	start_urls = [
	"http://www.appchina.com/category/40.html" 
    ]

	def parse3(self, response):#details
		sel = Selector(response)
		item = response.meta['item']
		items = []
		content = sel.xpath('//div[@id="app-detail-wrap"]')

		#提取目标数据
		size = content.xpath('div/span[@class="size"]/text()').extract()
		description = sel.xpath('//div[@class="scroll-content"]/text()').extract()
		category = sel.xpath('//div[@class="search-title"]/a[3]/text()').extract()
		loving = sel.xpath('//div[@class="app-download fr"]/p[@class="app-like"]/span/text()').extract()
		versions = sel.xpath('//div[@class="bg-wrap"][1]/input[@id="ver_name"]/@value').extract()

		#转码 
		like = [l.encode('utf-8') for l in loving]
		try:
			tmp = like[0]
		except:
			tmp = like
		tmp2 = tmp.split("\xe4\xba\xba\xe5\x96\x9c\xe6\xac\xa2")[-2]
		item['liking'] = int(tmp2)

		cate = [c.encode('utf-8') for c in category]
		item['category'] = cate[0]
		desc = [d.encode('utf-8') for d in description]
		item['description'] = desc[0].strip()
		sizes = [s.encode('utf-8') for s in size]
		item['size'] = sizes[0]
		version = [v.encode('utf-8') for v in versions]
		item['version'] = version[0]

		items.append(item)
		log.msg("Appending item22...",level='INFO')

		#存储网页
		body_ = response.body
		file_name = item['link'].split("/")[-2]
		directory_name = str(datetime.date.today())
		path="E:/scrapyed_pages/appchina/" + directory_name
		path1 = path + "/" + file_name + ".html"
		isExists=os.path.exists(path)
		if not isExists:
			os.makedirs(path)
		fo = open(path1,"wb")
		fo.write(body_)
		fo.close()

		return items

	def parse2(self, response):#list
		sel = Selector(response)
		sites = sel.xpath('//div[@id="bydown"]/ul/li')
		items = []

		for site in sites:
			item = GamesItem()

			name = site.xpath('div[@class="app_section"]/p[1]/a/text()').extract()
			link = site.xpath('div[@class="app_section"]/p[1]/a/@href').extract()
			icon = site.xpath('div[@class="app_section"]/a[1]/img/@src').extract()
			downloads = site.xpath('div[@class="app_section"]/p[@class="app_info"]/span[1]/text()').extract()
			update = site.xpath('div[@class="app_section"]/p[@class="app_info"]/span[2]/text()').extract()
			score = site.xpath('div[@class="app_section"]//input/@value').extract()

			names = [t.encode('utf-8') for t in name]
			item['name'] = names[0]
			links = [l.encode('utf-8') for l in link]
			item['link'] = links[0]
			icons = [i.encode('utf-8') for i in icon]
			item['icon'] = icons[0]

			#转码
			tmp = score[0]
			item['score'] = float(tmp)
			#
			tmp = downloads[0]
			tmp1 = tmp.partition('\xe4\xb8\x8b\xe8\xbd\xbd\xe9\x87\x8f\xef\xbc\x9a')
			tmp2 = tmp1[2]
			tmp3 = tmp2.partition('\xe6\xac\xa1')
			item['downloads'] = float(tmp3[0])
			#
			tmp = [d.encode('utf-8') for d in update]
			tmp0 = tmp[0]
			tmp1 = tmp0.partition('\xe6\x9b\xb4\xe6\x96\xb0\xef\xbc\x9a')
			item['update'] = tmp1[2]

			items.append(item)
			#记录
			log.msg("Appending item...",level='INFO')

		for item in items:
			link = "http://www.appchina.com" + item['link']
			yield Request(link,meta={'item':item},callback=self.parse3, dont_filter = False)

		urls = sel.xpath('//div[@id="bydown"]//span[@class="next"]/a/@href').extract()
		for url in urls:
			url = "http://www.appchina.com" + url
			yield Request(url,callback=self.parse2)

	def parse(self,response): #divided category
		sel = Selector(response)
		columns = sel.xpath('//div[@class="category_list"]/ul/li')

		for column in columns:
			next_c = column.xpath('@id').extract()
			next = "http://www.appchina.com/category/" + next_c[0] + ".html"
			yield Request(next,callback=self.parse2)