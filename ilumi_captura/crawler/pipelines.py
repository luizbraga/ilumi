# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from crawler import items
from crawler.tools import pipelines


class BaseCleanMixin(object):

    def clean_data(self, data, spider):
        data.update({
            'fonte': spider.fonte
        })
        return data


class LinkPipeline(BaseCleanMixin, pipelines.BaseMongoPipeline):
    items_allowed = [items.Noticia]
