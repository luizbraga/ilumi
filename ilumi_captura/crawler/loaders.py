# -*- coding: utf-8 -*-

from scrapy.loader import ItemLoader
from crawler.tools import processors
from crawler import items


class DefaultLoader(ItemLoader):
    default_input_processor = processors.remove_tags_processor
    default_output_processor = processors.join_and_strip


class NoticiaLoader(DefaultLoader):
    default_item_class = items.Noticia
    conteudo_in = processors.string_only()
    data_publicacao_in = processors.datetime_only()
