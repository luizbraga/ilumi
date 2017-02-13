# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from crawler.loaders import NoticiaLoader
import dateparser
import json


class UolSpider(CrawlSpider):
    name = 'captura-uol'
    start_urls = ['https://busca.uol.com.br/']
    busca_url = 'https://busca.uol.com.br/result.html?term={}&page={}&searchon=uol&type=all'
    api_url = ('https://busca.uol.com.br/'
               'search?client=uol&searchon=uol&type=all&term={}&page={}&quantity=10')
    fonte = 'uol'
    page = 1

    def __init__(self, individuo='', *args, **kwargs):
        super(UolSpider, self).__init__(*args, **kwargs)
        self.individuo = individuo

    def parse(self, response):
        url_busca = self.busca_url.format(
            self.individuo, self.page)
        url_api = self.api_url.format(
            self.individuo, self.page)

        self.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/53.0.2785.143 Safari/537.36'),
            'Referer': url_busca,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'en-US,en;q=0.8,pt;q=0.6',
        }

        yield Request(
            url=url_api,
            method='GET',
            headers=self.headers,
            callback=self.obter_links
        )

    def obter_links(self, response):
        resposta = json.loads(response.body)
        if resposta.get('results', []):
            for item in resposta.get('results', []):
                # Obter conteudo das noticias
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
                    url=item['url'],
                    method='GET',
                    headers=headers,
                    callback=self.extrair_noticia)

            self.page += 1
            yield Request(
                url=self.api_url.format(self.individuo, self.page),
                method='GET',
                headers=self.headers,
                callback=self.obter_links)

    def extrair_noticia(self, response):
        noticia = NoticiaLoader(selector=response)
        if 'folha.uol' in response.url:
            if (response.xpath('//div[@class="content"]//p/text()') and
                    response.xpath('//header/time/@datetime')):
                noticia.add_xpath(
                    'data_publicacao', '//header/time/@datetime')
                noticia.add_xpath(
                    'autor', '//div[@class="author"]//b/text()')
                noticia.add_xpath(
                    'titulo', '//h1[@itemprop="headline"]/text()')
                noticia.add_xpath(
                    'conteudo', '//div[@class="content"]//p')
                item = noticia.load_item()
                item['fonte'] = 'Folha de SP'
                item['url'] = response.url
                yield item
        elif 'noticias.uol' in response.url or 'economia.uol' in response.url:
            if response.xpath('//div[@id="texto"]//p'):

                data = dateparser.parse(
                    response.xpath('//time/@datetime').extract()[0])
                noticia.add_value(
                    'data_publicacao', data.strftime('%d/%m/%Y %H:%M'))
                noticia.add_value(
                    'autor', 'UOL')

                noticia.add_xpath(
                    'conteudo', '//div[@id="texto"]//p')
                noticia.add_xpath(
                    'titulo', '//h1[@class="pg-color10"]/text()')
                item = noticia.load_item()
                item['fonte'] = 'UOL'
                item['url'] = response.url
                yield item
