# -*- coding: utf-8 -*-

from scrapy.loader import processors
from crawler.tools import parsers
from w3lib.html import remove_tags

join_and_strip = processors.Compose(
    processors.Join(),
    unicode.strip)

remove_tags_processor = processors.MapCompose(remove_tags)


def build_url():
    return processors.MapCompose(
        parsers.normalize_url)


def string_only():
    return processors.MapCompose(
        parsers.string_only,
        unicode.strip
    )


def datetime_only():
    return processors.MapCompose(
        remove_tags,
        unicode.strip,
        parsers.datetime_only)
