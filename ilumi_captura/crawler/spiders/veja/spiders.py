# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request

from crawler.spiders.veja.constants import XPATH
from crawler.loaders import NoticiaLoader


class VejaSpider(CrawlSpider):
    name = 'captura-veja'
    start_urls = ['http://veja.abril.com.br/']
    search_url = (
        'https://cse.google.com/cse?cx={}'
        '&q={}&alt=json#gsc.page={}')
    handle_httpstatus_list = [400, 403]
    fonte = 'veja'
    pagina = 1

    def __init__(self, individuo='', *args, **kwargs):
        super(VejaSpider, self).__init__(*args, **kwargs)
        self.individuo = individuo

    def parse(self, response):
        self.cx = response.xpath(
            '//form[@id="cse-search-box"]//input[@name="cx"]//@value'
            ).extract()[0]
        self.url_busca = self.search_url.format(
            self.cx, self.individuo, self.pagina)

        headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/53.0.2785.143 Safari/537.36'),
            'Accept': ('text/html,application/xhtml+xml,'
                       'application/xml;q=0.9,image/webp,*/*;q=0.8'),
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,pt;q=0.6',
        }

        yield Request(
            url=self.url_busca,
            method='GET',
            headers=headers,
            callback=self.obter_links
        )

    def obter_links(self, response):
        import ipdb; ipdb.set_trace()
