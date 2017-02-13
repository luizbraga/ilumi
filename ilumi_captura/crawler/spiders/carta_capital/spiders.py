# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request

from crawler.spiders.carta_capital.constants import XPATH
from crawler.loaders import NoticiaLoader


class CartaCapitalSpider(CrawlSpider):
    name = 'captura-cartacapital'
    start_urls = ['http://www.cartacapital.com.br/']
    search_url = (
        'http://www.cartacapital.com.br/'
        '@@search?b_start:int={}&SearchableText={}')
    fonte = 'cartacapital'
    handle_httpstatus_list = [429, ]
    itens = 00

    def __init__(self, individuo='', *args, **kwargs):
        super(CartaCapitalSpider, self).__init__(*args, **kwargs)
        self.individuo = individuo

    def parse(self, response):
        self.url_busca = self.search_url.format(self.itens, self.individuo)

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
        if not response.xpath('//div[@id="search-results"]//p//strong'):
            for link in response.xpath(XPATH['lista_urls']):
                # Obter conteudo das noticias
                yield Request(
                    url=link.extract(),
                    method='GET',
                    headers=response.request.headers,
                    callback=self.extrair_noticia)

            paginacao = response.xpath(XPATH['paginacao'])
            if paginacao:
                self.itens += 25
                yield Request(
                    url=self.search_url.format(self.itens, self.individuo),
                    method='GET',
                    headers=response.request.headers,
                    callback=self.obter_links)

    def extrair_noticia(self, response):
        if (response.xpath(XPATH['conteudo']) and
                'examenegocios' not in response.url):
            noticia = NoticiaLoader(selector=response)
            noticia.add_xpath(
                'data_publicacao', '//span[@class="documentPublished"]/text()')
            noticia.add_xpath(
                'autor', '//span[@class="documentAuthor"]//a/text()')
            noticia.add_xpath(
                'titulo', '//h1[@class="documentFirstHeading"]/text()')
            noticia.add_xpath(
                'conteudo', '//div[@id="content-core"]//div//p/text()')
            item = noticia.load_item()
            item['fonte'] = self.fonte
            item['url'] = response.url
            yield item
