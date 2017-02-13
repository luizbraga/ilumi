# -*- coding: utf-8 -*-

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

CONCURRENT_REQUESTS = 32


SPIDER_MODULES = (
    'crawler.spiders.carta_capital',
    # 'crawler.spiders.exame',
    'crawler.spiders.globo',
    'crawler.spiders.uol',
    # 'crawler.spiders.veja',
)

ITEM_PIPELINES = {
    'crawler.pipelines.LinkPipeline': 0,
}

DATABASE_COLLECTION = 'noticias'
