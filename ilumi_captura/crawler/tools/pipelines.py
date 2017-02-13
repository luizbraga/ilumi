# -*- coding: utf-8 -*-

import pymongo
import datetime
from crawler import settings
from scrapy import signals


class BaseMongoPipeline(object):

    collection_name = settings.get('DATABASE_COLLECTION')

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'database'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )
        crawler.signals.connect(
            ext.item_scraped,
            signal=signals.item_scraped)

        return ext

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def item_scraped(self, item, spider):
        data = dict(item)
        data['extraido_em'] = datetime.datetime.now()
        if not data.get('titulo', ''):
            return
        return self.db[self.collection_name].update_one(
            {'titulo': data['titulo']},
            {'$addToSet': {
                'individuo': spider.individuo
            }, '$set': data}, upsert=True)
