# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class MongoPipeline(object):
    def open_spider(self):
        self.client = pymongo.MongoClient('localhost', 277017)
        self.database = self.client['Scrapy_Tiki']
    def close_spider(self):
        self.client.close()
    def process_item(self, item, spider):
        collection= self.database[item['category']]
        collection.insert_one(item)
